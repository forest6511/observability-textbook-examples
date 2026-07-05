# 第11章: ログを集める — Loki と Alloy

JSON 構造化ログを吐くアプリのログを Grafana Alloy が収集し、Loki に保存して
LogQL で横断検索する。Promtail は EOL（2026-03-02）のため、現行の正解である
Alloy を使う。

## 構成

- `logger`（python:3.13-slim）— JSON ログ（level / msg / trace_id / status_code）
  を 0.5 秒ごとに `/var/log/app/app.log` へ書き続ける。
- `alloy`（grafana/alloy:v1.17.1）— `config.alloy` に従いログファイルを tail し、
  JSON を解析して level をラベル・trace_id を structured metadata にして Loki へ送る。
- `loki`（grafana/loki:3.6.0）— single-binary / filesystem / schema v13 / tsdb。
- `grafana`（grafana/grafana:12.0.0）— Loki datasource を provisioning で自動登録。

## 起動

```bash
docker compose up -d
```

Loki の起動確認:

```bash
curl http://localhost:3100/ready   # → ready
```

## 動作確認

### LogQL（curl）

```bash
# level ラベルの値（Alloy が JSON から付けた）
curl -s http://localhost:3100/loki/api/v1/label/level/values

# level 別の件数（ログから Errors を数える）
NOW=$(date +%s)000000000
curl -s -G http://localhost:3100/loki/api/v1/query \
  --data-urlencode 'query=sum by (level) (count_over_time({job="checkout"}[1m]))' \
  --data-urlencode "time=$NOW"
```

### ストリーム数（cardinality の確認）

```bash
# trace_id をラベルにしていないのでストリームは level 分の 3 本だけ。
curl -s http://localhost:3100/metrics | grep loki_ingester_streams_created_total
```

### Grafana Explore

ブラウザで http://localhost:3000 （admin/admin）→ Explore → Loki を選び、
`examples/logs.logql` のクエリを実行する。

## 停止

```bash
docker compose down -v
```
