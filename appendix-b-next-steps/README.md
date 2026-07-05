# 付録B: 次の一歩 — Kubernetes監視と既存監視からの移行

本書『Grafanaで作る監視入門』付録B に対応する参照リンク集。

付録B は本書の docker compose 環境から本番規模・移行への橋渡しで、専用の実行スタックは
持たない。ここでは付録で触れた各トピックの一次情報へのリンクをまとめる。実際に手を
動かすときは、それぞれの公式ドキュメントに沿って進める。

## Kubernetes で動かす

- **kube-prometheus-stack**（Helm で Prometheus/Grafana/Alertmanager 一式）
  https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack
- **Prometheus Agent mode**（`--agent`、scrape + remote write に特化）
  https://prometheus.io/docs/prometheus/latest/feature_flags/#prometheus-agent
- **Alloy on Kubernetes**（DaemonSet でノードごとに収集、Promtail EOL 後の標準）
  https://grafana.com/docs/alloy/latest/

## 既存監視からの移行

- **node_exporter**（Zabbix エージェント相当の OS メトリクス収集）
  https://github.com/prometheus/node_exporter
- **OpenTelemetry Collector receivers**（CloudWatch など既存ソースの取り込み）
  https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver
- **OTLP を移行の共通言語に**（送り先は Collector の exporter で付け替え）
  https://opentelemetry.io/docs/collector/configuration/

## スケールとマネージド

- **Grafana Mimir**（Prometheus メトリクスの長期保存・水平スケール）
  https://grafana.com/docs/mimir/latest/
- **Grafana Cloud**（LGTM 一式のマネージド）
  https://grafana.com/products/cloud/
- **Amazon Managed Service for Prometheus**
  https://docs.aws.amazon.com/prometheus/

## 学び続けるための一次情報

- Prometheus: https://prometheus.io/docs/
- Grafana / Loki / Tempo / Mimir / Alloy: https://grafana.com/docs/
- OpenTelemetry: https://opentelemetry.io/docs/

signal の成熟度（logs signal は執筆時点で beta）や EOL 情報（Promtail は 2026-03-02
EOL、Grafana Agent は 2025-11 EOL）は時間とともに変わる。最新は上記公式で確認する。
