# observability-textbook-examples

書籍 **『Grafanaで作る監視入門 — Prometheus・OpenTelemetryで学ぶオブザーバビリティ実践ハンズオン』**（森川 陽介 / KDP）の companion コード。

Prometheus・Grafana・OpenTelemetry・Loki・Tempo（LGTM スタック）を 1 つの `docker compose` で通しで動かす、実機検証済みのサンプル一式です。本文の各リスト・実行結果・画面はこのリポジトリのコードと 1 対 1 で対応します。

## 動作前提

- Docker Desktop（または Docker Engine）+ Docker Compose v2（`docker compose` コマンド）
- 空きポート: 3000（Grafana）/ 9090（Prometheus）/ 3100（Loki）/ 3200（Tempo）/ 4317・4318（OTLP）
- メモリ 4GB 以上を Docker に割り当て推奨

各コンポーネントのバージョンは [`versions.env`](./versions.env) にピン留めしています（`latest` は使いません）。

## ディレクトリ構成

章ごとに独立して起動できるように分割しています。各ディレクトリで `docker compose up -d` を実行してください。

- `ch02-allinone/` — 第2章: LGTM オールインワンを 5 秒で動かす
- `ch03-decompose/` — 第3章: スタックを分解し docker compose で各コンポーネントを繋ぐ
- `ch04-prometheus/` — 第4章: Prometheus でメトリクスを収集する
- `ch05-promql/` — 第5章: PromQL 実践
- `ch06-grafana/` — 第6章: Grafana でダッシュボードを作る
- `ch07-alertmanager/` — 第7章: Alertmanager でアラートを設計する
- `ch08-instrumentation/` — 第8章: OpenTelemetry でアプリを計装する
- `ch09-collector/` — 第9章: OTel Collector を理解する
- `ch10-tracing/` — 第10章: Tempo で分散トレーシング
- `ch11-loki/` — 第11章: Loki と Alloy でログを集める
- `ch12-correlation/` — 第12章: 三本柱をつなぐ（メトリクス⇄トレース⇄ログの相関）
- `appendix-a-troubleshooting/` — 付録A: トラブルシュート
- `appendix-b-next-steps/` — 付録B: 次の一歩（Kubernetes 監視・既存監視からの移行）
- `_shared/` — 章をまたいで再利用する Grafana provisioning・スクリプト

## 使い方（例: 第2章）

```bash
cd ch02-allinone
docker compose up -d
# Grafana: http://localhost:3000 （初期ユーザー admin / admin）
docker compose down -v
```

## ライセンス

MIT License（[LICENSE](./LICENSE) 参照）。書籍の本文と図表の著作権は著者に帰属します。
