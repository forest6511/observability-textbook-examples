# ch10-tracing — 分散トレーシング: Tempo で遅い箇所を特定する

第10章のサンプル。第8章の計装アプリ（python-dice / go-dice）が出すトレースを
Collector 経由で Tempo に集め、TraceQL で検索する。さらに Tempo の
metrics_generator が trace から RED メトリクスと service graph を生成し、
Prometheus に remote_write する。

## 構成

- `python-app/` `go-app/` — 第8章の計装アプリ（トレース源）
- `otel-collector-config.yaml` — 第9章の完成版（traces を Tempo に振り分け）
- `tempo.yaml` — metrics_generator を有効化。span-metrics / service-graphs を
  overrides で指定し、remote_write で Prometheus に送る
- `prometheus.yml` / compose — Prometheus は `--web.enable-remote-write-receiver`
  で Tempo からの remote_write を受け付ける

## バージョン（実機検証 2026-07-05）

- Tempo v3.0.0 / Prometheus v3.12.0 / Grafana 12.0.0 / Collector 0.154.0
- 計装: opentelemetry-distro 0.51b0（Python）/ otel v1.35.0（Go）

## 使い方

```bash
docker compose up -d --build

# トレースを発生させる
for i in $(seq 1 20); do curl -s localhost:8000/roll >/dev/null; \
  curl -s localhost:8001/roll >/dev/null; done

# TraceQL で検索（Tempo API。start/end は現在時刻に合わせる）
NOW=$(date +%s)
curl -s -G "http://localhost:3200/api/search" \
  --data-urlencode 'q={ resource.service.name = "python-dice" }' \
  --data-urlencode "start=$((NOW-3600))" --data-urlencode "end=$NOW"

# Grafana の Explore > Tempo でウォーターフォール表示（admin / admin）
open http://localhost:3000

# metrics_generator が生成した RED メトリクスを Prometheus で確認
curl -s "http://localhost:9090/api/v1/query?query=traces_spanmetrics_calls_total"
```

## メモ

- **Tempo 3.0 の metrics_generator processor 名はハイフン**（`span-metrics` /
  `service-graphs`）。アンダースコアだと "ignoring unknown metrics-generator
  processor" で無視される。有効化は `overrides.defaults.metrics_generator.processors`
  で行う（トップレベル `metrics_generator` に `processors` は書けない）。
- Prometheus に `--web.enable-remote-write-receiver` が無いと remote_write が
  届かない。
- 生成されるメトリクス: `traces_spanmetrics_calls_total`（RED の Rate）/
  `traces_spanmetrics_latency_*`（Duration）/ `traces_service_graph_request_*`
  （サービス間の依存と遅延）。計装していないサービスでも trace さえあれば RED が得られる。
- TraceQL の `/api/search` は start/end を付けないと既定の狭い時間窓になり、
  トレースがあっても 0 件に見える。現在時刻に合わせた窓を渡す。

## 停止

```bash
docker compose down -v
```
