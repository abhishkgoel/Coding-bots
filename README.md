# Agentic Google Wallet Pass Creator

This project is a web application that uses a multi-step AI agent to read, categorize, and create a smart Google Wallet pass from an uploaded receipt image.

## Features

- **Web Interface**: A simple drag-and-drop UI to upload receipt images.
- **Agentic AI**:
    1.  **Extracts Data**: Intelligently pulls the merchant name, total, and date from the receipt.
    2.  **Reasons & Categorizes**: Determines the expense category (e.g., "Dining", "Groceries") based on the merchant.
    3.  **Enriches & Acts**: Creates a fully-formed Google Wallet pass with the extracted and categorized data.
- **Secure Backend**: A Python Flask server handles all secure operations, including communication with AI services and the cryptographic signing of Wallet passes.
- **One-Click Operation**: The entire application starts with a single command, automatically opening the web interface.

## Project Structure

```
.
├── app.py                  # The Python Flask backend server
├── index.html                # The HTML/JS frontend
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Prerequisites

1.  **Python 3.x**
2.  **Google Cloud Project** with the **Google Wallet API** enabled.
3.  **Google Wallet Issuer Account** with approved publishing access.
4.  **Google AI (Gemini) API Key**.
5.  A **Service Account** linked to your Google Wallet Issuer account.

## Setup Instructions

### 1. Clone the Repository

Clone this repository to your local machine.

### 2. Install Dependencies

Create a virtual environment and install the required Python libraries.

```bash
# Create and activate a virtual environment (optional but recommended)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Credentials

This application uses environment variables to securely manage API keys and credentials.

**A. Get Your Credentials**

You will need:
- Your **Google Wallet Service Account Key**: This is a JSON file. Make sure it contains your `issuerId`.
- Your **Gemini API Key**: A plain text string from the Google AI Studio.

**B. Set the Environment Variables**

You must set two environment variables in your terminal session before running the app.

**On macOS or Linux:**

```bash
# Paste the entire content of your Google Wallet JSON key file inside the quotes
export WALLET_CREDENTIALS_JSON='<PASTE CONTENT OF walletapi.json HERE>'

# Paste your Gemini API Key
export GEMINI_API_KEY='<PASTE YOUR GEMINI API KEY HERE>'
```

**On Windows (Command Prompt):**

```cmd
:: Paste the entire content of your Google Wallet JSON key file
set "WALLET_CREDENTIALS_JSON=<PASTE CONTENT OF walletapi.json HERE>"

:: Paste your Gemini API Key
set "GEMINI_API_KEY=<PASTE YOUR GEMINI API KEY HERE>"
```

### 4. Run the Application

With the environment variables set, start the application with a single command:

```bash
python app.py
```

Your default web browser will automatically open to `http://127.0.0.1:5001`, and you can start creating passes.
