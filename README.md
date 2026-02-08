# photo_mover

photo_mover は、ソースツリーから指定したディレクトリへ写真・動画ファイルを移動するための Python 製 CLI ユーティリティです。

クイックスタート

```powershell
uv sync
uv run python -m photo_mover --src "C:\path\to\source" --dst "D:\path\to\dest" --dry-run
```

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
