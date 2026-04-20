# SE445 HW2 - Customer Support Triage

This project implements Homework 2 for **Customer Support Triage**.

## What it does
- Receives a support ticket with HTTP POST
- Accepts JSON with exactly:
  - `name`
  - `email`
  - `message`
- Stores each successful ticket in **Google Sheets**
- Sends a generic **"We received your ticket"** email to the sender

## Required HW2 flow
`HTTP POST ({name, email, message}) -> Google Sheets -> acknowledgment email`

---

## Project files
- `app.py` → Main Flask application
- `requirements.txt` → Python dependencies
- `.env.example` → Example environment variables
- `test_payload.json` → Sample request body

---

## 1) Create a Google Sheet
Create a Google Sheet with the name:

`support_tickets`

The first row can be:

`timestamp | name | email | message`

If the sheet is empty, the app will add this header automatically.

---

## 2) Create a Google Service Account
1. Go to Google Cloud Console
2. Create/select a project
3. Enable:
   - Google Sheets API
   - Google Drive API
4. Create a **Service Account**
5. Download the JSON key file
6. Rename it to:

`service_account.json`

7. Put it in the same folder as `app.py`
8. Share your Google Sheet with the service account email as **Editor**

---

## 3) Gmail setup
If you use Gmail:
1. Turn on 2-Step Verification
2. Create an **App Password**
3. Use that app password as `SMTP_PASSWORD`

Do **not** use your normal Gmail password.

---

## 4) Install
```bash
pip install -r requirements.txt
```

---

## 5) Create `.env`
Copy `.env.example` and create a `.env` file:

```env
GOOGLE_SHEET_NAME=support_tickets
GOOGLE_SERVICE_ACCOUNT_FILE=service_account.json
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
FROM_EMAIL=your_email@gmail.com
```

---

## 6) Run the app
```bash
python app.py
```

Expected:
- API starts on `http://127.0.0.1:5000`

Health check:
```bash
curl http://127.0.0.1:5000/
```

---

## 7) Test the `/ticket` endpoint

### PowerShell
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/ticket" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"name":"Ceren","email":"your_test_email@gmail.com","message":"My payment was charged twice."}'
```

### cURL
```bash
curl -X POST http://127.0.0.1:5000/ticket \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Ceren\",\"email\":\"your_test_email@gmail.com\",\"message\":\"My payment was charged twice.\"}"
```

---

## Expected result
1. The API returns success JSON
2. A new row appears in Google Sheets
3. The sender receives a generic acknowledgment email

---

## Notes
- HW2 does **not** require AI classification yet.
- HW2 focuses on:
  - data input
  - persistence
  - successful receipt email
- AI validation/classification will fit naturally into HW3.

