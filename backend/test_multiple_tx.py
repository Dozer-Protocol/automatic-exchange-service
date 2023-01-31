import sys,os, django
sys.path.append("/app/backend") #here store is root folder(means parent).
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dozer.settings")
django.setup()
from api.models import Wallet
from time import sleep

def test_multiple_tx():

    w= Wallet.objects.get(name='Test Wallet')
    for i in range(1,3):
        print(f'{i} sent')
        w.sendToken("Wkc1QXWq4RvW1EAPgzPpoZNbLWx3fmL86t",i*25,"00")
        sleep(1)


    


if __name__=='__main__':
    test_multiple_tx()