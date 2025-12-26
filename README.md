# WhatsApp → Google Sheets AI Bot

A lightweight AI-powered WhatsApp bot that allows users to **add, update, and retrieve data from Google Sheets through simple WhatsApp messages.**

This makes it easy to use Google Sheets as a live database without opening a browser.

---

## ✨ Features

- Add new records to Google Sheets via WhatsApp  
- Retrieve stored information instantly  
- Natural language understanding (AI powered)  
- Supports multiple users  
- Real-time sync with Google Sheets  

---

## ⚙️ How It Works

1. User sends a message on WhatsApp  
2. The AI interprets the request  
3. Data is written to or read from Google Sheets  
4. The response is sent back to WhatsApp  

---

## 🧩 Example Commands

| WhatsApp Message | Action |
|------------------|-------|
| `Add John 08012345678` | Saves contact to Google Sheets |
| `Get John` | Retrieves John's record |
| `List customers` | Returns all saved customers |

---

## 🛠 Tech Stack

- Python / Node.js  
- WhatsApp API (Twilio / Meta Cloud API)  
- Google Sheets API  
- Groq / LLM integration  

---

## 🚀 Setup

1. Clone the repository  
2. Create a Google Sheets API service account  
3. Add your API keys to `.env`  
4. Run the server  
