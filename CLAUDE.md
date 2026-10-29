# くさむらモンスター — 開発メモ

- 編集するのは `src/game.js` と `src/shell.html`。`index.html` と `dist/` は `python3 tools/build.py` で生成する。
- 変更後は `python3 tools/build.py && python3 tests/check_maps.py`。大きな変更では `tests/fuzz.py` も実行する。
- claude.ai のアーティファクトとして公開するときは `dist/artifact.html` を使う（doctype なしの版）。
- ユーザーへの返答は日本語。ゲーム内テキストはひらがな・カタカナ中心で、全角スペース区切り。
- ゲーム内テキストの改行は JS 文字列の `\n`。二重エスケープ（`\\n`）すると画面に「\n」と表示されてしまうので注意。
- マップを追加したら、入口・人・看板・アイテムに歩いて行けるかを `tests/check_maps.py` で必ず確認する。
