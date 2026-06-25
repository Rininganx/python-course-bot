"""
Health-check веб-сервер для Render.com.

Отдаёт 200 OK на любой GET-запрос, чтобы Render не засыпал бесплатный сервис.
Запускается в отдельном потоке, не блокирует polling бота.
"""
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        pass


def start_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"Web server on port {port}")
