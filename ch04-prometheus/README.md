# ch04-prometheus — Prometheus でメトリクスを収集する

第4章のサンプル。第3章の分解版に node_exporter を足し、Prometheus が
pull でホストメトリクスを収集する構成にする。native histograms の
受け入れも有効化する。

## 構成（ch03 からの差分）

- `node-exporter` サービスを追加（quay.io/prometheus/node-exporter:v1.8.2）
- `prometheus.yml` に `job_name: node` を追加、`scrape_native_histograms: true` を有効化

## バージョン（実機検証 2026-07-05）

- Prometheus v3.12.0 / node_exporter v1.8.2
- Grafana 12.0.0 / Loki 3.6.0 / Tempo v3.0.0 / Collector 0.154.0

## 使い方

```bash
docker compose up -d

# scrape 対象の状態を確認（Prometheus UI）
open http://localhost:9090/targets      # node と prometheus が UP

# node メトリクスが収集できているか
curl -G http://localhost:9090/api/v1/query \
  --data-urlencode 'query=up{job="node"}'    # up = 1

# node_exporter の生メトリクス
curl http://localhost:9100/metrics | head
```

## メモ

- node-exporter は macOS / Windows でも動くよう、ホスト rootfs のマウントを
  付けていない（コンテナ視点のメトリクスを出す）。Linux で本格的にホストを
  見るには `--path.rootfs=/host` と `/:/host:ro` を足す。

## 停止

```bash
docker compose down -v
```
