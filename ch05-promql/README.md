# ch05-promql — PromQL 実践

第5章のサンプル。第3章/第4章の分解版スタック（Prometheus + node_exporter）を
そのまま実行環境とし、章本文の PromQL を実行して確認する。

## 構成

- 第4章と同じ compose（Collector / Prometheus / node_exporter / Loki / Tempo / Grafana）
- 章本文の全クエリは `examples/red-use.promql` に収録

## バージョン（実機検証 2026-07-05）

- Prometheus v3.12.0 / node_exporter v1.8.2
- Grafana 12.0.0 / Loki 3.6.0 / Tempo v3.0.0 / Collector 0.154.0

## 使い方

```bash
docker compose up -d

# クエリの実行方法は 2 通り
# (1) Prometheus UI: http://localhost:9090 の入力欄に貼る
# (2) Grafana Explore: http://localhost:3000 → Explore → Prometheus データソース

# CLI から実行する例（RPS）
curl -sG http://localhost:9090/api/v1/query \
  --data-urlencode 'query=sum(rate(prometheus_http_requests_total[5m]))'

# レイテンシ p90（native histogram）
curl -sG http://localhost:9090/api/v1/query \
  --data-urlencode 'query=histogram_quantile(0.9, sum by (handler) (rate(prometheus_http_request_duration_seconds[5m])))'
```

## メモ

- `prometheus_http_request_duration_seconds` は現行 Prometheus では native
  histogram（`_bucket` 系列が無い）。`le` を意識せず `histogram_quantile` が書ける。
- エラー率クエリ（`code=~"5.."`）は、この環境ではエラーが出ないため空を返す。
  「エラーが無い健全な状態」を正しく表している（本文 5-6 参照）。
- `offset 1w` は、データが 1 週間分たまるまで空を返す（本文 5-10 参照）。

## 停止

```bash
docker compose down -v
```
