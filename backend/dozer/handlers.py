import json
from api.tasks import createTx
from asgiref.sync import sync_to_async
from django.conf import settings


def registerTx(response,sendAddress):
    print('registrando')
    createTx(response,sendAddress)
    print('registrou')
    return True

async def message_handler(message, websocket):    
    response=json.loads(message)        
    if ('type' in response) and (response['type']=='wallet:new-tx') and response['walletId']==settings.WALLET_ID:
        data=response['data']
        inputs=data['inputs']               
        for input in inputs:
            if (input['token']=='00'):
                print(f"send address {input['decoded']['address']}")   
                await sync_to_async(registerTx,thread_sensitive=True)(response,input['decoded']['address'])
                print('saiu do await')
                break