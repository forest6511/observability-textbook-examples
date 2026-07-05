# ch03-decompose — スタックを分解する

第3章のサンプル。第2章のオールインワン（1 コンテナ）を、OpenTelemetry
Collector・Prometheus・Loki・Tempo・Grafana の個別サービスに分解し、
docker compose で自分の手で配線する。

## 構成

- `compose.yaml` — 5 サービスの定義（image タグは versions.env の確定値でピン留め）
- `otel-collector-config.yaml` — OTLP 受信 → metrics/logs/traces を 3 バックエンドへ振り分け
- `prometheus.yml` — 最小設定。OTLP 受信は `--web.enable-otlp-receiver` フラグで有効化
- `loki-config.yaml` — single-binary / filesystem storage
- `tempo.yaml` — OTLP 受信 + local storage
- `grafana/provisioning/datasources/datasources.yaml` — 3 データソースを自動登録
- `send-telemetry.sh` — メトリクス・ログ・トレースを 1 件ずつ Collector に送る

## バージョン（実機検証 2026-07-05）

- Prometheus v3.12.0 / Grafana 12.0.0 / Loki 3.6.0 / Tempo v3.0.0
- OpenTelemetry Collector contrib 0.154.0

## 使い方

```bash
docker compose up -d

# 各サービスの起動確認
curl http://localhost:9090/-/healthy   # Prometheus
curl http://localhost:3100/ready       # Loki
curl http://localhost:3200/ready       # Tempo
curl http://localhost:3000/api/health  # Grafana

# 3 シグナルを送る
./send-telemetry.sh

# 届いたか確認
curl 'http://localhost:9090/api/v1/query?query=demo_requests_total'
# Grafana: http://localhost:3000 （admin / admin）→ Explore
```

## 停止

```bash
docker compose down        # コンテナ停止
docker compose down -v     # データも消す
```
