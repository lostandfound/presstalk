## PressTalk CLI

言語: [English](README.md) | [日本語](README-ja.md)

ローカル完結のプッシュトゥトーク（PTT）。macOS 向け、常時キャプチャ＋オフライン ASR（faster-whisper）。

- アーキテクチャ: docs/architecture.md
- 使い方（日本語）: docs/usage-ja.md
- 使い方（英語）: docs/usage.md
- コマンド一覧: docs/commands.md
- ロードマップ: docs/ROADMAP.md

## クイックスタート
```bash
uv venv && source .venv/bin/activate
uv pip install -e .

# 動作確認（疑似）
uv run presstalk simulate

# 実行（既定＝グローバルホットキー）
uv run presstalk run
```
Tips:
- 初回は macOS のマイク/アクセシビリティ許可が必要
- 既定ホットキーは `ctrl`。押して録音、離して確定＋貼り付け

## Makefile ショートカット
- `make venv && source .venv/bin/activate && make install`
- `make run` / `make console`
- `make simulate CHUNKS="hello world" DELAY=40`
- `make test` / `make test-file FILE=tests/test_controller.py`
- `make lint` / `make format` / `make typecheck`

## 依存関係
- Python 3.9+（macOS 13+ 推奨）
- 開発ツール: `xcode-select --install`
- `sounddevice` で失敗する場合: `brew install portaudio` → 再インストール
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
