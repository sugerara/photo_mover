# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

photo_mover は、ソースディレクトリから写真・動画ファイルを移動する Python 製 CLI ユーティリティ。CSV 出力モードによるファイル一覧・重複調査機能も備える。パッケージマネージャは **uv**、Python **3.14+** が必要。

## よく使うコマンド

```bash
# 依存関係インストール
uv sync

# テスト実行
uv run pytest -q

# 単一テスト実行
uv run pytest tests/test_mover.py::test_dry_run -q

# リントチェック（black）
uv run black --check photo_mover/ tests/

# コードフォーマット
uv run black photo_mover/ tests/

# CLI 実行
uv run python -m photo_mover --src <パス> --dst <パス> --dry-run
```

## アーキテクチャ

- `photo_mover/__main__.py` — CLI エントリポイント（argparse）。移動モードと `--csv` 出力モードの2つのモードを持つ。
- `photo_mover/mover.py` — コアロジック。`move_media()` がソースディレクトリを走査し、対象拡張子のファイルを移動（または dry-run）する。`is_media()` で拡張子フィルタリング。
- `photo_mover/csv_exporter.py` — `--csv` フラグ使用時の CSV 出力ロジック（`scan_media`, `write_csv`）。
- `main.py` — 未使用のプレースホルダ（実際のエントリポイントではない）。

## 設計方針

- **安全第一**: `move_media()` の `dry_run` パラメータはデフォルト `True`。破壊的操作は明示的フラグでのみ実行。
- **拡張子ベースのフィルタリング**: メディア判定は `DEFAULT_EXTENSIONS`（jpg, jpeg, png, heic, mp4, mov, avi, gif）で定義。`--csv` モードは全ファイル対象（`--extensions` で絞り込み可）。
- **外部依存なし**: ランタイムは標準ライブラリのみ。開発用依存は `black` と `pytest`。

## CI

CI は全 push・全 PR で実行。`lint`（black --check）と `test`（pytest）の2ジョブ構成。Python 3.14 + uv を使用。
