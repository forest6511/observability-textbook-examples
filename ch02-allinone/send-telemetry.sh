#!/usr/bin/env bash
# OTLP HTTP(:4318) にサンプルのメトリクスを 1 件送る最小スクリプト。
# 送った demo_requests_total が Grafana(:3000) の Explore で見えることを確認するために使う。
set -euo pipefail

NOW_NS=$(python3 -c "import time; print(int(time.time()*1e9))")

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
