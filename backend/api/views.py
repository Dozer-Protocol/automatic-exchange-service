from django.conf import settings
from django.http import JsonResponse
from .models import *

def getStatus(request):
    try:
        wallet=Wallet.objects.get(name='wallet')
        wallet.refreshWallet()
        token_balance=0
        htr_balance=0
        if wallet.ready:                     
            for token in wallet.balance:
                if(token['token']=='00'):
                    htr_balance=token['available']
                if(token['token']==settings.TOKEN_UUID):
                    token_balance=token['available']
            response={
                "online":True,
                "htr_balance": htr_balance,
                "token_balance": token_balance,
                "tx_qty": len(Tx.objects.all()),
                "tx_last_week": len(Tx.objects.filter(creation_time__day__gte=7)),
            }
        else:
            response={
            "online":False
            }
    except:
        response={
            "online":False
        }
    return JsonResponse(response, safe=False)
