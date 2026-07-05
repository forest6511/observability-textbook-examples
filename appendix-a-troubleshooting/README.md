# 付録A: トラブルシュート集

本書『Grafanaで作る監視入門』付録A に対応するクイックリファレンス。

付録A は各章で実際にぶつかったつまずきを症状別に集めたもので、専用の実行スタックは
持たない。確認コマンドは、対応する章のスタックを起動した状態で実行する。

## 症状 → 参照する章スタック

- **起動・コンテナ**（ポート衝突 / コンテナ落ち / Loki の `user: "0"` /
  Loki・Tempo の healthcheck / node_exporter マウント）→ `ch02-allinone` / `ch03-decompose`
- **メトリクスが出ない**（`up` が 0 / `/targets` DOWN / OTLP receiver /
  native histograms / カーディナリティ）→ `ch04-prometheus`
- **PromQL**（0 件 / rate と sum の順 / `le` 忘れ / 結果の型）→ `ch05-promql`
- **Collector**（`validate` / 未定義 exporter / memory_limiter の drop /
  `prometheus_remote_write` / `filelog` / logs beta）→ `ch09-collector`
- **トレースが途切れる**（`traceparent` / processor 名ハイフン /
  `--web.enable-remote-write-receiver` / TraceQL の start・end）→ `ch10-tracing`
- **ログが集まらない / Loki が重い**（Promtail EOL → Alloy /
  trace_id は structured metadata / LogQL は範囲が要る）→ `ch11-loki`
- **相関のリンクが出ない**（exemplar ラベル名 `traceID` /
  `--enable-feature=exemplar-storage` / derived fields `matcherType: label` /
  provisioning の `$$` エスケープ）→ `ch12-correlation`

## 切り分けの順番

1. `docker compose ps` — コンテナが `Up` か `Exited` か
2. `docker compose logs <サービス名>` — 落ちた理由・drop・配線ミス
3. メトリクスが空なら Prometheus の `/targets` と `up`
4. トレースが途切れるなら `traceparent` の伝播と検索の時間範囲
5. ログが重いならラベルのカーディナリティ
6. 相関が飛ばないなら trace_id が全シグナルに乗っているか、datasource uid が一致しているか

各章スタックの起動方法は、それぞれのディレクトリの README.md を参照。

## 動作環境

Prometheus 3.12 / Grafana 12.x / Loki 3.6.0 / Tempo 3.0.0 /
OpenTelemetry Collector contrib v0.154 / Alloy v1.17 / node_exporter v1.8.2。
バージョンは `../versions.env` に集約。
