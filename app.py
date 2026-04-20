import os
from datetime import datetime
from flask import Flask, request, jsonify
import gspread
from google.oauth2.service_account import Credentials
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# =========================
# CONFIG
# =========================
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "support_tickets")
GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "service_account.json")

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USERNAME)

REQUIRED_KEYS = {"name", "email", "message"}


# =========================
# GOOGLE SHEETS
# =========================
def get_sheet():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    creds = Credentials.from_service_account_file(
        GOOGLE_SERVICE_ACCOUNT_FILE,
        scopes=scopes
    )
    client = gspread.authorize(creds)
    sheet = client.open(GOOGLE_SHEET_NAME).sheet1
    return sheet


def ensure_header(sheet):
    expected_header = ["timestamp", "name", "email", "message"]
    current_header = sheet.row_values(1)

    if current_header != expected_header:
        if current_header:
            # If first row exists but is different, do nothing automatically.
            # This keeps the demo simple and prevents accidental overwrite.
            return
        sheet.append_row(expected_header)


def save_to_sheets(name: str, email: str, message: str):
    sheet = get_sheet()
    ensure_header(sheet)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [timestamp, name, email, message]
    sheet.append_row(row)
    return timestamp


# =========================
# EMAIL
# =========================
def send_ack_email(to_email: str, name: str):
    if not SMTP_USERNAME or not SMTP_PASSWORD or not FROM_EMAIL:
        raise ValueError("SMTP credentials are missing. Check your .env file.")

    subject = "We received your ticket"
    body = f"""Hello {name},

We received your support ticket successfully.

Our team will review your message and get back to you as soon as possible.

Best regards,
Support Team
"""

    msg = MIMEMultipart()
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(FROM_EMAIL, to_email, msg.as_string())


# =========================
# VALIDATION
# =========================
def validate_payload(data):
    if not data:
        return False, "Request body must be valid JSON."

    incoming_keys = set(data.keys())
    if incoming_keys != REQUIRED_KEYS:
        return False, (
            "JSON body must contain exactly these keys: "
            '{"name", "email", "message"}'
        )

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    message = str(data.get("message", "")).strip()

    if not name or not email or not message:
        return False, "name, email, and message cannot be empty."

    return True, ""


# =========================
# ROUTES
# =========================
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "ok",
        "message": "HW2 Customer Support Triage API is running."
    }), 200


@app.route("/ticket", methods=["POST"])
def receive_ticket():
    try:
        data = request.get_json(silent=True)

        is_valid, error_message = validate_payload(data)
        if not is_valid:
            return jsonify({
                "status": "error",
                "message": error_message
            }), 400

        name = data["name"].strip()
        email = data["email"].strip()
        message = data["message"].strip()

        timestamp = save_to_sheets(name, email, message)
        send_ack_email(email, name)

        return jsonify({
            "status": "success",
            "message": "Ticket stored and acknowledgment email sent.",
            "stored_data": {
                "timestamp": timestamp,
                "name": name,
                "email": email,
                "message": message
            }
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
