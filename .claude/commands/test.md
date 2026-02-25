テストコードを作成してください。

## 注意点
- `project_path/tests/` ディレクトリにテストコードを作成してください。
- `uv run pytest` でテストを実行できるようにしてください。
- 以下の箇所はモックを使用してください。
  - 外部との通信が必要な箇所
  - 推論など、不定の結果が返ってくる箇所
- `src/` ディレクトリにあるファイルは編集しないでください。修正しないとエラーが発生する場合は、そのままにしてその旨通知してください。

## pyproject.tomlへの追記
```toml
[tool.pytest.ini_options]
pythonpath = [".", "src"]
testpaths = ["tests"]
```
この内容をpyproject.tomlに追記してください。
