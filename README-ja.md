## PressTalk CLI

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

言語: [English](README.md) | [日本語](README-ja.md)

音声入力ツール（プッシュトゥトーク, PTT）。コントロールキーを押している間だけ録音し、離すと最前面アプリのカーソル位置に文字起こし結果を貼り付けます。すべてローカルで動作します（サーバ不要）。macOS と Windows をサポートします。

- アーキテクチャ: docs/architecture.md
- 使い方（日本語）: docs/usage-ja.md
- 使い方（英語）: docs/usage.md
- コマンド一覧: docs/commands.md
- ロードマップ: docs/ROADMAP.md

## クイックスタート

まずクローン:
```bash
git clone https://github.com/lostandfound/presstalk.git
cd presstalk
```

方法A（推奨・No‑CD 一発セットアップ）:
```bash
make bootstrap
# 以後どこからでも
presstalk
```

方法B（プロジェクト内 venv）:
```bash
uv venv && source .venv/bin/activate
uv pip install -e .
uv run presstalk
```
Tips:
- 初回は macOS のマイク/アクセシビリティ許可が必要です。
- 既定ホットキーは `ctrl`。押して録音、離すとローカルで文字起こししてカーソル位置に貼り付けます。
- 既定でペーストガード有効（Terminal/iTerm には貼り付けを抑止、設定で変更可能）。

## できること（概要）
- どのテキスト入力欄でも、キー押下中のみ録音→キーを離すと貼り付け。
- 既定はグローバルホットキー（`ctrl`）。YAML または CLI で変更可能。
- faster‑whisper によるオフライン ASR。音声は端末外へ送信しません。
- ペーストガードで Terminal/iTerm を回避（YAML で調整可能）。

## Makefile ショートカット
- `make venv && source .venv/bin/activate && make install`
- `make run` / `make console`
- `make simulate CHUNKS="hello world" DELAY=40`
- `make test` / `make test-file FILE=tests/test_controller.py`
- `make lint` / `make format` / `make typecheck`

## リポジトリに移動せずに起動する（No‑CD Setup）
- 一発セットアップ（uv/pipx/venv を自動判別）:
  - `make bootstrap`
  - 以後はどこからでも: `presstalk run`（または `pt` エイリアス）
- グローバルインストール（uv）:
  - `make install-global` 実行後、`~/.local/bin` を PATH に追加（`make path-zsh` か `make path-bash`）
- いま即起動（インストール不要・リポジトリから実行）:
  - `make run-anywhere`

## 依存関係
- Python 3.9+（macOS 13+ または Windows 10/11）
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
hotkey: ctrl     # ctrl/cmd/alt/space または文字キー
paste_guard: true
paste_blocklist:
  - Terminal
  - iTerm2
  - com.apple.Terminal
  - com.googlecode.iterm2
```

ライセンス: MIT（pyproject を参照）

Windows の注意事項やペーストガードの既定値は `docs/usage.md` / `docs/usage-ja.md` を参照してください。
