"""
NEKSORA form webhook — receives form submissions and forwards to Telegram.
Runs as a simple HTTP server on port 8077.
"""
import http.server
import json
import os
import urllib.request
import urllib.parse
from pathlib import Path

# Read bot token from hermes .env
ENV_PATH = Path.home() / ".hermes" / ".env"
BOT_TOKEN = None
CHAT_ID = "419186486"  # Sergei's Telegram ID

def load_token():
    global BOT_TOKEN
    if BOT_TOKEN:
        return BOT_TOKEN
    for line in ENV_PATH.read_text().splitlines():
        if line.startswith("TELEGRAM_BOT_TOKEN="):
            BOT_TOKEN = line.split("=", 1)[1].strip()
            return BOT_TOKEN
    raise RuntimeError("TELEGRAM_BOT_TOKEN not found in .env")

def send_telegram(text):
    token = load_token()
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())

class Handler(http.server.BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "https://neksora.pro")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        if self.path != "/api/contact":
            self.send_response(404)
            self.end_headers()
            return

        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))

            name = body.get("name", "").strip()
            phone = body.get("phone", "").strip()
            obj = body.get("object", "").strip()
            message = body.get("message", "").strip()

            if not name or not phone:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "https://neksora.pro")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Имя и телефон обязательны"}).encode())
                return

            # Format Telegram message
            tg_text = (
                "🔔 <b>Новая заявка с сайта neksora.pro</b>\n\n"
                f"👤 <b>{name}</b>\n"
                f"📞 {phone}\n"
            )
            if obj:
                tg_text += f"🏠 {obj}\n"
            if message:
                tg_text += f"\n📝 {message}\n"

            send_telegram(tg_text)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "https://neksora.pro")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True}).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "https://neksora.pro")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def log_message(self, format, *args):
        print(format % args)

if __name__ == "__main__":
    server = http.server.HTTPServer(("127.0.0.1", 8077), Handler)
    print("NEKSORA webhook running on :8077")
    server.serve_forever()
