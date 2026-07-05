#!/usr/bin/env bash
# OTLP HTTP(:4318 = Collector) にメトリクス・ログ・トレースを 1 件ずつ送る。
# 分解版で Collector が3つのバックエンドへ正しく振り分けることを確認するために使う。
# 送信先はすべて Collector（localhost:4318）。Collector が Prometheus / Loki / Tempo へ振る。
set -euo pipefail

NOW_NS=$(python3 -c "import time; print(int(time.time()*1e9))")
# トレースの ID は 16進の固定長。trace_id=32桁, span_id=16桁。
TRACE_ID="5b8aa5a2d2c872e8321cf37308d69df2"
SPAN_ID="051581bf3cb55c13"

# --- メトリクス → Prometheus ---
curl -s -o /dev/null -w "OTLP metric POST -> HTTP %{http_code}\n" \
  -X POST http://localhost:4318/v1/metrics \
  -H "Content-Type: application/json" \
  -d '{
    "resourceMetrics": [{
      "resource": {
        "attributes": [
          {"key": "service.name", "value": {"stringValue": "demo-app"}}
        ]
      },
      "scopeMetrics": [{
        "metrics": [{
          "name": "demo_requests",
          "sum": {
            "aggregationTemporality": 2,
            "isMonotonic": true,
            "dataPoints": [{
              "asInt": "42",
              "timeUnixNano": "'"${NOW_NS}"'",
              "attributes": [
                {"key": "route", "value": {"stringValue": "/checkout"}}
              ]
            }]
          }
        }]
      }]
    }]
  }'

# --- ログ → Loki ---
curl -s -o /dev/null -w "OTLP log POST    -> HTTP %{http_code}\n" \
  -X POST http://localhost:4318/v1/logs \
  -H "Content-Type: application/json" \
  -d '{
    "resourceLogs": [{
      "resource": {
        "attributes": [
          {"key": "service.name", "value": {"stringValue": "demo-app"}}
        ]
      },
      "scopeLogs": [{
        "logRecords": [{
          "timeUnixNano": "'"${NOW_NS}"'",
          "severityText": "INFO",
          "body": {"stringValue": "checkout completed"}
        }]
      }]
    }]
  }'

# --- トレース → Tempo ---
curl -s -o /dev/null -w "OTLP trace POST  -> HTTP %{http_code}\n" \
  -X POST http://localhost:4318/v1/traces \
  -H "Content-Type: application/json" \
  -d '{
    "resourceSpans": [{
      "resource": {
        "attributes": [
          {"key": "service.name", "value": {"stringValue": "demo-app"}}
        ]
      },
      "scopeSpans": [{
        "spans": [{
          "traceId": "'"${TRACE_ID}"'",
          "spanId": "'"${SPAN_ID}"'",
          "name": "GET /checkout",
          "kind": 2,
          "startTimeUnixNano": "'"${NOW_NS}"'",
          "endTimeUnixNano": "'"${NOW_NS}"'"
        }]
      }]
    }]
  }'
