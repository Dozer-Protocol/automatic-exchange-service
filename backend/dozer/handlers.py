import json
from api.tasks import createTx
from asgiref.sync import sync_to_async
from django.conf import settings


def registerTx(response,sendAddress,buyback):
    createTx(response,sendAddress,buyback)
    return True

async def message_handler(message, websocket):    
    response=json.loads(message)        
    if ('type' in response) and (response['type']=='wallet:new-tx') and response['walletId']==settings.WALLET_ID:
        data=response['data']
        inputs=data['inputs']               
        for input in inputs:
            if (input['token']=='00' and input['decoded']['address']!=settings.RECEIVE_ADDRESS):
                print(f"address {input['decoded']['address']} sent {input['token']}")   
                await sync_to_async(registerTx,thread_sensitive=True)(response,input['decoded']['address'],False)
                break
            if (input['token']==settings.TOKEN_UUID and input['decoded']['address']!=settings.RECEIVE_ADDRESS):
                print(f"address {input['decoded']['address']} sent {input['token']}")   
                await sync_to_async(registerTx,thread_sensitive=True)(response,input['decoded']['address'],True)
                break