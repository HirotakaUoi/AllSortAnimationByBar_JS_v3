# ソートアルゴリズム アニメーション v3

v2 に 3-way partition クイックソートと並列クイックソートを追加したバージョン。

## 起動

```bash
uvicorn main:app --reload --port 8003
```

ブラウザ: http://localhost:8003

## v2 との違い

- **クイックソート（3-way partition）** を追加。重複値が多い配列で通常版より大幅に高速。
- **並列クイックソート（CPU数無制限 / CPU数制限）** を追加。複数サブ範囲を同時並行でパーティション処理し、並列実行の挙動を可視化。
- **並列数スライダー** — CPU数制限版は 2〜1024 の範囲でスライダーにより同時実行タスク数を指定可能。

## 対応アルゴリズム（15種）

| # | アルゴリズム |
|---|---|
| 1〜7 | バブル / 選択 / 挿入 / シェル / クイック(通常・3点中央・ランダム) |
| 8 | クイックソート（3-way partition） |
| 9 | 並列クイックソート（CPU数無制限） |
| 10 | 並列クイックソート（CPU数制限） |
| 11〜12 | バイトニック / 並列バイトニック |
| 13〜15 | コム / ノーム / パンケーキ |

## ファイル構成

```
main.py              # FastAPI + WebSocket エンドポイント
sort_algorithms.py   # 15種のソートアルゴリズム（ジェネレータ形式）
requirements.txt
render.yaml          # Render 自動デプロイ設定
static/
  index.html
  css/style.css
  js/
    canvas.js        # SortCanvas クラス（Canvas 2D 描画）
    ws_client.js     # AnimationClient（WebSocket ラッパー）
    app.js           # SortPanel クラス + パネル管理（並列数スライダー含む）
```

## アーキテクチャ

```
[Browser] ←─ WebSocket ─→ [FastAPI / main.py] ←─ import ─→ [sort_algorithms.py]
  app.js                    /api/start                         generator関数群
  canvas.js                 /ws/{session_id}
```

## WebSocket フレーム形式

```json
{
  "data":     [42, 17, 95, ...],
  "color":    ["b", "r", "g", ...],
  "arrows":   [[i, j], ...],
  "texts":    ["pivot=42", ...],
  "lines":    [{"x": 3, "color": "gray"}, ...],
  "bars":     [2, 5],
  "finished": false
}
```

## アルゴリズム追加手順

1. `sort_algorithms.py` にジェネレータ関数を実装（`yield` でフレームを1つずつ出力）
2. `main.py` の `ALGORITHMS` リストに登録
