var request = require('request');
var crypto = require('crypto');
var hmac = cryto.createHmac;
var _ = require('lodash');

var client = function(apiKey, apiSecret, BrokerID) {
  // bind client to this
  var client = this;

  // set the keys
  client.apiKey = apiKey;
  client.apiSecret = apiSecret;
  client.BrokerID = BrokerID;

  // send message prototype
  client.sendMessage = function(msg, callback) {
    // default param
    if (typeof(env) === 'undefined') {
      env = 'prod';
    }

    var key = client.apiKey;
    var secret = client.apiSecret;

    var nonce = Date.now().toString();

    var signature = hmac('sha256', secret)
      .update(secret)
      .update(nonce)
      .digest('hex');

      var action = request({
        url: 'https://api.blinktrade.com/tapi/v1/message',
        method: "POST",
        headers: {
          'Content-Type': 'application/json',
          'APIKey': key,
          'Nonce': nonce,
          'Signature': signature
        },
        body: msg
      }, function(err, response, body) {
        if (err === null && response.statusCode === 200) {
          callback(body);
        }
        // do the action
        action();
      });
  };

  // balance check
  client.getBalance = function(callback) {
    var msg = {
      "MsgType": "U2", // Balance Request
      "BalanceReqID": 1 // An ID assigned by you. It can be any number.  The response message associated with this request will contain the same ID.
    };
    sendMessage(msg);
  };

  // create a new order TODO make this
  client.createOrder = function(options, callback) {
    /* example
    options = {
      "ClOrdID": clientOrderId, // Unique identifier for Order as assigned by you
      "Symbol": "BTCUSD", // Can be BTCBRL, BTCPKR, BTCVND, BTCVEF, BTCCLP.
      "Side": "1", // 1 - Buy, 2-Sell
      "OrdType": "2", // 2 - Limited order
      "Price": 26381000000, // Price in satoshis
      "OrderQty": 2723810, // Qty in saothis
      "BrokerID": 5 // 1=SurBitcoin, 3=VBTC, 4=FoxBit, 5=Tests , 8=UrduBit, 9=ChileBit
    }
    */
    options = _(options).pick([
      'ClOrdID', 'Symbol', 'Side', 'OrdType', 'Price', 'OrderQty',
    ]);
    options.MsgType = "D";
    options.BrokerID = client.BrokerID;

    if (typeof(options.clientOrderId) === undefined) {
      options.clientOrderId = Date.now().toString(); // this ID must be uniq
    }
    msg = options;
    client.sendMessage(msg, callback);
  };

  client.cancelOrder = function(clientOrderId, callback) {
    msg = {
      "MsgType": "F", // Order Cancel Request message. Check for a full doc here: http://www.onixs.biz/fix-dictionary/4.4/msgType_F_70.html
      "ClOrdID": clientOrderId // Unique identifier for Order as assigned by you
    };
    sendMessage(msg, callback);
  };

  client.createDepositAddress = function(callback) {
    msg = {
      "MsgType": "U18", // Deposit request
      "DepositReqID": 1, // Deposit Request ID.
      "Currency": "BTC", // Currency.
      "BrokerID": client.BrokerID // Exchange ID
    };
    sendMessage(msg, callback);
  };
};
