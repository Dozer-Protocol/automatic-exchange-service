import json
from types import NoneType
from django.db import models
# from account.models import User
import urllib.parse
import requests
from django.conf import settings
from time import sleep


class Wallet(models.Model):
    name=models.CharField(max_length=30,null=True)
    wallet_id=models.CharField(max_length=20,default='123')
    address=models.CharField(max_length=50,default="Wff9MYF9wwomVHtfJRSeAQbmA8MVUgu2jb")
    balance=models.JSONField(null=True)
    ready=models.BooleanField(default=False)
    seedKey=models.CharField(max_length=50,default="default")
    passphrase=models.CharField(max_length=100,default=settings.WALLET_PASS)    
    
    def startWallet(self):    
        url = urllib.parse.urljoin('http://wallet:8000', '/start')        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            'wallet-id': self.wallet_id,
            'seedKey': self.seedKey,
            'passphrase': self.passphrase
        }
        try:            
            response = requests.post(url, headers=headers,data=data)
        except:
            print('Start wallet failed')
            print(response.json())
        if response.json()['success']:
            print(f'Wallet with id {self.wallet_id} started.')
            self.refreshWallet()                        
            self.save()
        else:
            print('Start wallet failed')
            print(response.json()['message'])
            self.ready=False
            self.save()
        return self

    def stopWallet(self):    
        url = urllib.parse.urljoin('http://wallet:8000', '/wallet/stop')        
        headers = {
            "X-Wallet-Id": self.wallet_id
        }        
        print(f'Deleting wallet with ID {self.wallet_id}')
        try:
            response = requests.post(url, headers=headers)            
        except:
            print('Stop wallet failed')
            print(response.json())
        if response.json()['success']:
            self.delete()
            print(f'Wallet with id {self.wallet_id} deleted.')
            
        else:
            print('Stop wallet failed')
            print(response.json()['message'])    
            if response.json()['message']=="Invalid wallet id parameter":
                print('Wallet does not exist, deleting from db')
                self.delete()

    def getAddress(self):    
        url = urllib.parse.urljoin('http://wallet:8000', '/wallet/addresses')
        headers = {
            "X-Wallet-Id": self.wallet_id
        }
        try:
            response = requests.get(url, headers=headers)    
        except:
            print('Failed to get wallet address')
            print(response.json())
        if 'addresses' in response.json():                  
            return response.json()['addresses'][0]
        else:
            print('Failed to get wallet addresses')
            print(response.json()['message'])

    def getReady(self):    
        url = urllib.parse.urljoin('http://wallet:8000', '/wallet/status')
        headers = {
            "X-Wallet-Id": self.wallet_id
        }
        count=0        
        while (1):                      
            try:                        
                response = requests.get(url, headers=headers)                              
                sleep(1)
            except requests.exceptions.RequestException as e:                     
                print(response.json())
                print('Failed to get wallet status')
                raise(e)
                return False
            if count==10:
                print('Failed to get wallet status')
                print(response.json())
                print('Waiting timed out')
                return False
            if ('statusMessage' in response.json() and response.json()['statusMessage']=='Ready'):                
                return True
            count+=1
            

    def getBalance(self):            
        url = urllib.parse.urljoin('http://wallet:8000', '/wallet/balance')
        headers = {
            "X-Wallet-Id": self.wallet_id
        }
        if type(self.balance)==NoneType:
            try:
                request=requests.get(url, headers=headers).json()
            except:
                print('Failed to get wallet balance')
            if 'available' in request:
                response=[
                    {
                    "token":"00",
                    "available":request['available'],
                    "locked":request['locked']
                    }
                ]
                return response
            else:
                print('Failed to get wallet balance')
        else:
            for token in self.balance:            
                params={
                    "token":token['token']
                }
                try:
                    response=requests.get(url,headers=headers,params=params).json()                    
                except:
                    print(f"Failed to get wallet balance of {token} token")                
                if 'available' in response:
                    token['available']=response['available']
                    token['locked']=response['locked']
                else:
                    print(f"Failed to get wallet balance of {token['token']} token")
            return self.balance
    
    def setToken(self,token):
        for t in self.balance:
            if t['token']==token:
                print(f'Token {token} already registered on wallet.')
                return False
        self.balance.append({
            "token":token,
            "available":0,
            "locked":0
        })
        print(f'Token {token} registered on wallet.')
        print('Updating balance...')
        self.getBalance()
        print('Balance updated.')
        self.save()
        return True
    
    def refreshWallet(self):               
        self.ready=self.getReady()        
        self.address=self.getAddress()
        self.balance=self.getBalance()
        self.save()

    def sendToken(self,address,amount=100,token="00"):
        url = urllib.parse.urljoin('http://wallet:8000', '/wallet/simple-send-tx')        
        headers = {
            "Content-Type": "application/json",
            "X-Wallet-Id": self.wallet_id
        }
        data = {
            "address": address,
            "value": amount,
            "token": token,
            "change_address": self.getAddress()
        }
        try:
            response = requests.post(url, headers=headers,data=json.dumps(data))
        except:
            print('Failed to send token.')
            print(response.json())
            raise Exception('Failed to send Token')
        if response.json()['success']:
            print(f'Sent {amount} {token} to {address}.')
            self.refreshWallet()
            return response.json()           
        else:
            print('Failed to send token.')
            print(response.json())
            raise Exception('Failed to send Token')

    
class Tx(models.Model):
    sendAddress=models.CharField(max_length=1000,null=True)
    creation_time=models.TimeField(auto_now_add=True,null=True)
    htr_amount=models.IntegerField()
    token_amount=models.IntegerField()
    buyback=models.BooleanField(default=False)