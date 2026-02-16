# photo_mover

photo_mover は、ソースツリーから指定したディレクトリへ写真・動画ファイルを移動するための Python 製 CLI ユーティリティです。

クイックスタート

```powershell
uv sync
uv run python -m photo_mover --src "C:\path\to\source" --dst "D:\path\to\dest" --dry-run
```

CSV 出力（ファイル一覧の事前調査）

移動前にファイルの重複や拡張子・サイズ分布を調査できます。

```bash
# ファイル一覧を CSV で標準出力に出力
uv run python -m photo_mover --src ./photos --csv

# サブディレクトリも再帰的にスキャン
uv run python -m photo_mover --src ./photos --csv --recursive

# SHA256 ハッシュ付きで出力（重複検出用）
uv run python -m photo_mover --src ./photos --csv --recursive --csv-include-hash
```

出力カラム: `filename`, `extension`, `relative_path`, `size_bytes`（`--csv-include-hash` 指定時は `sha256` を追加）

> **注意**: `--csv-include-hash` はファイルごとにハッシュを計算するため、大量ファイルでは処理時間が増加します。

オプションの一覧は `--help` を参照してください。

Issue の報告について

不具合報告や機能要望は、リポジトリの Issue テンプレートを使って提出してください。

- バグ報告: `Bug Report` テンプレートを選び、最低でも次を含めてください — 目的、背景、再現手順、環境、ログ
- 機能要望: `Feature Request` テンプレートを選び、最低でも次を含めてください — 目的、背景、要件、受け入れ基準、補足

報告時は最小限の再現コマンドと出力を含めてください。例：

```powershell
uv run python -m photo_mover --src "C:\path\to\source" --dst "D:\path\to\dest" --dry-run
```

Issue テンプレートは `.github/ISSUE_TEMPLATE` にあります。テンプレートに従って必要事項を記載してください。
