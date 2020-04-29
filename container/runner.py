import asyncio
import websockets
import json
from pprint import pprint as pp
msg = \
{
  "jsonrpc" : "2.0",
  "id" : 3600,
  "method" : "public/subscribe",
  "params" : {
    "channels" : [
      "deribit_price_index.btc_usd"
    ]
  }
}


msgOrderBook = {
"method":"public/get_order_book",
"params":{
    "instrument_name":"BTC-PERPETUAL",
    "depth":10
},
"jsonrpc":"2.0",
"id":4
}


async def call_api(msg):
   async with websockets.connect('wss://testapp.deribit.com/ws/api/v2') as websocket:
       await websocket.send(msg)
       while websocket.open:
           response = await websocket.recv()
           # do something with the response...
           pp(response)
       pp("Closed")

   pp("Closed")


asyncio.get_event_loop().run_until_complete(call_api(json.dumps(msg)))