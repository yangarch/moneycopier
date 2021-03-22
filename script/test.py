import os
import jwt
import uuid
import hashlib
from urllib.parse import urlencode

import requests
import json


def make_cred(account):
    path = "/Users/yangarch/Project/moneycopier/credential"
    path = path + "/upbit.json"
    with open(path) as json_file:
        credentialFile = json.load(json_file)
    credential = ''
    for i in credentialFile:
        if i['account'] == account:
            credential = i
            break
    return credential


def main():
    account = 'bbang'
    cred = make_cred(account)
    url = 'https://api.upbit.com'


    payload = {
        'access_key': cred['accesskey'],
        'nonce': str(uuid.uuid4()),
    }

    jwt_token = jwt.encode(payload, cred['secretkey'])
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.get(url+ "/v1/accounts",headers=headers)

    print(res.json())


if __name__ == "__main__":
    main()