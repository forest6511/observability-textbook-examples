# ch06-grafana — Grafana でダッシュボードを作る

第6章のサンプル。第5章のスタックに dashboards の provisioning を足し、
起動すると RED メソッドのダッシュボードが自動で登録される構成にする。

## 構成（ch05 からの差分）

- `dashboards/red-http.json` — RED ダッシュボード（実機で作成し export）
- `grafana/provisioning/dashboards/dashboards.yaml` — dashboards を自動登録する provisioning 設定
- compose の grafana に `./dashboards:/var/lib/grafana/dashboards:ro` マウントを追加

## バージョン（実機検証 2026-07-05）

- Grafana 12.0.0（commit 4c0e7045f9）
- Prometheus v3.12.0 / node_exporter v1.8.2 / Loki 3.6.0 / Tempo v3.0.0 / Collector 0.154.0

## 使い方

```bash
docker compose up -d

# Grafana を開く（admin / admin）
open http://localhost:3000

# RED ダッシュボードが自動登録されていることを確認
curl -s -u admin:admin "http://localhost:3000/api/search?type=dash-db"
#=> RED メソッド — Prometheus HTTP  uid=red-http-demo
```

ログイン後、Dashboards から「RED メソッド — Prometheus HTTP」を開くと、
handler 別 RPS・全体 RPS・CPU 使用率・p90 レイテンシのパネルが並ぶ。

## メモ

- ダッシュボードの JSON（`dashboards/red-http.json`）は Grafana の API から
  export したもの。`gridPos`（配置）・`targets.expr`（PromQL）・`type`（パネル種別）
  で構成される。
- provisioning の `options.path`（/var/lib/grafana/dashboards）に JSON を置くと、
  起動時に自動登録される。データソース（ch03 で設定）と同じ仕組み。

## 停止

```bash
docker compose down -v
```
