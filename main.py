import requests
from flask import Flask
from flask import request, jsonify

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


@app.route('/quote', methods=['POST'])
def method():
    request_data = request.get_json()
    action = request_data['action']
    base_currency = request_data['base_currency']
    quote_currency = request_data['quote_currency']
    amount = request_data['amount']
    inverse = None
    response = requests.get(
        "https://ftx.com/api/markets/" + base_currency + "/" + quote_currency + "/orderbook?depth=20")
    if response.status_code != 200:
        response = requests.get(
            "https://ftx.com/api/markets/" + quote_currency + "/" + base_currency + "/orderbook?depth=20")
        inverse = True

    if response.status_code != 200:
        return jsonify({'Error processing the request': 'FTX API returned error.'
                        })

    ftx_orderbook = response.json()
    weightedResult = 0.0
    if action == "buy":
        calculatedSum = 0.0
        remaining = float(amount)
        for i in ftx_orderbook['result']['asks']:
            if inverse:
                floatPrice = 1 / float(i[0])
            else:
                floatPrice = float(i[0])
            floatSize = float(i[1])

            if remaining > floatSize:
                calculatedSum += floatPrice * floatSize
                remaining = remaining - floatSize
            else:
                calculatedSum += floatPrice * remaining
                weightedResult += calculatedSum / float(amount)
                break

    else:
        calculatedSum = 0.0
        remaining = float(amount)
        for i in ftx_orderbook['result']['bids']:
            if inverse:
                floatPrice = 1 / float(i[0])
            else:
                floatPrice = float(i[0])
            floatSize = float(i[1])

            if remaining > floatSize:
                calculatedSum += floatPrice * floatSize
                remaining = remaining - floatSize
            else:
                calculatedSum += floatPrice * remaining
                weightedResult += calculatedSum / float(amount)
                break

    return jsonify({'total': round(weightedResult * float(amount), 8),
                    'price': round(weightedResult, 8),
                    'currency': quote_currency})


if __name__ == '__main__':
    app.run(host="localhost", port=8000)
