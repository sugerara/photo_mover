# Project Guidelines

## Code Style
- 構文: Python 3.10+ を想定。
- フォーマット: `black` 相当のスタイル（4スペースインデント、シングルまたはダブルどちらでも可だが一貫すること）。
- リンター: 小さなユーティリティなのでまずは標準ライブラリ中心。重要なスクリプトは `photo_mover/mover.py` を参照。

## Architecture
- 単一コマンドラインユーティリティ。主要モジュール:
  - `photo_mover/mover.py`: ファイル検出と移動の主要ロジック
  - `photo_mover/__main__.py`: CLI エントリポイント（argparse ベース）
- 設計方針: 副作用を最小にし、まず `--dry-run` で結果を確認できること。

## Build and Test
- 推奨手順（ローカル）:
  - 仮想環境作成: `uv venv` (または自動的に作成される)
  - 依存インストール: `uv sync`
  - テスト実行: `uv run pytest -q`
- 自動化: CI では上記と同じコマンドを順に実行してください。

## Project Conventions
- 安全第一: デフォルトで `--dry-run` を推奨。破壊的操作は明示的フラグでのみ実行。
- 対象判定: 拡張子ベース（`jpg`, `jpeg`, `png`, `mp4`, `mov`, `avi` など）。必要があれば `--extensions` で上書き可能。
- 再帰探索: `--recursive` オプションで有効化。

## Integration Points
- ファイルシステム操作のみ。ネットワークや外部 API は使わない想定。
- 大量ファイル処理ではファイルシステムの権限とパフォーマンスに注意。

## Security
- ユーザーのホームやシステム重要ディレクトリを誤って上書きしないよう、移動先の確認を行うこと。
- 実行前に `--dry-run` を推奨。自動実行（CIやスケジューラ）する場合は十分なテストと限定された権限で動かすこと。

## Issues の使い方
- 目的: バグ報告や機能要望、CI/ワークフロー追加などのために Issue を使用してください。
- 背景: Issue には発生状況や前提を明確に記載すると対応が速くなります。
- 要件: バグ報告では再現手順・環境情報を、機能要望では目的・要件・受け入れ基準を必ず記載してください。
- 受け入れ基準: 修正後に再現手順でエラーが発生しないこと、関連テストが追加され CI を通過することを推奨します。
- 補足: `.github/ISSUE_TEMPLATE` のテンプレートを利用してください（`Bug Report` / `Feature Request`）。ラベル付けは `bug` / `enhancement` を想定しています。

---
If anything in these notes is unclear or you want more project-specific rules (naming, packaging, CI), tell me which area to expand.
