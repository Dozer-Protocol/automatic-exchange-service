import sys,os, django
sys.path.append("/app/backend") #here store is root folder(means parent).
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()
from api.models import Wallet
from time import sleep
from django.conf import settings
from django.core import management
from django.db import connections
from django.db.utils import OperationalError
from django.contrib.auth.models import User

def setup():
    connected=False
    while(connected==False):
        print('Waiting for db...')
        db_conn = connections['default']
        try:
            c = db_conn.cursor()
        except OperationalError:
            connected = False
        else:
            connected = True
        sleep(2)

    management.call_command('makemigrations')
    management.call_command('migrate')

    for el in Wallet.objects.all():
        el.delete()
    
    w=Wallet()
    w.wallet_id=settings.WALLET_ID
    w.name='wallet'
    w.passphrase=settings.WALLET_PASS
    w.save()
    w.stopWallet()
    w.startWallet()
    w.setToken(settings.TOKEN_UUID)
    w.refreshWallet()

    w1=Wallet()
    w1.wallet_id='123'
    w1.name='Test Wallet'
    w1.passphrase=settings.WALLET_PASS_TEST
    w1.save()
    w1.stopWallet()
    w1.startWallet()    
    w1.setToken(settings.TOKEN_UUID)
    w1.refreshWallet()

    try:
        User.objects.create_superuser('admin','admin@admin.com',settings.ADMIN_DJANGO_PASSWORD)
    except Exception as exp:
        pass


    os.system('python manage.py runserver 0.0.0.0:8080 & python manage.py process_tasks &')

    
    print('#### All services running! ####')

if __name__=='__main__':
    setup()