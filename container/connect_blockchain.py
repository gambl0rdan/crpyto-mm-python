import os
from websocket import create_connection

options = {}
options['origin'] = 'https://exchange.blockchain.com'
url = "wss://ws.prod.blockchain.info/mercury-gateway/v1/ws"

def connect_to_api_defaults():

    secret = os.environ.get('API_SECRET', None)

    if not secret:
        with open('./.API_SECRET') as secret_file:
            secret = secret_file.readline()

    return connect_to_api(url, options, secret)

def connect_to_api(url, options, secret):
    api = create_connection(url, **options)
    msg = '{"token": "%s", "action": "subscribe", "channel": "auth"}' % secret
    api.send(msg)
    result =api.recv()
    print(result)
    return api