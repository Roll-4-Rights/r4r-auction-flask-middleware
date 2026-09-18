from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# ============= INFRASTRUCTURE LAYER =============
NOCODB_URL = os.environ.get('NOCODB_URL', 'http://localhost:8080')
NOCODB_TOKEN = os.environ.get('NOCODB_TOKEN')
NOCODB_SITE_BASE_ID = os.environ.get('NOCODB_SITE_BASE_ID')

# Explicitly tracks your live workspace table IDs
TABLE_IDS = {
    'Site Content': 'mjy7qbt2mekpcer',
    'Banner Messages': 'm5yzd3dm3341les',      # Replace with your actual live banner ID string
    'Campaign Settings': 'me952mqf3n1v9yw',
}

ALLOWED_ORIGINS = os.environ.get(
    'ALLOWED_ORIGINS',
    'https://duckdns.org'
).split(',')

CORS(app, supports_credentials=True, origins=ALLOWED_ORIGINS)

# Router helper explicitly locked down to your Site Base hash pointer
def nocodb_records_url(table_name, record_id=None):
    table_id = TABLE_IDS[table_name]
    base = f'{NOCODB_URL}/api/v2/bases/{NOCODB_SITE_BASE_ID}/tables/{table_id}/records'
    return f'{base}/{record_id}' if record_id else base

# ============= ROUTING ENDPOINTS =============

@app.route('/api/site-content', methods=['GET'])
def get_site_content():
    try:
        headers = {'xc-token': NOCODB_TOKEN}
        url = nocodb_records_url('Site Content')
        response = requests.get(url, headers=headers, params=request.args)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/banner-messages', methods=['GET'])
def get_banner_messages():
    try:
        headers = {'xc-token': NOCODB_TOKEN}
        url = nocodb_records_url('Banner Messages')
        response = requests.get(url, headers=headers, params=request.args)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/campaign-info', methods=['GET'])
def get_campaign_info():
    try:
        headers = {'xc-token': NOCODB_TOKEN}
        url = nocodb_records_url('Campaign Settings')
        response = requests.get(url, headers=headers)
        settings_data = response.json()
        
        records = settings_data.get('list', []) if isinstance(settings_data, dict) else settings_data
        settings = records[0] if isinstance(records, list) and len(records) > 0 else (records if isinstance(records, dict) else {})

        raw_start = settings.get('Auction Start Time', '')
        raw_end = settings.get('Auction End Time', '')

        if raw_start and ' ' in raw_start and 'T' not in raw_start:
            raw_start = raw_start.replace(' ', 'T')
        if raw_end and ' ' in raw_end and 'T' not in raw_end:
            raw_end = raw_end.replace(' ', 'T')

        # Attachment extraction layout
        raw_logo = settings.get('Charity Logo', '')
        logo_url = ''
        if isinstance(raw_logo, list) and len(raw_logo) > 0:
            attachment = raw_logo[0]
            logo_url = attachment.get('url') or attachment.get('signedUrl') or attachment.get('path', '')
            if logo_url and logo_url.startswith('/'):
                logo_url = f"{NOCODB_URL}{logo_url}"

        return jsonify({
            'name': settings.get('Campaign Name', ''),
            'tagline': settings.get('Campaign Information', ''),
            'charityName': settings.get('Charity Organization', ''),
            'charityDescription': settings.get('Charity Organization Information', ''),
            'startDate': raw_start, 
            'endDate': raw_end,    
            'charityLogoUrl': logo_url, 
            'charityWebsite': settings.get('Charity Website', '')
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001) # Set to run on a separate port line (5001)
