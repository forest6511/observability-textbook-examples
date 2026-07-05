# ch09-collector — OTel Collector を理解する

第9章のサンプル。第3章の最小 Collector 設定に、実務で必須の
memory_limiter（OOM 防止）と batch（スループット）を足した完成 config で、
3つの signal（metric / log / trace）をパイプラインに流す。

## 構成

- `otel-collector-config.yaml` — 完成版の Collector 設定。receivers（otlp）/
  processors（memory_limiter → batch）/ exporters（Prometheus / Loki / Tempo）/
  service.pipelines を明示。processor は順序が意味を持つので memory_limiter を先頭に置く
- `send-telemetry.sh` — OTLP HTTP で metric / log / trace を 1 件ずつ投入する検証スクリプト
- `prometheus.yml` / `loki-config.yaml` / `tempo.yaml` / `grafana/` — 第3章と同じ

## バージョン（実機検証 2026-07-05）

- OpenTelemetry Collector contrib 0.154.0
- Prometheus v3.12.0 / Loki 3.6.0 / Tempo v3.0.0 / Grafana 12.0.0

## 使い方

```bash
docker compose up -d

# config が valid か検証する
docker run --rm -v "$PWD/otel-collector-config.yaml:/cfg.yaml:ro" \
  otel/opentelemetry-collector-contrib:0.154.0 validate --config=/cfg.yaml

# テレメトリを投入する（metric / log / trace）
bash send-telemetry.sh
#=> OTLP metric POST -> HTTP 200
#=> OTLP log POST    -> HTTP 200
#=> OTLP trace POST  -> HTTP 200

# それぞれのバックエンドに届いたか確認する
curl -s "http://localhost:9090/api/v1/query?query=demo_requests_total"
curl -s "http://localhost:3200/api/traces/5b8aa5a2d2c872e8321cf37308d69df2"
```

## メモ

- **processor の順序が意味を持つ**。memory_limiter は pipeline の先頭に置き、
  上限に近づいたら受信側へ backpressure をかけてデータ喪失を最小化する。
  公式は GOMEMLIMIT を hard limit の 80% に設定することも推奨。
- config が壊れていると起動前の `validate` で分かる。たとえば pipeline が
  未定義の exporter を参照すると:
  `Error: service::pipelines::traces: references exporter "otlp/nonexistent" which is not configured`
- logs signal は Collector 全体としては beta。実務ではファイルログを filelog
  receiver で拾うのが現実的（第11章で Loki/Alloy を主軸に扱う）。
- contrib は filelog / tail_sampling など多数のコンポーネントを同梱する。
  本書は contrib を使う。

## 停止

```bash
docker compose down -v
```
