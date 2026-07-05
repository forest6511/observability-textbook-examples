# ch07-alertmanager — Alertmanager でアラートを設計する

第7章のサンプル。Prometheus のルール評価 → Alertmanager → 通知 を通しで動かす。
第6章までの巨大スタックは使わず、アラートに必要な最小構成に絞っている。

## 構成

- `prometheus.yml` — `rule_files` と `alerting.alertmanagers` を追加した Prometheus 設定
- `rules/alerts.yml` — alerting rule。`HighRequestLatency`（本文の例）と、実機で
  必ず pending→firing する `AlwaysFiring`（テスト用、`for: 15s`）
- `rules/recording.yml` — recording rule `code:prometheus_http_requests_total:sum`
- `alertmanager.yml` — route / receivers / inhibit_rules。webhook は webhook-sink へ、
  Slack は設定例のみ
- `webhook-sink/sink.py` — 届いた webhook 通知を標準出力に書くだけの最小サーバ
  （Slack の実 URL が無くても通知の到達を確認できる）

## バージョン（実機検証 2026-07-05）

- Prometheus 3.12.0（revision 9f27dffc）
- Alertmanager 0.28.0（revision 4ce04fb0）
- node_exporter v1.8.2 / Python 3.13-slim（webhook-sink）

## 使い方

```bash
docker compose up -d

# ルール・設定の検証
docker exec prometheus promtool check rules \
  /etc/prometheus/rules/alerts.yml /etc/prometheus/rules/recording.yml
docker exec alertmanager amtool check-config /etc/alertmanager/alertmanager.yml

# ~1 分待つと AlwaysFiring が firing になり、webhook に通知が届く
docker compose logs webhook-sink
#=> POST / status=firing
#=> alerts=1 alertname=AlwaysFiring severity=warning
```

- Prometheus の Alerts 画面: http://localhost:9090/alerts （pending→firing を観察）
- Alertmanager の UI: http://localhost:9093 （grouping・silence の作成）

```bash
# ルーティングツリーの確認
docker exec alertmanager amtool config routes \
  --alertmanager.url=http://localhost:9093
#=> default-route → {severity="critical"} → critical
```

## メモ

- `AlwaysFiring` は `node_load1 >= 0`（常に真）で、`for: 15s` なのですぐ発火する。
  本番のアラートは症状ベース（レイテンシ・エラー率）で書く。
- Slack receiver は実在する Incoming Webhook URL が要るため設定例のみ。実発火の
  確認は webhook-sink で行う。
- inhibition の `equal` に挙げたラベルが source/target の両方に無いと、無条件に
  抑制がかかる点に注意（本文 7-9 参照）。

## 停止

```bash
docker compose down -v
```
