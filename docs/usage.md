# PressTalk 利用手順（完全ローカル / uv優先）

本書は PressTalk（押している間だけ録音→離して確定→最前面アプリに貼り付け）を uv ベースでローカル実行する手順です。WhisperLiveKit は不要です。

## 前提条件
- macOS 13+ 推奨（Apple Silicon / Intel）
- Python 3.9+（3.10+推奨）
- Command Line Tools（`xcode-select --install` 済み）
- uv が使えること（未導入なら https://docs.astral.sh/uv/ を参照）

## 1) 仮想環境（uv）
```bash
uv venv
source .venv/bin/activate
```

## 2) 依存のインストール（uv）
```bash
uv pip install -e .
```
- macOSで`sounddevice`が失敗する場合は PortAudio を先に:
```bash
brew install portaudio
```
その後、依存インストールを再実行してください。

## 3) 権限（macOS）
- マイク: 初回録音開始時に許可ダイアログ。拒否した場合は、システム設定 → プライバシーとセキュリティ → マイク で Terminal を許可。
- アクセシビリティ（貼り付け用）: システム設定 → プライバシーとセキュリティ → アクセシビリティ で Terminal を有効化。

## 4) 設定（YAML）
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
mode: hold
hotkey: ctrl
```

## 4) 動作確認（ダミー）
実デバイスを使わず、疑似チャンクで流れを確認:
```bash
uv run presstalk simulate --chunks hello world --delay-ms 40
```
期待: `FINAL: bytes=...` が表示されます。

## 5) 実行（ローカルPTT / faster-whisper）
実マイク入力でローカルASRを実行:
```bash
uv run presstalk run --mode hold --language ja --model small --prebuffer-ms 200 --min-capture-ms 1800
```
- 操作（コンソール内の簡易操作）:
  - hold: `p` + Enter で開始、`r` + Enter で停止、`q` で終了
  - toggle（`--mode toggle`）: `t` + Enter で開始/停止を切替、`q` で終了
- 期待: 停止後に数秒で最前面アプリへ貼り付け（Terminal を前面にしていると Terminal に貼り付きます）。
  - 注意: 最終化（[PT] Finalizing...）中は終了（q）が無効化されます。貼り付け完了までお待ちください。

## 6) 推奨設定値
- 言語: `--language ja`
- モデル: `--model small`（既定）
- プリバッファ: `--prebuffer-ms 0..300`（押下直後の欠け対策。0 で無効）
- 最小録音時間: `--min-capture-ms 1800`（短押し対策）

## 7) トラブルシュート
- `sounddevice` エラー: `brew install portaudio` → `uv pip install sounddevice` 再試行
- モデル初回が遅い: 初回ダウンロード/キャッシュのため。2回目以降は高速化。
- 貼り付かない: アクセシビリティ許可、最前面アプリのテキスト入力フォーカスを確認。
- 短すぎて結果が出ない: `--min-capture-ms 2000`、`--prebuffer-ms 200..300` を試す。

## 8) 環境変数での既定値（任意）
CLI引数の代わりに以下も利用可能（`src/presstalk/config.py`参照）:
- `PT_LANGUAGE`（既定: `ja`）
- `PT_SAMPLE_RATE`（既定: `16000`）
- `PT_CHANNELS`（既定: `1`）
- `PT_PREBUFFER_MS`（既定: `1000`）
- `PT_MIN_CAPTURE_MS`（既定: `1800`）
- `PT_MODEL`（既定: `small`）

## 9) 既知の制限と今後
- 現在はコンソール操作の簡易PTT。今後、グローバルホットキー（pynput）と貼り付けガード（Terminal/iTerm抑止）を追加予定。
- ダイアライゼーションや逐次確定は今後の拡張対象。

---
困ったら `uv run presstalk simulate` の結果とエラーメッセージを共有してください。最小の再現手順からサポートします。

## 10) グローバルホットキー（既定）
- 既定でグローバルホットキーが有効です（`--console` を付けると対話モード）。
- 実行例（Ctrlを押している間だけ録音）:
```bash
uv run presstalk run --mode hold --hotkey ctrl --language ja --model small --prebuffer-ms 200 --min-capture-ms 1800
```
- ホットキー指定例: `ctrl` / `cmd` / `alt` / `space` / 文字キー（例: `a`）
- 注意: macOS ではアクセシビリティ許可が必要です（Terminalを有効に）。

## 11) 貼り付けガード（Terminal/iTerm を避ける）
- 既定で、最前面アプリが Terminal/iTerm の場合は自動貼り付けを抑止します。
- 制御は環境変数で可能:
  - `PT_PASTE_GUARD=1`（既定1=有効、0で無効）
  - `PT_PASTE_BLOCKLIST="Terminal,iTerm2,com.apple.Terminal,com.googlecode.iterm2"`
    - アプリ名/Bundle ID の部分一致で判定（カンマ区切りで追加可能）
