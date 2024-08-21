from flask import Flask, request, jsonify
import urllib.parse
from functools import wraps
import logging
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains on all routes

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = app.logger

# Get API secret from environment variable
API_SECRET = os.environ.get('API_SECRET', 'default_secret')

def require_api_secret(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.headers.get('X-API-Secret') != API_SECRET:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

def parse_payload(payload):
    decoded_payload = urllib.parse.parse_qs(payload)
    lead_data = {key: value[0] if len(value) == 1 else value 
                 for key, value in decoded_payload.items()}
    return lead_data

def validate_lead_data(lead_data):
    required_fields = ['name', 'email', 'phone']
    for field in required_fields:
        if field not in lead_data:
            raise ValueError(f"Missing required field: {field}")

def process_lead(lead_data):
    try:
        validate_lead_data(lead_data)
        logger.info(f"Received lead: {lead_data}")
        return jsonify({'status': 'success', 'message': 'Lead received successfully'}), 200
    except ValueError as e:
        logger.error(f"Invalid lead data: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error processing lead: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/lead_api', methods=['POST'])
@require_api_secret
def receive_lead():
    lead_data = parse_payload(request.get_data().decode('utf-8'))
    return process_lead(lead_data)

@app.route('/test_lead_api', methods=['POST'])
def test_receive_lead():
    logger.info(f"Received test lead: {request.get_data().decode('utf-8')}")
    return receive_lead()

if __name__ == '__main__':
    app.run(debug=True)