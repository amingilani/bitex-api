var request = require('request');
var crypto = require('crypto');
var hmac = cryto.createHmac;

var sendMessage = function(msg, env) {
  // default param
  if (typeof(env) === 'undefined') {
    env = 'prod';
  }

  var key = 'YOUR_API_KEY_GENERATED_IN_API_MODULE';
  var secret = 'YOUR_SECRET_KEY_GENERATED_IN_API_MODULE';

  var nonce = Date.now().toString();

  var signature = hmac('sha256', secret)
    .update(secret)
    .update(nonce)
    .digest('hex');

  if (env === 'prod') {
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
        return body;
      }
    });

  }
};

var balanceRequest = function() {
  var msg = {
    "MsgType": "U2", // Balance Request
    "BalanceReqID": 1 // An ID assigned by you. It can be any number.  The response message associated with this request will contain the same ID.
  };

  sendMessage(msg);
};

var newOrder = function() {

  var client_order_id = Date.now().toString();  // this ID must be uniq
  msg = {
      "MsgType":"D",              // New Order Single message. Check for a full doc here: http://www.onixs.biz/fix-dictionary/4.4/msgType_D_68.html
      "ClOrdID": client_order_id, // Unique identifier for Order as assigned by you
      "Symbol":"BTCUSD",          // Can be BTCBRL, BTCPKR, BTCVND, BTCVEF, BTCCLP.
      "Side":"1",                 // 1 - Buy, 2-Sell
      "OrdType":"2",              // 2 - Limited order
      "Price":26381000000,        // Price in satoshis
      "OrderQty":2723810,         // Qty in saothis
      "BrokerID":5                // 1=SurBitcoin, 3=VBTC, 4=FoxBit, 5=Tests , 8=UrduBit, 9=ChileBit
  };

  sendMessage(msg);
};
