# PressTalk 設計書（完全ローカル PTT） — Archived

この文書は初期設計の記録として保存しています。最新の構成と仕様は以下を参照してください。

- Architecture Overview: `docs/architecture.md`
- Roadmap: `docs/ROADMAP.md`
- Usage Guide: `docs/usage.md`
- Command Reference: `docs/commands.md`

本書は、WhisperLiveKit を使わずに「押している間だけ録音 → 離したら確定 → 前面アプリに貼り付け」を完全ローカルで実現する Push‑to‑Talk（以下 PTT）ツール「PressTalk」の設計を示す。

## ゴール / 非ゴール
- ゴール
  - フォーカス不要のグローバル PTT（押下中のみ録音／トグルも選択可）
  - 冒頭欠け無し（常時キャプチャ＋事前バッファ）
  - 停止時の取りこぼし無し（フラッシュ順序の厳守）
  - 完全ローカル ASR（ネットワーク不要）
  - 最前面アプリへ自動貼り付け（安全ガード付き）
- 非ゴール
  - 多人数同時利用、分散スケール
  - 高度なダイアライゼーション／翻訳 UI（将来拡張）

## 想定環境
- 最優先: macOS 13+（Apple Silicon/Intel）
- Python 3.10+（ASR に `faster-whisper` を使用）
- オプション: GPU/MPS があれば高速化

## 全体アーキテクチャ

```
[Global Hotkey] ──> [PTT Controller] ──> (press) start capture
                                  │
                                  ├─> [Capture (hold-to-talk)] ─ PCM(16k/mono/s16) ─┐
                                  │                                                 │
                                  ├─> [Ring Buffer (PREBUFFER_MS)] (任意: 直近のみ) <┘
                                  │
                                  ├─> [ASR Engine] (faster-whisper)  ← PCM push (prebuffer + live)
                                  │
                                  └─> (release) stop capture ─ finalize → [Final Text] → [Paste Guard] → Cmd+V
```

### モジュール構成（MVP）
- `hotkey.py`: グローバルキーの押下/解放検知（`pynput`）。長押しPTT/トグル両方に対応。
- `capture.py`: 押下中のみマイク取り込み（CoreAudio/sounddevice）。16kHz/mono/s16 をコールバックで供給。
- `ring_buffer.py`: 事前バッファ（例: 700〜1200ms）をバイト列で保持。
- `engine/faster_whisper_engine.py`: ASR 本体。モデル常駐、逐次/バッチ処理を提供。
- `controller.py`: PTT 状態機械。押下で prebuffer + live をエンジンに push、解放で finalize。
- `paste_macos.py`: クリップボード一時置換 → Cmd+V（アクセシビリティ許可前提）。Terminal への誤貼り防止ガード。
- `config.py`: 環境変数/YAML 読み込み、チューニング値（PREBUFFER_MS, MIN_CAPTURE_MS など）。
- `cli.py`: 起動・ログ・例外処理・ヘルスチェック。

### データフロー詳細
1) アイドル時はキャプチャ停止。
2) 押下（press）:
   - `controller` が新セッションを開始。
   - 直前の短いリング（任意/設定）を prebuffer として先頭投入（有効時）。
   - すぐにキャプチャ開始し、ライブPCMを小チャンクで ASR へ push。
3) 解放（release）:
   - キャプチャ停止 / live push を停止。
   - `engine.finalize()` を呼び最終文を確定（必要なら簡易ポストプロセス）。
   - `paste_macos` へテキストを渡す（前面アプリガード適用）。

## インタフェース設計（内部 API）

### Capture → RingBuffer
```python
class RingBuffer:
    def write(self, pcm_bytes: bytes) -> None: ...
    def snapshot_tail(self, n_bytes: int) -> bytes: ...
    def size(self) -> int: ...
    def capacity(self) -> int: ...
```

### Controller → Engine
```python
class AsrEngine:
    def start_session(self, language: str = 'ja') -> str: ...  # returns session_id
    def push_audio(self, session_id: str, pcm_bytes: bytes) -> None: ...
    def finalize(self, session_id: str, timeout_s: float = 10.0) -> str: ...  # returns final text
    def close_session(self, session_id: str) -> None: ...
```

### Controller（状態機械）
```text
Idle → Pressing → Streaming → Releasing → Finalizing → Pasting → Idle

- Pressing: prebuffer push を直ちに実施。MIN_CAPTURE_MS を満たすまで Releasing へ遷移させない。
- Releasing: live push を停止し engine.finalize() を待つ（タイムアウト時は手持ちの仮文で代替）。
```

## 推論エンジン（完全ローカル）

### 候補
- faster-whisper（推奨）
  - 長所: 高速・高精度、Python で扱いやすい、GPU/MPS 対応。
  - モデル: `small`（日本語混在向け）/`base`/`tiny`。初期ロードを起動時に済ませる。
- whisper.cpp
  - 長所: 軽量・C/C++・Metal 対応。
  - 短所: Python 連携の容易さは faster-whisper に劣る。

### ストリーミング方針
- MVP（安定優先）
  - 擬似ストリーミング: MIN_CAPTURE_MS を確保しつつ、押下中も一定サイズ蓄積で部分推論を許可（UI/ログ用）。
  - 解放時に最終一括推論（flush 位置は VAD か固定オーバーラップ）。
- 将来（低遅延）
  - トークン差分確定・バッファテキスト（buffer_transcription）を導入し、逐次確定に寄せる。

## 音声キャプチャ
- macOS: `sounddevice`（CoreAudio）で 16,000Hz/mono/s16 を直接取得（ffmpeg 依存回避）。
- チャンク: 20〜40ms（例: 320〜640サンプル）でコールバック。
- 事前バッファ（任意）: `PREBUFFER_MS = 0..1200`（0 にすれば prebuffer 無効に）。
- 無音対策: 短発話では VAD を切り、`MIN_CAPTURE_MS = 1500..2000` で結果を安定化。

## 貼り付け（macOS）
- 方式: クリップボード一時上書き → `Cmd+V` 送出 → クリップボード復元。
- 実装: `osascript` 経由 or `pynput`/`pyobjc`。
- ガード: 最前面アプリが `Terminal`/`iTerm` ならスキップ（設定で無効化可）。

## 設定（例）
```yaml
language: ja
model: small
prebuffer_ms: 1000
min_capture_ms: 1800
ready_timeout_s: 10
hotkey_mode: hold   # hold or toggle
hotkey_key: ctrl    # ctrl/cmd/alt or combination (toggle 用)
paste_guard: true
```

## ロギング / 診断
- 送出 PCM バイト数、推論レイテンシ、finalize 所要時間、無音長、ドロップ有無。
- エラーログ: デバイス切断、権限不足、モデル未ロード、タイムアウト。

## セキュリティ / プライバシ
- 音声・テキストは端末外へ送信しない。
- ログには内容を含めない。サイズ/時刻のみ。

## 失敗モードと対策
- 冒頭欠け: 常時キャプチャ＋PREBUFFER_MS で解消。
- 停止取りこぼし: finalize 前に push を完全停止し、エンジン側で flush 位置を制御。
- 短すぎる発話: MIN_CAPTURE_MS を下限に設ける。
- 過負荷: バッファが閾値超過で警告。モデルサイズ変更ガイダンスを表示。

## ディレクトリ構成（提案）
```
presstalk/
  docs/
    design.md
  src/
    presstalk/
      __init__.py
      cli.py            # エントリポイント
      config.py
      controller.py
      hotkey.py
      capture.py
      ring_buffer.py
      paste_macos.py
      engine/
        __init__.py
        faster_whisper_engine.py
  pyproject.toml        # 最小依存（sounddevice, pynput, faster-whisper など）
  README.md
```

## 開発ロードマップ
1) MVP（バッチ確定型、安定最優先）
   - 常時キャプチャ＋リング／押下→prebuffer＋live push→解放→一括推論→貼付
   - 設定・ログ・権限確認（マイク/アクセシビリティ）
2) 低遅延化
   - 部分推論・トークン差分確定・短発話向け調整
3) 拡張
   - ダイアライゼーション、翻訳、GUI 設定、アプリ別プロファイル

## 主要チューニング値（初期推奨）
- `PREBUFFER_MS = 0..300`（押下直後の欠けを最小限に。常時キャプチャを使わない前提）
- `MIN_CAPTURE_MS = 1800`
- `language = ja`, `model = small`
- `hotkey_mode = hold`（慣れ次第 toggle も選択可）

---
（以降は当初の設計内容のため、現状と差異がある場合があります）
