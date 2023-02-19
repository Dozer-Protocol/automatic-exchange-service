import sys,os, django
sys.path.append("/app/backend")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dozer.settings")
django.setup()
from api.models import Wallet
from time import sleep
from django.conf import settings

def test_multiple_tx():
    repeat=1
    w= Wallet.objects.get(name='Test Wallet')
    print('### Initiating buy action test ###')
    for i in range(1,repeat+1):
        print(f'buy tx number {i}')
        w.sendToken(settings.RECEIVE_ADDRESS,124,"00")
        sleep(1)

    print('### Initiating buyback action test ###')
    for i in range(1,repeat+1):
        print(f'buyback tx number {i}')
        #w.sendToken(settings.RECEIVE_ADDRESS,557,settings.TOKEN_UUID)
        sleep(1)


    


if __name__=='__main__':
    test_multiple_tx()