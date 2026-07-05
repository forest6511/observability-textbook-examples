# ch08-instrumentation — OpenTelemetry でアプリを計装する

第8章のサンプル。第3章の分解版スタックに、計装した 2 つのアプリを足す。
どちらも OTLP で Collector に送り、Collector が Tempo にトレースを振り分ける。

- **python-dice** — Flask を **zero-code 計装**（`opentelemetry-instrument`）
- **go-dice** — Go を **手動 SDK 計装**（Go はネイティブコンパイルで zero-code が効かない）

## 構成

- `python-app/` — Flask アプリ。`opentelemetry-distro` を入れ、Dockerfile の CMD で
  `opentelemetry-instrument python app.py` として起動。`/roll` が自動 span になり、
  その下に手動 span `charge`（`dice.value` 属性付き）をぶら下げる
- `go-app/` — 手動 SDK でTracerProvider を設定し、`otelhttp.NewHandler` で HTTP を
  自動計装。さらに手動 span `charge` を足す
- `otel-collector-config.yaml` / `prometheus.yml` / `loki-config.yaml` / `tempo.yaml`
  / `grafana/` — 第3章の分解版と同じ

## バージョン（実機検証 2026-07-05）

- OpenTelemetry Collector contrib 0.154.0
- Python: opentelemetry-distro 0.51b0 / opentelemetry-exporter-otlp 1.30.0 / Flask 3.1.0
- Go: go.opentelemetry.io/otel v1.35.0 / otelhttp v0.60.0 / otlptracegrpc v1.35.0
- Prometheus v3.12.0 / Grafana 12.0.0 / Loki 3.6.0 / Tempo v3.0.0

## 使い方

```bash
docker compose up -d --build

# リクエストを流す
curl http://localhost:8000/roll   # python-dice → {"value":N}
curl http://localhost:8001/roll   # go-dice     → value=N

# Grafana を開き、Explore で Tempo を選んでトレースを見る（admin / admin）
open http://localhost:3000
```

Tempo API で直接確認する場合:

```bash
# Tempo が知っている service.name
curl -s http://localhost:3200/api/search/tag/service.name/values
#=> {"tagValues":["go-dice","python-dice"], ...}
```

python-dice のトレースは `GET /roll`（自動）の下に `charge`（手動、`dice.value` 属性）が
ぶら下がる 2 span 構成になる。

## メモ

- **semantic conventions の現実**: 現行の auto-instrumentation（Python distro 0.51b0 /
  Go otelhttp v0.60.0）は、HTTP 属性を**旧名 `http.method` / `http.status_code`** で出す。
  spec の stable 名は `http.request.method` で、Python は `OTEL_SEMCONV_STABILITY_OPT_IN=http`
  で新名に切り替わる。本書はこの現実を正直に扱う。
- **logs signal は beta**。本サンプルは `OTEL_LOGS_EXPORTER=none` にして trace/metric を
  先に固める。ログは第11章で Loki/Alloy を使って扱う。
- Go の zero-code（eBPF/OBI）は Linux 限定・実験的なので、本書は手動 SDK を baseline にする。

## 停止

```bash
docker compose down -v
```
