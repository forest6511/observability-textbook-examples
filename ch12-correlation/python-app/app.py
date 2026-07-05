"""zero-code 計装で自動トレースされる Flask アプリ。
opentelemetry-instrument で起動すると /roll ハンドラが自動で span になる。
さらに、業務的に意味のある処理を手動 span（charge）で細かく見せる。

第12章の相関のために、各リクエストでログも出す。zero-code 計装が
Python logging を OTLP logs に橋渡しし、現在の trace_id をログに埋め込む。
このログが Collector → Loki に流れ、trace_id でトレースとログが繋がる。
"""
import logging
import random
import time

from flask import Flask
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

app = Flask(__name__)
# 手動 span 用の tracer。zero-code の自動計装が SDK をセットアップ済みなので、
# ここでは get_tracer するだけでよい。
tracer = trace.get_tracer("dice.app")
logger = logging.getLogger(__name__)


@app.route("/roll")
def roll():
    # 自動 span（Flask のハンドラ）の下に、手動 span をぶら下げる。
    with tracer.start_as_current_span("charge") as span:
        value = random.randint(1, 6)
        span.set_attribute("dice.value", value)
        # 1 の目を「決済失敗」に見立てて error ログを出す。
        # zero-code 計装がこのログに現在の trace_id を添付し OTLP で送る。
        if value == 1:
            # 決済に失敗するリクエストは、リトライで時間がかかってから落ちる。
            # この遅延が charge span を長くし、メトリクスの p90 を押し上げる。
            # レイテンシの跳ね上がり → 遅い span → 失敗ログ、という相関の起点になる。
            time.sleep(random.uniform(0.4, 0.8))
            span.set_attribute("charge.retried", True)
            # span をエラー状態にする。metrics_generator が status_code=
            # STATUS_CODE_ERROR の span metrics を生成し、エラー率が計算できる。
            span.set_status(Status(StatusCode.ERROR, "payment failed"))
            logger.error("payment failed for dice roll")
        else:
            time.sleep(random.uniform(0.005, 0.02))
            logger.info("dice roll handled")
        return {"value": value}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(host="0.0.0.0", port=8000)
