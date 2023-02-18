from background_task import background
from .models import Tx,Wallet
from django.conf import settings
import logging
from math import ceil,floor

logger = logging.getLogger('')

@background(schedule=30)
def createTx(response,sendAddress,buyback):
    wallet=Wallet.objects.get(name='wallet')
    data=response['data']
    outputs=data['outputs']    
    if settings.FEES.lower()=='true':
        fees=0.02
    else:
        fees=0
    tx=Tx() 
    tx.txid_receive=data['tx_id']
    tx.htr_amount=0
    tx.token_amount=0
    tx.buyback=buyback
    tx.sendAddress=sendAddress
    wallet_htr_balance=0
    wallet_token_balance=0
    wallet.refreshWallet()
    for balance in wallet.balance:
        if(balance['token']=='00'):
            logger.warning(f"Wallet have {balance['available']} HTR")
            wallet_htr_balance=balance['available']
        if(balance['token']==settings.TOKEN_UUID):
            logger.warning(f"Wallet have {balance['available']} tokens")
            wallet_token_balance=balance['available']    
    if buyback:
        for output in outputs:
            if (output['token']==settings.TOKEN_UUID) and (output['decoded']['address']==settings.RECEIVE_ADDRESS):
                    logger.warning(f"received {float(output['value'])/100} {output['token']}")   
                    tx.token_amount+=output['value']              
        tx.htr_amount=floor(tx.token_amount*(1-fees)*float(settings.TOKEN_BUYBACK_PRICE))
        tx.save()
        logger.warning(f"will send {tx.htr_amount/100} HTR")
        if (wallet_htr_balance>tx.htr_amount) and tx.htr_amount>0:
            logger.warning("Wallet has available token")
            resp=wallet.sendToken(tx.sendAddress,tx.htr_amount,"00")
            tx.txid_send=resp['hash']
            tx.success=True
            tx.save()
            if settings.FEES.lower()=='true':
                logger.warning(f"sending {ceil(fees*tx.token_amount*float(settings.TOKEN_BUYBACK_PRICE))/100} htr as fees")
                # wallet.sendToken("WWKbW1kKWjCcH4m8PFUvteQDDCuDbXX5zk", ceil(fees*tx.token_amount*float(settings.TOKEN_BUYBACK_PRICE)), "00")
        else:
            logger.warning("Wallet has no available HTR, sending token back")
            resp=wallet.sendToken(tx.sendAddress,tx.token_amount,settings.TOKEN_UUID)     
            tx.txid_send=resp['hash']
            tx.success=False
            tx.save()
    else:
        for output in outputs:
            if (output['token']=="00") and (output['decoded']['address']==settings.RECEIVE_ADDRESS):
                    logger.warning(f"received {float(output['value'])/100} {output['token']}")   
                    tx.htr_amount+=output['value']              
        tx.token_amount=floor(tx.htr_amount*(1-fees)/float(settings.TOKEN_PRICE))
        tx.save()
        logger.warning(f"will send {tx.token_amount/100} token")
        if (wallet_token_balance>tx.token_amount) and tx.token_amount>0:
            logger.warning("Wallet has available token")
            resp=wallet.sendToken(tx.sendAddress,tx.token_amount,settings.TOKEN_UUID)
            tx.success=True
            tx.txid_send=resp['hash']
            tx.save()
            if settings.FEES.lower()=='true':
                logger.warning(f"sending {ceil(fees*tx.htr_amount)/100} HTR as fees")
                # wallet.sendToken("WWKbW1kKWjCcH4m8PFUvteQDDCuDbXX5zk", ceil(fees*tx.token_amount), "00")
        else:
            logger.warning("Wallet has no available tokens, sending HTR back")
            resp=wallet.sendToken(tx.sendAddress,tx.htr_amount,"00") 
            tx.success=False
            tx.txid_send=resp['hash']
            tx.save()