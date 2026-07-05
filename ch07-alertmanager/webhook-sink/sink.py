"""Alertmanager の webhook 通知を受けて、中身を標準出力に書くだけの最小サーバ。

Slack の実 URL が無くても、アラートが Alertmanager を経由して通知先まで
届いたことを、docker compose logs webhook-sink で確認できるようにする。
標準ライブラリだけで動くので追加の pip install は不要。
"""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            data = {}

        status = data.get("status", "?")
        alerts = data.get("alerts", [])
        print(f"POST / status={status}", flush=True)
        for a in alerts:
            labels = a.get("labels", {})
            name = labels.get("alertname", "?")
            sev = labels.get("severity", "?")
            print(
                f"alerts={len(alerts)} alertname={name} severity={sev}",
                flush=True,
            )

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    # アクセスログは邪魔なので黙らせる（本文で見せたい行だけ出す）。
    def log_message(self, *args):
        pass


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 5001), Handler).serve_forever()
