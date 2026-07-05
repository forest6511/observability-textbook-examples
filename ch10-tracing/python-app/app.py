"""zero-code 計装で自動トレースされる Flask アプリ。
opentelemetry-instrument で起動すると /roll ハンドラが自動で span になる。
さらに、業務的に意味のある処理を手動 span（charge）で細かく見せる。
"""
import random

from flask import Flask
from opentelemetry import trace

app = Flask(__name__)
# 手動 span 用の tracer。zero-code の自動計装が SDK をセットアップ済みなので、
# ここでは get_tracer するだけでよい。
tracer = trace.get_tracer("dice.app")


@app.route("/roll")
def roll():
    # 自動 span（Flask のハンドラ）の下に、手動 span をぶら下げる。
    with tracer.start_as_current_span("charge") as span:
        value = random.randint(1, 6)
        # semantic conventions の app.* 接頭辞で独自属性を付ける。
        span.set_attribute("dice.value", value)
        return {"value": value}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
