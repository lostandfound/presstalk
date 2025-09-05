## PressTalk CLI

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

言語: [English](README.md) | [日本語](README-ja.md)

音声入力ツール（プッシュトゥトーク, PTT）。コントロールキーを押している間だけ録音し、離すと最前面アプリのカーソル位置に文字起こし結果を貼り付けます。すべてローカルで動作します（サーバ不要）。macOS / Windows / Linux をサポートします。

- アーキテクチャ: docs/architecture.md
- 使い方（日本語）: docs/usage-ja.md
- 使い方（英語）: docs/usage.md
- コマンド一覧: docs/commands.md
- ロードマップ: docs/ROADMAP.md

## クイックスタート

方法A（一発・グローバル推奨）
```bash
uv run python task.py bootstrap
# 以後どこからでも
presstalk
```

方法B（ローカル開発・プロジェクト venv）
```bash
uv venv && source .venv/bin/activate
uv pip install -e .
# 実行（グローバルホットキー）/ コンソールモード
uv run presstalk
uv run presstalk --console
```
Tips:
- 初回は macOS のマイク/アクセシビリティ許可が必要です。
- 既定ホットキーは `ctrl+space`。押して録音、離すとローカルで貼り付け。

## できること（概要）
- どのテキスト入力欄でも、キー押下中のみ録音→キーを離すと貼り付け。
- 既定はグローバルホットキー（`ctrl+space`）。YAML または CLI で変更可能。
- faster‑whisper によるオフライン ASR。音声は端末外へ送信しません。
- ペーストガードで Terminal/iTerm を回避（YAML で調整可能）。

## タスク実行（クロスプラットフォーム）
共通のワークフローは task.py を使います:
- インストール: `uv run python task.py install`
- テスト: `uv run python task.py test`
- シミュレーション: `uv run python task.py simulate --chunks hello world --delay-ms 40`
- 実行: `uv run python task.py run`（または `--console`）

Unix 環境では Makefile のラッパーもありますが任意です。詳細は docs 参照。

## ドキュメント
- 使い方（英語）: docs/usage.md（Windows/macOS/Linux の注意・YAML・Makefile ラッパー）
- 使い方（日本語）: docs/usage-ja.md
- コマンド一覧: docs/commands.md

## 依存関係
- Python 3.9+（macOS 13+ / Windows 10/11 / Linux）
- 開発ツール（macOS）: `xcode-select --install`
- オーディオ（macOSで `sounddevice` が失敗する場合）: `brew install portaudio` → 再インストール
- 権限: macOS はマイク+アクセシビリティ、Windows は前面アプリのテキスト入力フォーカスが必要
- 注意: Docker 実行は非対応（マイク/ホットキー/貼り付けの制約）

## 設定（YAML）
- 自動検出: `./presstalk.yaml`、`$XDG_CONFIG_HOME/presstalk/config.yaml`、`~/.presstalk.yaml`
- 明示指定: `uv run presstalk run --config path/to/config.yaml`
- 例:
```yaml
language: ja
model: small
sample_rate: 16000
channels: 1
prebuffer_ms: 200
min_capture_ms: 1800
mode: hold       # hold または toggle
hotkey: ctrl+space     # 例: ctrl+space, cmd+space, ctrl+shift+x
```

### マイグレーション通知（v1.0.0）

- 既定ホットキーを `ctrl` から `ctrl+space` に変更しました（アクセシビリティとスクリーンリーダーとの競合回避のため）。
- 手順は docs/MIGRATION_v1.0.0.md を参照してください。
paste_guard: true
paste_blocklist:
  - Terminal
  - iTerm2
  - com.apple.Terminal
  - com.googlecode.iterm2
```

ライセンス: MIT（pyproject を参照）

Windows/Linux の注意事項やペーストガードの既定値は `docs/usage.md` / `docs/usage-ja.md` を参照してください。
