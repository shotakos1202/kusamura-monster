# くさむらモンスター

初代ポケモン風のブラウザRPG（試作版）。HTMLファイル1つで動きます。

## 遊び方

**▶ https://shotakos1202.github.io/kusamura-monster/**

`index.html` をブラウザで開くだけ。スマホ・PCどちらでも遊べます。

| 操作 | キーボード | 画面 / マウス |
|---|---|---|
| 移動 | W A S D | 十字キー |
| A（しらべる・けってい） | Enter | Aボタン / メニュー項目を左クリック |
| B（メニュー・もどる） | Tab | Bボタン |

セーブはブラウザ（localStorage）に自動保存されます。

### ホーム画面に追加（おすすめ）
- iPhone：Safariで開き、共有ボタン →「ホーム画面に追加」
- Android：Chromeで開き、メニュー（︙）→「ホーム画面に追加」または「アプリをインストール」

ホーム画面のアイコンから起動すると、オフラインでも遊べて、セーブも消えにくくなります。

### セーブの移し替え
タイトル画面の「セーブを うつす」でセーブのファイルを作り、移したい端末のタイトル画面で「セーブを とりこむ」を選びます（ファイルはAirDrop・LINE・メールなどで送れます）。

## いま遊べる範囲

- ミドリのむら → 1ばんどうろ → ハナサキタウン（いわジム）→ まよいのもり → 3ばんどうろ → ミナモシティ（みずジム）→ 4ばんどうろ → ミライポート（エスパージム）
- サイドエリア：ミナモかいがん（つりゲーム・ひみつの いりえ）、ミライの おか
- バッジ3こ で試作版クリア

## フォルダ構成

```
index.html          遊べる完成版（tools/build.py で生成）
src/shell.html      画面レイアウト・CSS・ボタン
src/game.js         ゲーム本体（マップ、モンスター、バトル、音楽など）
tools/build.py      src/ から index.html と dist/ を組み立てる
tests/check_maps.py 全マップの到達チェック（入口・人・看板・アイテム・セリフ）
tests/fuzz.py       ランダム操作で詰まり・エラーがないか確認
tools/make_icons.py アプリアイコン（icons/）をゲームの絵から作る
manifest.webmanifest, sw.js  ホーム画面追加・オフライン用
```

## 開発

```
python3 tools/build.py        # index.html を生成
python3 tests/check_maps.py   # マップ検証（Playwright が必要）
python3 tests/fuzz.py         # ランダム操作テスト
```

コードを直すときは `src/` を編集してから `tools/build.py` を実行してください。`index.html` を直接編集しないこと。
