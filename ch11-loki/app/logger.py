"""JSON 構造化ログを吐き続ける最小アプリ。
1行1JSON で level / msg / service / trace_id を出力する。
trace_id は分散トレーシング（第10章）で生成される ID を模した 32 桁 hex。
Alloy がこのファイルを tail して Loki に送る。
"""
import json
import os
import random
import time

LOG_PATH = os.environ.get("LOG_PATH", "/var/log/app/app.log")

LEVELS = ["info", "info", "info", "warn", "error"]
MESSAGES = {
    "info": ["request handled", "cache hit", "user logged in"],
    "warn": ["slow query", "retry scheduled"],
    "error": ["payment failed", "upstream timeout"],
}


def new_trace_id() -> str:
    """32桁 hex のトレース ID を生成する（W3C traceparent の trace-id 相当）。"""
    return "".join(random.choice("0123456789abcdef") for _ in range(32))


def main() -> None:
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", buffering=1) as f:
        while True:
            level = random.choice(LEVELS)
            record = {
                "level": level,
                "msg": random.choice(MESSAGES[level]),
                "service": "checkout",
                "trace_id": new_trace_id(),
                "status_code": 500 if level == "error" else 200,
            }
            f.write(json.dumps(record) + "\n")
            time.sleep(0.5)


if __name__ == "__main__":
    main()
