import json
import jwt
import time
import webbrowser
from threading import Timer
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import google.generativeai as genai
import os

# --- CONFIGURATION ---
SERVICE_ACCOUNT_FILE = os.getenv('WALLET_CREDENTIALS_JSON')
# IMPORTANT: Add your Gemini API Key here
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
# --- END CONFIGURATION ---

# Configure the Gemini API client
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize the Flask app
app = Flask(__name__)
CORS(app)

# Load credentials from the JSON file once when the server starts
try:
    with open(SERVICE_ACCOUNT_FILE, 'r') as f:
        credentials = json.load(f)
    PRIVATE_KEY = credentials['private_key']
    ISSUER_ID = credentials.get("issuerId", "YOUR_ISSUER_ID_MISSING_IN_JSON")
    CLIENT_EMAIL = credentials['client_email']
    print("✅ Server credentials loaded successfully.")
except FileNotFoundError:
    print(f"❌ FATAL ERROR: The credentials file '{SERVICE_ACCOUNT_FILE}' was not found.")
    PRIVATE_KEY = None
except Exception as e:
    print(f"❌ FATAL ERROR: Could not load credentials. Error: {e}")
    PRIVATE_KEY = None


@app.route('/')
def index():
    """Serves the frontend HTML file."""
    return send_from_directory('.', 'index.html')


@app.route('/create-agentic-pass', methods=['POST'])
def create_agentic_pass():
    """
    A new agentic endpoint that performs a multi-step process:
    1. Receives an image.
    2. Extracts structured data from the image.
    3. Reasons about the data to determine an expense category.
    4. Creates and signs a Google Wallet pass.
    """
    if not PRIVATE_KEY or not GEMINI_API_KEY or GEMINI_API_KEY == 'YOUR_GEMINI_API_KEY_HERE':
        return jsonify({"error": "Server is not configured correctly. Check credentials and API Key."}), 500

    if 'receiptImage' not in request.files:
        return jsonify({"error": "No image file found in the request."}), 400

    image_file = request.files['receiptImage']

    try:
        # --- Agentic Step 1: Data Extraction ---
        print("🤖 Agent Step 1: Extracting data from receipt...")
        receipt_image_blob = {"mime_type": image_file.mimetype, "data": image_file.read()}

        extraction_prompt = """
        Analyze this image of a receipt. Extract the following information and return it as a valid JSON object.
        - merchantName: The name of the store or merchant.
        - totalAmount: The final total amount paid, as a string with currency symbol if possible.
        - purchaseDate: The date of the transaction in YYYY-MM-DD format.
        If any field is not clearly visible, return "N/A" for its value.
        """

        # --- FIX: Use GenerationConfig to enforce a JSON response from the model ---
        json_generation_config = genai.types.GenerationConfig(response_mime_type="application/json")
        response = model.generate_content(
            [extraction_prompt, receipt_image_blob],
            generation_config=json_generation_config
        )

        # The response.text is now guaranteed to be a valid JSON string
        extracted_data = json.loads(response.text)
        print(f"   ✅ Extracted Data: {extracted_data}")

        # --- Agentic Step 2: Reasoning & Categorization ---
        print("🤖 Agent Step 2: Reasoning about the merchant to find a category...")
        merchant_name = extracted_data.get("merchantName", "N/A")

        categorization_prompt = f"""
        Based on the merchant name '{merchant_name}', classify this expense into ONE of the following categories:
        Groceries, Dining, Shopping, Travel, Utilities, Entertainment, Health, Transportation, Other.
        Respond with only the category name.
        """
        response = model.generate_content(categorization_prompt)
        category = response.text.strip()
        print(f"   ✅ Determined Category: {category}")

        # --- Agentic Step 3: Data Enrichment & Action ---
        print("🤖 Agent Step 3: Building and signing the pass...")
        jwt_payload = generate_jwt_payload(extracted_data, category)

        # Sign the JWT
        signed_jwt = jwt.encode(jwt_payload, PRIVATE_KEY, algorithm='RS256')
        save_url = f"https://pay.google.com/gp/v/save/{signed_jwt}"
        print(f"   ✅ Successfully created save link.")

        return jsonify({"saveUrl": save_url})

    except Exception as e:
        print(f"❌ An unexpected error occurred during the agentic process: {e}")
        return jsonify({"error": str(e)}), 500


def generate_jwt_payload(data, category):
    """Helper function to construct the JWT payload."""
    pass_object = {
        "id": f"{ISSUER_ID}.{time.time()}",  # Unique ID for each pass
        "classId": f"{ISSUER_ID}.d2887b51-9cf3-4af5-9006-be45ec8477ac",
        "state": "ACTIVE",
        "barcode": {"type": "QR_CODE", "value": f"receipt-{time.time()}"},
        "textModulesData": [
            {"id": "total", "header": "Total", "body": data.get("totalAmount", "N/A")},
            {"id": "date", "header": "Date", "body": data.get("purchaseDate", "N/A")},
            {"id": "category", "header": "Category", "body": category},
            {"id": "created_at", "header": "Pass Created On", "body": time.strftime("%Y-%m-%d %H:%M:%S")}
        ],
        "cardTitle": {"defaultValue": {"language": "en-US", "value": data.get("merchantName", "Receipt")}},
        "header": {"defaultValue": {"language": "en-US", "value": f"Bill for {data.get('totalAmount', 'N/A')}"}}
    }

    return {
        "iss": CLIENT_EMAIL,
        "aud": "google",
        "typ": "savetowallet",
        "iat": int(time.time()),
        "origins": ["http://127.0.0.1:5001"],
        "payload": {"genericObjects": [pass_object]}
    }


if __name__ == '__main__':
    def open_browser():
        webbrowser.open_new('http://127.0.0.1:5001/')


    print("🤖 Agentic Wallet Pass Creator is starting...")
    Timer(1, open_browser).start()
    app.run(port=5001, debug=True)
