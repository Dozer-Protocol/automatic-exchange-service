# AES - Automatic Exchange Service
<!-- We are proud to announce our first open-source project for Hathor ecosystem!  -->
<!-- ## What is it!? -->
<!-- Planned to be used as an ICO platform for projects which are willing to sell their tokens with an automatic solution. -->

Simple token exchange machine to run on top of Hathor Network. It was build for the proof of concept of Dozer Protocol before we got into nano contracts testing, and we made it open source now.
It can be used for an ICO platform  or for existing projects to provide liquidity for its investors before nanocontracs and Dozer Swap goes live.

The design is as follow

```mermaid
flowchart TD;
    id2{{headless_wallet}}<-- websocket -->django;
    id1[(Database)]<-->django;
```

Using the notification plugin bundled on headless wallet, a websocket connection between the wallet and the django backend will be responsible for trigger the TX subsequent treatment.

## Pre-requisites

- Docker
- Hathor Wallet
- $TokenX and $HTR

The only thing you will need before deploy the service is a hathor wallet with an amount of the token will be on sale. Besides that, it's interesting to send all the token amount to only one address, which will be used on RECEIVE_ADDRESS parameter.

## How to use

After clone the repo, you will need to configure the parameters of the `docker-compose.template.yml` as follow:

```
db:
    - POSTGRES_DB: db name to be created
    - POSTGRES_USER: db user
    - POSTGRES_PASSWORD: db password

backend:
    - POSTGRES_NAME: the same of above POSTGRES_DB
    - POSTGRES_USER: the same of above POSTGRES_USER
    - POSTGRES_PASSWORD: the same of above POSTGRES_PASSWORD
    - WALLET_PASS_TEST: passphrase to be used on the test wallet
    - WALLET_PASS: passphrase to be used on the main wallet
    - WALLET_ID: id for wallet, integer with maximum 10 digits
    - TOKEN_PRICE: token price in HTR (for example 0.25)
    - TOKEN_BUYBACK_PRICE: token price for the buyback function in HTR (for example 0.20)
    - TOKEN_UUID: uuid of the token will be sold
    - RECEIVE_ADDRESS: address that will be published for people send HTR or token, this address will be scanned for new tx
    - FEES: set true or false for sending a 2% fee for Dozer Team
    - ADMIN_DJANGO_PASSWORD: password for accessing the django admin panel
 wallet:
      - HEADLESS_SEED_DEFAULT: enter your seeds separeted with spaces and without quotes
```

If you want to run at mainnet, comment the wallet service and uncomment the below wallet service, designed for mainnet, remember to change your seeds, if needed.

Rename `docker-compose.template.yml` to `docker-compose.yml` and execute `docker compose build` and `docker compose up` on the root of the repository.

Make sure to stop any Hathor headless wallet running on the underline host.

## How it works?

With all the services running, the platform is ready to get new TX sent to the address informed on `RECEIVE_ADDRESS`. There are two types of TX will be processed by the platform:

### Buy

This is the regular TX: HTR will be sent to the `RECEIVE_ADDRESS` and the amount of token (when referencing **token**, it is the one specified by `TOKEN_UUID`) will be calculated using the `TOKEN_PRICE` parameter.

The main wallet will then verify if there is balance available for the TX and will send the token amount to the same address which sent the first transaction. If there is no available balance in main wallet, the HTR amount received will be sent back to the owner.

### Buyback

There will be someone that whant to send back the token bought, this is also possible using this ICO platorm.

When a TX received in `RECEIVE_ADDRESS` has the `TOKEN_UUID` token as input, a buyback action will be start: the amount of HTR to be sent is calculated using the `TOKEN_BUYBACK_PRICE` parameter.

The same balance check of the Buy action will be made before sending the HTR back.

## TX check

All the received transactions are registered on database. And the fields for each one are:

- creation_time - Register the time that the TX are verified by the websocket plugin, will easy the search for non-complete TX;
- txid_receive - First TX (receiving token or HTR by user) ID, will also help on search for problems;
- txid_send - "Answer" TX ID, to check and comprove the send of HTR or token to user
- htr_amount - self-explanatory
- token_amount - self-explanatory
- buyback - boolean field to show if it is a buyback transaction
- success - boolean field to represent the success of the entire transaction (enough balance)

To access the DB just go to `http://localhost:8080/admin` to access Django Admin page, use `admin` as username and the password set on `ADMIN_DJANGO_PASSWORD` parameter, then click on `Txs` to list all the registered transactions.

Note that is possible to edit the TX fields at this screen, but it will only update the TX status on the database and **NOT** on blockchain.
