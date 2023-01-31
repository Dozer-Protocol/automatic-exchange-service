from background_task import background
from .models import Tx,Wallet
from django.conf import settings
import logging

logger = logging.getLogger('')

@background(schedule=30)
def createTx(response,sendAddress):
    logger.warning('entrou na função')
    wallet=Wallet.objects.get(name='wallet')
    data=response['data']
    outputs=data['outputs']    
    tx=Tx() 
    tx.htr_amount=0
    tx.sendAddress=sendAddress
    wallet_balance=0
    for output in outputs:
        if (output['token']=='00') and (output['decoded']['address']=='Wkc1QXWq4RvW1EAPgzPpoZNbLWx3fmL86t'):
                logger.warning(f"mandou {output['value']}")   
                tx.htr_amount+=output['value']              
    wallet.refreshWallet()
    tx.dzr_amount=int(tx.htr_amount/settings.TOKEN_PRICE)
    tx.save()
    for balance in wallet.balance:
        if(balance['token']=='00'):
            logger.warning(f"wallet possui {balance['available']}")
            wallet_balance=balance['available']
            break
    logger.warning(f"vai receber {tx.dzr_amount}")
    if wallet_balance>tx.dzr_amount:
        logger.warning("Carteira tem DZR disponível.")
        wallet.sendToken(tx.sendAddress,tx.dzr_amount,"00b1b246cb512515c5258cb0301afcf83e74eb595dbe655d14e11782db4b70c6")
    else:
        wallet.sendToken(tx.sendAddress,tx.htr_amount,"00")
