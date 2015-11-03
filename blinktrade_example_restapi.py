#!/usr/bin/env python
import hashlib
import hmac
import time
import json
import urllib2
import datetime

# Q. Do you have A Websocket API?
# A. Yes, and we strongly recommend you to use it. Please, check our JavaScript websocket implementation for our WebSocket API here:
# https://github.com/blinktrade/frontend/blob/master/jsdev/bitex/api/bitex.js
#
# Q. Where is the public API for orderbook and ticker data?
# A. https://api.blinktrade.com/api/v1/{CURRENCY_CODE}/ticker
#    https://api.blinktrade.com/api/v1/{CURRENCY_CODE}/orderbook
#    https://api.blinktrade.com/api/v1/{CURRENCY_CODE}/trades
#  Where {CURRENCY_CODE} is:
#      BRL for Brazil Reals - FoxBit
#      VEF for Venezuelan Bolivares - SurBitcoin
#      CLP for Chilean Pesos - SurBitcoin
#      VND for Vietnamise Dongs - VBTC
#      PKR for Pakistani Ruppe - UrduBit
#
#
# Q. What about the Trade API and their respective api endpoints for test and production?
# testnet -> https://api.testnet.blinktrade.com/tapi/v1/message
# prod -> https://api.blinktrade.com/tapi/v1/message

# Q. How to generate an api key ?
# 1. go to your exchange account
#    https://tesnet.blinktrade.com/ for testnet environment
# 2. signup
# 3. Go to API
# 4. Select a name and all the permissions for that API Key.
# 5. Get the API Key and API Secret.  The API Secret will only be shown once.   The API Password is only used in the WebSocket Api

# Q. Can I use the same API in all exchanges powered by Blinktrade?
# A. Yes, same exactly API. You only have to change the BrokerID field
#    *--------------*----*
#    | BrokerID     | ID |
#    *--------------*----*
#    | SurBitcoin   |  1 |
#    | VBTC         |  3 |
#    | FoxBit       |  4 |
#    | Testnet      |  5 |
#    | UrduBit      |  8 |
#    | ChileBit     |  9 |
#    *--------------*----*


# Q. How does the api works ?
# A. Though the blinktrade API, you can
#    - Send and cancel orders
#    - Get a list of your open orders
#    - Get your balance
#    - Generate a Bitcoin deposit address

# Q. Can I generate a withdrawal request?
# A. Not through the web api.  You should use our Websocket API for that.


def send_msg(msg, env='prod'):
    key = 'YOUR_API_KEY_GENERATED_IN_API_MODULE'
    secret = 'YOUR_SECRET_KEY_GENERATED_IN_API_MODULE'

    dt = datetime.datetime.now()
    nonce = str(int((time.mktime( dt.timetuple() )  + dt.microsecond/1000000.0) * 1000000))
    signature = hmac.new( secret,  nonce, digestmod=hashlib.sha256).hexdigest()

    if env == 'prod':
      req = urllib2.Request("https://api.blinktrade.com/tapi/v1/message")
    else:
      req = urllib2.Request("https://api.testnet.blinktrade.com/tapi/v1/message")
    req.add_header('Content-Type', 'application/json')  # You must POST a JSON message
    req.add_header('APIKey', key)  # Your APIKey
    req.add_header('Nonce', nonce) # The nonce must be an integer, always greater than the previous one.
    req.add_header('Signature', signature)  # Use the API Secret  to sign the nonce using HMAC_SHA256 algo

    return urllib2.urlopen(req, json.dumps(msg)).read()


# Request Balance
msg = {
    "MsgType": "U2",    # Balance Request
    "BalanceReqID": 1   # An ID assigned by you. It can be any number.  The response message associated with this request will contain the same ID.
}
print send_msg(msg)
# {
#   "Status": 200,        # 200 for OK, 4xx for errors
#   "Description": "OK",  # Ok if successful, or an error description
#   "Responses": [        # An array of all responses.  Some messages might generated more than one response.
#                   {
#                       "MsgType": "U3",            # Balance response
#                       "5": {                      # 5 stands for your balance with the BrokerID number 5
#                           "BTC": 1985787956019,   # Amount in satoshis of BTC you have deposited into your account
#                           "BTC_locked": 0,        # Amount in satoshis of BTC you have locked ( open orders, margin positions, etc... )
#                           "USD": 41562916193320,  # Amount in satoshis of USD( or your FIAT currency) you have deposited into your account
#                           "USD_locked": 0         # Amount in satoshis of USD( or your FIAT currency) you have locked ( open orders, margin positions, etc... )
#                       },
#                       "ClientID": 90800003,       # Your account ID
#                       "BalanceReqID": 1           # This should match the BalanceReqID sent on the message U2
#                   }
#               ]
# }


# Request Open Orders
msg = {
    "MsgType": "U4",
    "OrdersReqID": 1,
    "Page": 0,
    "PageSize": 100,
    "Filter":["has_leaves_qty eq 1"]  # Set it to "has_leaves_qty eq 1" to get open orders, "has_cum_qty eq 1" to get executed orders, "has_cxl_qty eq 1" to get cancelled orders
}
print send_msg(msg)
#{
#   "Status": 200,
#   "Description": "OK",
#   "Responses": [
#                   {
#                       "MsgType": "U5",        # Order list response
#                       "OrdersReqID": 1,       # Match the request OrdersReqID field.
#                       "Page": 0,              # Starts with 0.
#                       "PageSize": 100,        # The page size. If the length of the array OrdListGrp is greather or equal to the PageSize, you should issue a new request incrementing the Page
#                       "OrdListGrp": [],       # Array of all orders.
#                       "Columns": [            # Description of all columns of the all orders in OrdListGrp
#                                   "ClOrdID",   # client order id. Set by you.
#                                   "OrderID",   # Order id. Set by blinktrade
#                                   "CumQty",    # The executed quantity of this order
#                                   "OrdStatus", # 0=New, 1=Partially filled, 2=Filled, 4=Cancelled, 8=Rejected, A=Pending New
#                                   "LeavesQty", # Quantity open for further execution
#                                   "CxlQty",    # Total quantity canceled for this order.
#                                   "AvgPx",     # Calculated average price of all fills on this order.
#                                   "Symbol",    # BTCUSD, BTCBRL
#                                   "Side",      # 1=Buy, 2=Sell, E=Redem, F=Lend, G=Borrow
#                                   "OrdType",   # 1=Market, 2=Limited, 3=Stop, 4=Stop Limit, G=Swap, P=Pegged
#                                   "OrderQty",  # Quantity ordered in satoshis
#                                   "Price",     # Price per unit in satoshis
#                                   "OrderDate", # Order date in UTC
#                                   "Volume",    # Quantity * Price
#                                   "TimeInForce"# 0=Day, 1=Good Till Cancel, 4=Fill or Kill
#                        ]
#                   }
#               ]
# }



# Send a new order
client_order_id = str(int(time.time()))  # this ID must be uniq
msg = {
    "MsgType":"D",              # New Order Single message. Check for a full doc here: http://www.onixs.biz/fix-dictionary/4.4/msgType_D_68.html
    "ClOrdID": client_order_id, # Unique identifier for Order as assigned by you
    "Symbol":"BTCUSD",          # Can be BTCBRL, BTCPKR, BTCVND, BTCVEF, BTCCLP.
    "Side":"1",                 # 1 - Buy, 2-Sell
    "OrdType":"2",              # 2 - Limited order
    "Price":26381000000,        # Price in satoshis
    "OrderQty":2723810,         # Qty in saothis
    "BrokerID":5                # 1=SurBitcoin, 3=VBTC, 4=FoxBit, 5=Tests , 8=UrduBit, 9=ChileBit
}
print send_msg(msg)
# {
#   "Status": 200,
#   "Description": "OK",
#   "Responses": [  # In this example, the request returned 2 messages.
#                   {
#                       "MsgType": "U3",                    # Balance respose. Problably because the request also change your account balance.
#                       "5": {"USD_locked": 718568316},     # In this example, modified the amount of USD you have locked into your account.
#                       "ClientID": 90800003                # Your account ID
#                   },
#                   {
#                       "MsgType": "8",             # Execution Report. Check for a full fix doc here: http://www.onixs.biz/fix-dictionary/4.4/msgType_8_8.html
#                       "OrderID": 5669865,         # Unique identifier for Order as assigned by broker
#                       "ExecID": 35,               # Unique identifier of execution message as assigned by broker
#                       "ExecType": "0",            # 0=New, 1=Partially fill, 2=Fill, 4=Cancelled, 8=Rejected, A=Pending New
#                       "OrdStatus": "0",           # 0=New, 1=Partially fill, 2=Fill, 4=Cancelled, 8=Rejected, A=Pending New
#                       "LeavesQty": 2723810,       # Quantity open for further execution
#                       "Symbol": "BTCUSD",         # Pair
#                       "OrderQty": 2723810,        # Quantity ordered in satoshis
#                       "LastShares": 0,            # Quantity of shares bought/sold on this fill
#                       "LastPx": 0,                # Price of the last fill
#                       "CxlQty": 0,                # Total quantity canceled for this order.
#                       "TimeInForce": "1",         # 0=Day, 1=Good Till Cancel, 4=Fill or Kill
#                       "CumQty": 0,                # Total quantity filled
#                       "ClOrdID": "1440927610",    # Unique identifier for Order as assigned by you
#                       "OrdType": "2",             # 1=Market, 2=Limited, 3=Stop, 4=Stop Limit, G=Swap, P=Pegged
#                       "Side": "1",                # 1=Buy, 2=Sell, E=Redem, F=Lend, G=Borrow
#                       "Price": 26381000000,       # Price per unit of quantity in satoshis
#                       "ExecSide": "1",            # Side of this fill
#                       "AvgPx": 0                  # Calculated average price of all fills on this order.
#                   }
#               ]
# }


# Cancel the order sent in the previous step
msg = {
    "MsgType":"F",                  # Order Cancel Request message. Check for a full doc here: http://www.onixs.biz/fix-dictionary/4.4/msgType_F_70.html
    "ClOrdID": client_order_id      # Unique identifier for Order as assigned by you
}
print send_msg(msg)
# The response of Cancel Order Request is almost identical to the New Order Single, but with different paramenters.
# {
#   "Status": 200,
#   "Description": "OK",
#   "Responses": [
#                   {
#                       "MsgType": "U3",            # Balance respose. Problably because the request also change your account balance.
#                       "5": {"USD_locked": 0},     # In this example, modified the amount of USD you have locked into your account.
#                       "ClientID": 90800003        # Your account ID
#                   },
#                   {
#                       "MsgType": "8",             # Execution Report. Check for a full fix doc here: http://www.onixs.biz/fix-dictionary/4.4/msgType_8_8.html
#                       "OrderID": 5669865,         # Unique identifier for Order as assigned by broker
#                       "ExecID": 36,               # Unique identifier of execution message as assigned by broker
#                       "ExecType": "4",            # 0=New, 1=Partially fill, 2=Fill, 4=Cancelled, 8=Rejected, A=Pending New
#                       "OrdStatus": "4",           # 0=New, 1=Partially fill, 2=Fill, 4=Cancelled, 8=Rejected, A=Pending New
#                       "LeavesQty": 0,             # Quantity open for further execution
#                       "Symbol": "BTCUSD",         # Pair
#                       "OrderQty": 2723810,        # Quantity ordered in satoshis
#                       "LastShares": 0,            # Quantity of shares bought/sold on this fill
#                       "LastPx": 0,                # Price of the last fill
#                       "CxlQty": 2723810,          # Total quantity canceled for this order.
#                       "TimeInForce": "1",         # 0=Day, 1=Good Till Cancel, 4=Fill or Kill
#                       "CumQty": 0,                # Total quantity filled
#                       "ClOrdID": "1440927610",    # Unique identifier for Order as assigned by you
#                       "OrdType": "2",             # 1=Market, 2=Limited, 3=Stop, 4=Stop Limit, G=Swap, P=Pegged
#                       "Side": "1",                # 1=Buy, 2=Sell, E=Redem, F=Lend, G=Borrow
#                       "Price": 26381000000,       # Price per unit of quantity in satoshis
#                       "ExecSide": "1",            # Side of this fill
#                       "AvgPx": 0                  # Calculated average price of all fills on this order.
#                   }
#               ]
#  }


# Generating a bitcoin deposit address
 msg = {
    "MsgType":"U18",    # Deposit request
    "DepositReqID":1,   # Deposit Request ID.
    "Currency":"BTC",   # Currency.
    "BrokerID": 5       # Exchange ID
}
print send_msg(msg)
# {
#    "Status": 200,
#    "Description": "OK",
#    "Responses": [
#                   {
#                       "DepositReqID": 1,                                  # Deposit Request ID
#                       "MsgType": "U19",                                   # Deposit response
#                       "DepositMethodID": null,                            # Deposit Method ID
#                       "DepositMethodName": "deposit_btc",                 # Deposit method name
#                       "DepositID": "12db13d5c36c436993f8e8156467d2b6",    # Deposit ID
#                       "UserID": 90800003,                                 # Your account ID
#                       "ControlNumber": null,                              # Control number. Only used for FIAT deposits
#                       "Type": "CRY",                                      # CRY = Crypto Currency
#                       "Username": "rodrigo",                              # Your username
#                       "AccountID": 90800003,                              # Account ID
#                       "Data": {
#                           "InputAddress": "mzUfpURjD1hDPNk7QBWQkXN5NbKjpf6e56",   # The address that you have to deposit
#                           "Destination": "mtzsTx923NqnFeHugUBsgQKqr8YkEtzQzU"     # This is the exchange wallet. DO NOT DEPOSIT IN THIS ADDRESS.
#                       },
#                       "ClOrdID": null,                                    # Unique identifier for Order as assigned by you
#                       "Status": "0",                                      # 0 - New
#                       "Created": "2015-08-31 05:39:31",                   # Creation date GMT
#                       "BrokerID": 5,                                      # Exchange ID
#                       "Value": 0,                                         # Amount
#                       "PaidValue": 0,                                     # Paid amount
#                       "Currency": "BTC",                                  # Currency
#                       "ReasonID": null,                                   # Reason for the rejection - ID
#                       "Reason": null,                                     # Reason for the rejection - Description
#                       "PercentFee": 0.0,                                  # Percent fee to process this deposit
#                       "FixedFee": 0                                       # Fixed fee in satoshis
#                   },
#               ]
# }
