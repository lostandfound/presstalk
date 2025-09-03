# 手動検証ガイド（Hotkey / Audio / 基本動作）

本ドキュメントは、実機での最終動作確認に用いる汎用的なチェックリストです。ホットキー、音によるフィードバック、基本的な記録/確定フローを対象とし、アクセシビリティ（スクリーンリーダー非衝突、WCAG配慮）とクロスプラットフォーム性を重視します。

## 対象
- OS: macOS / Windows / Linux (X11/Wayland)
- 実装: ADR-001 に基づくホットキー（デフォルト: `ctrl+space`）と複合キー対応、音フィードバック（ビープ）

## 前提条件
- リポジトリ取得済み
- Python環境: `uv` 利用
- 依存パッケージ: 
  - 実行時: `pynput`（グローバル・ホットキー用）
  - テスト時: 付属ユニットテストのみ（実機検証は本手順）

## セットアップ
- 仮想環境作成とインストール
  - `uv venv && source .venv/bin/activate`
  - `uv pip install -e .`
  - `uv pip install pynput`
- 実行（ローカルモード）
  - `uv run presstalk run`
  - 初回はロゴとともに `Ready for voice input (press <hotkey> to start)` のログが出力されます（既定: `ctrl+space`）。

## 基本動作の確認
1) デフォルト・ホットキー（例: Ctrl+Space）
- 前面アプリが何であっても、ホットキー押下で `[PT] Recording...`、離上で `[PT] Finalizing...` が出力されること。

2) コンソールモード比較（参考）
- `uv run presstalk run --console`
- `p` → `[PT] Recording...`、`r` → `[PT] Finalizing...` の挙動が同等であること。

3) 音フィードバック（ビープ）
- 既定では記録開始/終了時にビープが鳴る（環境により可聴性は異なる）。
- 無効化: `audio_feedback: false` を YAML に設定し、鳴動しないことを確認。

## 複合キーと互換性の確認
- カスタム複合キー（例）
  - `uv run presstalk run --hotkey ctrl+shift+x`
  - 修飾キー＋主キーの同時押下で開始、いずれか離上で終了すること。
- 無効な組み合わせ（エラー）
  - `uv run presstalk run --hotkey ctrl+alt`
  - 起動時に無効（主キー欠如）。修飾キーのみの指定（例: `ctrl`）も無効。

## モード確認
- トグルモード
  - `uv run presstalk run --mode toggle`
  - ホットキー1回（押して離す）で開始、再度1回で終了すること。

## OS別チェックポイント
- macOS
  - システム設定 → プライバシーとセキュリティ → アクセシビリティ/マイク でターミナル（実行シェル）を許可。
  - 既知の競合（入力ソース切替 `ctrl+space`、IDE 補完など）は再割当等で回避可能であることを確認。
- Windows
  - 複数アプリで前面切替しながらもグローバルに検知されること。
  - OS予約ショートカット（Alt+Space 等）と致命的な衝突がないこと。
- Linux
  - X11: グローバル・ホットキーが機能すること。
  - Wayland: セキュリティ設計上、フォーカス外のキーボードフックが制限される場合があります（動作しない場合は X11 セッションで再確認）。

## 性能・安定性
- 連続短押し（素早い押下/離上）や長押しを繰り返しても取りこぼしや遅延がないこと。
- CPU使用率が過度に増えないこと（アクティビティモニタ/タスクマネージャで確認）。

## トラブルシューティング
- 依存不足: `pynput` が無い場合は `uv pip install pynput`。
- 権限不足（macOS）: アクセシビリティ/マイク権限の付与後、ターミナルを再起動。
- 詳細ログ: `--log-level DEBUG` を付与して動作を追跡。
- 明示的設定: `--config ./presstalk.yaml` でYAMLの有効化を強制。
 - ビープが鳴らない: 端末種別/ミュート設定の影響を受ける場合あり。`audio_feedback: true` を確認。

## レポートテンプレート
- 環境: OS/バージョン/ディスプレイサーバ（X11/Wayland）
- 前面アプリ: アプリ名（複数）
- ホットキー: 使用した組み合わせ（例: `ctrl+space`, `ctrl+shift+x`）
- 結果: 開始/終了ログの有無、遅延/取りこぼしの有無
- 既知の衝突: 有/無（あればアプリ・機能名）
- ログ抜粋: `[PT] Recording...` / `[PT] Finalizing...` 付近
 - 音フィードバック: 開始/終了時の鳴動有無、可聴性（環境依存）

## 参考
- ADR: `docs/adr/ADR-001-default-hotkey-change.md`
- 分析: `docs/knowledge/report-hotkey.md`
