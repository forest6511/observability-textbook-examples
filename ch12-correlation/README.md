# 第12章: 三本柱をつなぐ — メトリクス⇄トレース⇄ログの相関

第10章（トレース + metrics_generator）と第11章（Loki のログ）の全部入りスタックに、
4 方向の相関設定を足す。1 つの事象を、メトリクス→トレース→ログ→トレース→メトリクスと
数クリックで追える状態を作る。

## 4 方向の相関

- **exemplar（メトリクス → トレース）** — Prometheus datasource の
  `exemplarTraceIdDestinations`。ヒストグラムの exemplar 点に付いた traceID で Tempo へ。
- **tracesToLogsV2（トレース → ログ）** — Tempo datasource。span から同じ trace_id の
  ログを Loki で開く。`filterByTraceID: true`。
- **derivedFields（ログ → トレース）** — Loki datasource。ログの trace_id（structured
  metadata）を拾って Tempo のトレースへリンク。
- **tracesToMetrics / serviceMap（トレース → メトリクス）** — Tempo datasource。
  span から `traces_spanmetrics_*` の RED メトリクスへ、サービスグラフも描く。

設定は `grafana/provisioning/datasources/datasources.yaml` に集約。uid（prometheus /
tempo / loki）の相互参照が鍵。

## 構成

- `python-dice` — /roll で trace を出し、1 の目で error ログを出す。zero-code 計装が
  ログに trace_id を注入し OTLP で送る（`OTEL_LOGS_EXPORTER=otlp` +
  `OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true`）。
- `otel-collector`（0.154.0）— trace/metric/log を受けて Tempo/Prometheus/Loki へ。
- `tempo`（v3.0.0）— metrics_generator で span metrics と service graph を生成、
  exemplar 付きで Prometheus へ remote_write。
- `prometheus`（v3.12.0）— `--enable-feature=exemplar-storage` で exemplar を保持。
- `loki`（3.6.0）— OTLP ログを structured metadata（trace_id）付きで保存。
- `grafana`（12.0.0）— 4 相関つき datasource を provisioning。

## 起動

```bash
docker compose up -d --build
```

負荷をかける（1 の目で error ログ + trace が出る）:

```bash
for i in $(seq 1 60); do curl -s http://localhost:8000/roll >/dev/null; done
```

## 動作確認（curl）

```bash
# ログに trace_id が乗っているか（logs -> traces の材料）
NOW=$(date +%s)000000000; START=$(($(date +%s) - 300))000000000
curl -s -G http://localhost:3100/loki/api/v1/query_range \
  --data-urlencode 'query={service_name="python-dice"} |= `payment failed`' \
  --data-urlencode "start=$START" --data-urlencode "end=$NOW" --data-urlencode "limit=1"

# span metrics が生成されているか（traces -> metrics）
curl -s -G http://localhost:9090/api/v1/query \
  --data-urlencode 'query=sum(traces_spanmetrics_calls_total) by (service_name)'

# exemplar が保持されているか（metrics -> traces）
NOW=$(date +%s); START=$((NOW-300))
curl -s -G http://localhost:9090/api/v1/query_exemplars \
  --data-urlencode 'query=traces_spanmetrics_latency_bucket' \
  --data-urlencode "start=$START" --data-urlencode "end=$NOW"
```

## Grafana で相関をたどる

http://localhost:3000 （admin/admin）→ Explore。

1. Loki で `{service_name="python-dice"} |= \`payment\`` → ログ行を開くと TraceID リンク → Tempo へ。
2. Tempo で trace を開く → span から Logs / RED メトリクスへ。
3. Prometheus で `traces_spanmetrics_latency_bucket` を Graph 表示 → exemplar 点 → Tempo へ。

## 停止

```bash
docker compose down -v
```
