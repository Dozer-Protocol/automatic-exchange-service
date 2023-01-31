from background_task import background
from .models import Tx,Wallet
from django.conf import settings
import logging

logger = logging.getLogger('')

@background(schedule=30)
def createTx(response,sendAddress):
    wallet=Wallet.objects.get(name='wallet')
    data=response['data']
    outputs=data['outputs']    
    tx=Tx() 
    tx.htr_amount=0
    tx.sendAddress=sendAddress
    wallet_balance=0
    for output in outputs:
        if (output['token']=='00') and (output['decoded']['address']==wallet.address):
                logger.warning(f"sent {output['value']}")   
                tx.htr_amount+=output['value']              
    wallet.refreshWallet()
    tx.token_amount=int(tx.htr_amount/float(settings.TOKEN_PRICE))
    tx.save()
    for balance in wallet.balance:
        if(balance['token']=='00'):
            logger.warning(f"Wallet have {balance['available']}")
            wallet_balance=balance['available']
            break
    logger.warning(f"will receive {tx.token_amount}")
    if (wallet_balance>tx.token_amount) and tx.token_amount>0:
        logger.warning("Wallet has available token")
        wallet.sendToken(tx.sendAddress,tx.token_amount,settings.TOKEN_UUID)
        if(settings.FEES) and (int(tx.htr_amount*2/100)>0):
            wallet.sendToken('Wkc1QXWq4RvW1EAPgzPpoZNbLWx3fmL86t',tx.htr_amount*2/100,"00")
    else:
        logger.warning("Wallet has no available tokens, sending HTR back")
        wallet.sendToken(tx.sendAddress,tx.htr_amount,"00")
