import os
import jwt
import uuid
import hashlib
from urllib.parse import urlencode

import requests
import json
import time
import threading


def make_cred(account):
    #path = "/Users/yangarch/Project/moneycopier/credential"
    path = "/home/yansgarch/archcoin/moneycopier/credential"
    path = path + "/upbit.json"
    with open(path) as json_file:
        credentialFile = json.load(json_file)
    credential = ''
    for i in credentialFile:
        if i['account'] == account:
            credential = i
            break
    return credential


def my_bank(cred):
    path = cred['baseurl']
    url = path + "/accounts"

    payload = {
        'access_key': cred['accesskey'],
        'nonce': str(uuid.uuid4()),
    }

    jwt_token = jwt.encode(payload, cred['secretkey'])
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.get(url,headers=headers)
    result = res.json()
    return result


def market_info(cred):
    path = cred['baseurl']
    endpoint = '/market/all'
    url = path + endpoint
    querystring = {"isDetails":"false"}
    response = requests.request("GET", url, params=querystring)
    return response

def sale(cred,coinid,balance):
    url = cred['baseurl'] + '/orders'
    query = {
        'market': 'KRW-'+coinid,
        'side': 'ask',
        'volume': balance,
        'ord_type': 'market',
    }
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': cred['accesskey'],
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': "SHA512",
    }

    jwt_token = jwt.encode(payload, cred['secretkey'])
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.post(url, params=query, headers=headers)
    result = res.json()
    return result

def current_price(cred,coinid):
    url = cred['baseurl'] + '/candles/minutes/1'
    querystring = {"market":"KRW-"+coinid,"count":"1"}
    res = requests.request("GET", url, params=querystring)
    response = res.json()
    price = response[0]['trade_price']
    return price

def my_coin(cred,except_list):
    mybank = my_bank(cred)
    res = {}
    try:
        for i in mybank:
            if i['currency'] not in except_list:
                tmp={}
                tmp['balance'] = 0
                tmp['price'] = 0
                tmp['balance'] = i['balance']
                tmp['price'] = i['avg_buy_price']
                res[i['currency']] = tmp
    except:
        pass
    return res


def calc_profit(price):
    profit_rate = 1.0305
    profit_price = float(price) * profit_rate
    return profit_price


def user_sail(account):
    account = account # trade name
    cred = make_cred(account)
    except_list = cred['except'].split(',')

    hold = my_coin(cred,except_list)
    for i in hold:
        try:
            now_price =current_price(cred, i) #current price
            profit_price = calc_profit(hold[i]['price'])    
            balance = hold[i]['balance']
            if now_price > profit_price:
                res_sale = sale(cred, i, hold[i]['balance'])
                print(res_sale)
            else:
                print(f'{account}: target price is {profit_price}, now {now_price}. balance :{balance}')
        except:
            print('check my bank detail')
            pass


def main():
    
    while(1):
        user_sail('arch')
        user_sail('bbang')
        time.sleep(1)
    
    
if __name__ == "__main__":
    main()