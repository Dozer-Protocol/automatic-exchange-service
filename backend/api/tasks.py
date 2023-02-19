from background_task import background
from .models import Tx,Wallet
from django.conf import settings
import logging
from math import ceil,floor

logger = logging.getLogger('')

@background(schedule=9)
def createTx(response,sendAddress,buyback):
    try:
        fee_address = "Way3s3SLyaJFwb9MAPco8fpFwBwzAny9J6" if (settings.RECEIVE_ADDRESS[0]=="W") else "H7hwed6NR6fLQN1Sh7P7ddC5BmoDLu9kkh"
        wallet=Wallet.objects.get(name='wallet')
        data=response['data']
        outputs=data['outputs']    
        fees=0.01
        tx=Tx() 
        tx.txid_receive=data['tx_id']
        tx.htr_amount=0
        tx.token_amount=0
        tx.buyback=buyback
        tx.sendAddress=sendAddress
        tx.save()
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
            value_htr=tx.token_amount*float(settings.TOKEN_BUYBACK_PRICE)
            amount_fees=ceil(fees*value_htr)
            tx.htr_amount=floor(value_htr-amount_fees)
            tx.save()
            logger.warning(f"will send {tx.htr_amount/100} HTR")
            if (wallet_htr_balance>tx.htr_amount) and tx.htr_amount>0:
                logger.warning("Wallet has available token")
                if fees>0:
                    resp=wallet.sendTokens(tx.sendAddress, tx.htr_amount,"00", fee_address, amount_fees, "00")
                else:
                    resp=wallet.sendToken(tx.sendAddress, tx.htr_amount,"00")
                tx.txid_send=resp['hash']
                tx.success=True
                tx.save()     
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
            amount_fees=ceil(fees*tx.htr_amount)
            tx.token_amount=floor((tx.htr_amount-amount_fees)/float(settings.TOKEN_PRICE))
            tx.save()
            logger.warning(f"will send {tx.token_amount/100} token")
            if (wallet_token_balance>tx.token_amount) and tx.token_amount>0:
                logger.warning("Wallet has available token")
                if fees>0:
                    resp=wallet.sendTokens(tx.sendAddress,tx.token_amount,settings.TOKEN_UUID,fee_address, amount_fees, "00")
                else:
                    resp=wallet.sendToken(tx.sendAddress,tx.token_amount,settings.TOKEN_UUID)
                tx.success=True
                tx.txid_send=resp['hash']
                tx.save()

            else:
                logger.warning("Wallet has no available tokens, sending HTR back")
                resp=wallet.sendToken(tx.sendAddress,tx.htr_amount,"00") 
                tx.success=False
                tx.txid_send=resp['hash']
                tx.save()
    except:
        pass