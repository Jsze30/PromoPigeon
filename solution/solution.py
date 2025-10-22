from flask import Flask
import math

app = Flask(__name__)

# Dictionary to store receipt points
receipt_points = {}

def calculate_points(receipt):
    points = 0

    # Alphanumeric characters in retailer name
    points += sum(ch.isalnum() for ch in receipt['retailer'])

    # Round dollar total
    if receipt['total'] == int(receipt['total']):
        points += 50
    
    # Multiple of 0.25 total
    if receipt['total'] % 0.25 == 0:
        points += 25
    
    # Number of item pairs
    points += (len(receipt['items']) // 2) * 5

    # Trimmed length of description multiple of 3
    for item in receipt['items']:
        description = item['shortDescription'].strip()
        if len(description) % 3 == 0:
            points += math.ceil(0.2 * float(item['price']))

    # Purchase date odd
    purchase_day = int(receipt['purchaseDate'].split('-')[2])
    if purchase_day % 2 == 1:
        points += 6
    
    # Time of purchase between 2:00 PM and 4:00 PM
    purchase_time = receipt['purchaseTime']
    if int(purchase_time.split(':')[0]) >= 14 and (int(purchase_time.split(':')[0]) < 16 or (int(purchase_time.split(':')[0]) == 16 and int(purchase_time.split(':')[1]) == 0)):
        points += 10

    return points


@app.route('/receipts/process', methods=['POST'])
def process_receipt():


@app.route('/receipts/<id>/points', methods=['GET'])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)