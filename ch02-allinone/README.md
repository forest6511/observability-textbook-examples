# 第2章: 5秒で動かす — LGTMオールインワン

書籍「Grafanaで作る監視入門」第2章のサンプルです。Grafana 公式のオールインワンイメージ
`grafana/otel-lgtm` を 1 コンテナで起動し、OTLP でテレメトリを送って Grafana で確認します。

> `grafana/otel-lgtm` は **開発・デモ・テスト専用** です。本番では使いません（第3章で分解します）。

## 前提

- Docker / Docker Compose (v2)
- macOS / Linux / Windows (WSL2)

## はじめかた

```bash
docker compose up -d      # オールインワンを起動（数秒で up）
docker compose logs       # 起動バナーを確認（up and running が出れば完了）
```

起動後、ブラウザで http://localhost:3000 を開きます（初期ログイン: `admin` / `admin`）。
Connections → Data sources に Prometheus / Loki / Tempo / Pyroscope が最初から登録されています。

## テレメトリを送る

```bash
./send-telemetry.sh       # OTLP HTTP(:4318) にサンプルメトリクスを 1 件送る
```

`OTLP metric POST -> HTTP 200` が返ります。Grafana の Explore で Prometheus を選び、
`demo_requests_total` をクエリすると、送った値が表示されます。

## 動作確認済み環境

- `grafana/otel-lgtm:0.28.0`（同梱: Grafana v13.0.1 / OTel Collector v0.151.0 /
  Loki v3.7.1 / Prometheus v3.11.3 / Tempo v2.10.5 / Pyroscope v2.0.2）

## 公開ポート

- `3000` Grafana / `4317` OTLP gRPC / `4318` OTLP HTTP

## 片付け

```bash
docker compose down -v    # コンテナと volume を削除
```
