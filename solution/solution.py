import uuid
from flask import Flask, request, jsonify
import math
import re
from datetime import datetime

app = Flask(__name__)

# Dictionary to store receipt points
receipt_points = {}

def validate_receipt(receipt):
    """Validate receipt against API specification."""
    if not isinstance(receipt, dict):
        return False
    
    # Check required fields
    required_fields = ['retailer', 'purchaseDate', 'purchaseTime', 'items', 'total']
    for field in required_fields:
        if field not in receipt:
            return False
    
    # Validate retailer
    if not isinstance(receipt['retailer'], str) or not re.match(r'^[\w\s\-&]+$', receipt['retailer']):
        return False
    
    # Validate purchaseDate (format: YYYY-MM-DD)
    if not isinstance(receipt['purchaseDate'], str):
        return False
    try:
        datetime.strptime(receipt['purchaseDate'], '%Y-%m-%d')
    except ValueError:
        return False
    
    # Validate purchaseTime (format: HH:MM in 24-hour time)
    if not isinstance(receipt['purchaseTime'], str):
        return False
    try:
        datetime.strptime(receipt['purchaseTime'], '%H:%M')
    except ValueError:
        return False
    
    # Validate total
    if not isinstance(receipt['total'], str) or not re.match(r'^\d+\.\d{2}$', receipt['total']):
        return False
    
    # Validate items (must be array with at least 1 item)
    if not isinstance(receipt['items'], list) or len(receipt['items']) < 1:
        return False
    
    for item in receipt['items']:
        if not isinstance(item, dict):
            return False
        
        # Check required item fields
        if 'shortDescription' not in item or 'price' not in item:
            return False
        
        # Validate shortDescription
        if not isinstance(item['shortDescription'], str) or not re.match(r'^[\w\s\-]+$', item['shortDescription']):
            return False

        # Validate price
        if not isinstance(item['price'], str) or not re.match(r'^\d+\.\d{2}$', item['price']):
            return False
    
    return True

def calculate_points(receipt):
    points = 0

    # Alphanumeric characters in retailer name
    points += sum(ch.isalnum() for ch in receipt['retailer'])

    # Round dollar total
    if float(receipt['total']) == int(float(receipt['total'])):
        points += 50
    
    # Multiple of 0.25 total
    if float(receipt['total']) % 0.25 == 0:
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
    try:
        payload = request.get_json(force=True, silent=False)
    except Exception:
        return jsonify({"error": "The receipt is invalid."}), 400

    if not validate_receipt(payload):
        return jsonify({"error": "The receipt is invalid."}), 400

    receipt_id = str(uuid.uuid4())
    receipt_points[receipt_id] = payload

    return jsonify({"id": receipt_id}), 200

@app.route('/receipts/<id>/points', methods=['GET'])
def get_receipt_points(id):
    if id not in receipt_points:
        return jsonify({"error": "Receipt not found."}), 404

    points = calculate_points(receipt_points[id])
    return jsonify({"points": points}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
