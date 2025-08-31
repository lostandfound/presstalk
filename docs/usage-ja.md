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
- 自動検出: リポジトリルートの `presstalk.yaml`（editable インストール時）
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
paste_guard: true
paste_blocklist:
  - Terminal
  - iTerm2
  - com.apple.Terminal
  - com.googlecode.iterm2
show_logo: true
```

## 5) 動作確認（ダミー）
実デバイスを使わず、疑似チャンクで流れを確認:
```bash
uv run presstalk simulate --chunks hello world --delay-ms 40
```
期待: `FINAL: bytes=...` が表示されます。

## 6) 実行（ローカルPTT / faster-whisper）
実マイク入力でローカルASRを実行（グローバルホットキー既定）:
```bash
uv run presstalk run
```
- 期待: ホットキー（既定 `ctrl`）を押している間だけ録音、離すと確定→貼り付け。
- `--mode toggle` や `--hotkey cmd` などは YAML または CLI で変更可。
- コンソールモード（代替）:
  - `uv run presstalk run --console`
  - hold: `p` + Enter で開始、`r` + Enter で停止、`q` で終了
  - 注意: 最終化（[PT] Finalizing...）中は終了（q）が無効化されます。

## 7) タスクランナー（Make不要・推奨）
Windows/macOS/Linux 共通で `task.py` を利用できます:
```bash
uv run python task.py install
uv run python task.py test
uv run python task.py simulate --chunks hello world --delay-ms 40
uv run python task.py run          # グローバルホットキー
uv run python task.py run --console
uv run python task.py clean
```

## 8) 推奨設定値
- 言語: `--language ja`
- モデル: `--model small`（既定）
- プリバッファ: `--prebuffer-ms 0..300`（押下直後の欠け対策。0 で無効）
- 最小録音時間: `--min-capture-ms 1800`（短押し対策）

## 9) トラブルシュート
- `sounddevice` エラー: `brew install portaudio` → `uv pip install sounddevice` 再試行
- モデル初回が遅い: 初回ダウンロード/キャッシュのため。2回目以降は高速化。
- 貼り付かない: アクセシビリティ許可、最前面アプリのテキスト入力フォーカスを確認。
- 短すぎて結果が出ない: `--min-capture-ms 2000`、`--prebuffer-ms 200..300` を試す。

## 10) Linux の注意事項
- 推奨パッケージ（Debian/Ubuntu 例）:
```bash
sudo apt-get update && sudo apt-get install -y \
  portaudio19-dev libasound2-dev xclip xdotool
```
- Wayland: クリップボードに `wl-clipboard`（`wl-copy`）を導入。コンポジタ設定によりキー注入が制限される場合は `--console` を利用してください。
```bash
sudo apt-get install -y wl-clipboard
```
- セットアップ自体は macOS/Windows と同様に venv 作成→ `uv pip install -e .` → `simulate`/`run --console`。
- ペーストガードの既定には一般的な Linux ターミナルが含まれます。YAML の `paste_blocklist:` か `PT_PASTE_BLOCKLIST` で上書き可能。

## 11) 環境変数での既定値（任意）
CLI引数の代わりに以下も利用可能（`src/presstalk/config.py`参照）:
- `PT_LANGUAGE`（既定: `ja`）
- `PT_SAMPLE_RATE`（既定: `16000`）
- `PT_CHANNELS`（既定: `1`）
- `PT_PREBUFFER_MS`（既定: `1000`）
- `PT_MIN_CAPTURE_MS`（既定: `1800`）
- `PT_MODEL`（既定: `small`）

## 12) 既知の制限と今後
- グローバルホットキーと貼り付けガードは実装済み（既定で有効）。
- ダイアライゼーションや逐次確定は今後の拡張対象。

---
困ったら `uv run presstalk simulate` の結果とエラーメッセージを共有してください。最小の再現手順からサポートします。

## 13) グローバルホットキー（既定）
- 既定でグローバルホットキーが有効です（`--console` を付けると対話モード）。
- 実行例（Ctrlを押している間だけ録音）:
```bash
uv run presstalk run --mode hold --hotkey ctrl --language ja --model small --prebuffer-ms 200 --min-capture-ms 1800
```
- ホットキー指定例: `ctrl` / `cmd` / `alt` / `space` / 文字キー（例: `a`）
- 注意: macOS ではアクセシビリティ許可が必要です（Terminalを有効に）。

## 14) 貼り付けガード（Terminal/iTerm を避ける）
- 既定で、最前面アプリが Terminal/iTerm の場合は自動貼り付けを抑止します。
- 制御は環境変数で可能:
  - `PT_PASTE_GUARD=1`（既定1=有効、0で無効）
  - `PT_PASTE_BLOCKLIST="Terminal,iTerm2,com.apple.Terminal,com.googlecode.iterm2"`
    - アプリ名/Bundle ID の部分一致で判定（カンマ区切りで追加可能）
  - 既定ブロックリスト（OS別）:
    - macOS: `Terminal,iTerm2,com.apple.Terminal,com.googlecode.iterm2`
    - Windows: `cmd.exe,powershell.exe,pwsh.exe,WindowsTerminal.exe,wt.exe,conhost.exe`
    - Linux: `gnome-terminal,org.gnome.Terminal,konsole,xterm,alacritty,kitty,wezterm,terminator,tilix,xfce4-terminal,lxterminal,io.elementary.terminal`
