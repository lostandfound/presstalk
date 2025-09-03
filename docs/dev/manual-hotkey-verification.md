# 手動ホットキー検証ガイド

本ドキュメントは、グローバル・ホットキー実装の最終動作確認を実機で行うための手順書です。スクリーンリーダー非衝突とWCAG 2.1配慮、複合キー対応、後方互換性、性能面の観点を網羅します。

## 対象
- OS: macOS / Windows / Linux (X11/Wayland)
- 実装: ADR-001 に基づくデフォルト `shift+space` と複合キー対応

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
  - 初回はロゴとともに `Ready for voice input (press shift+space to start)` のログが出力されます。

## 基本動作の確認
1) デフォルト・ホットキー（Shift+Space）
- 前面アプリが何であっても、Shift+Space 押下で `[PT] Recording...` が出力され、離上で `[PT] Finalizing...` が出力されること。

2) コンソールモード比較（参考）
- `uv run presstalk run --console`
- `p` → `[PT] Recording...`、`r` → `[PT] Finalizing...` の挙動が同等であること。

## 複合キーと互換性の確認
- カスタム複合キー（例）
  - `uv run presstalk run --hotkey ctrl+shift+x`
  - `Ctrl`→`Shift`→`X` の順に押下してコンボ成立時に記録が開始し、いずれか離上で終了すること。
- レガシー単一修飾（後方互換）
  - `uv run presstalk run --hotkey ctrl`
  - `Ctrl` 押下で開始・離上で終了すること（従来設定の互換確保）。
- 無効な組み合わせ（エラー）
  - `uv run presstalk run --hotkey ctrl+alt`
  - 起動時に無効なホットキーとしてエラーになること（主キー欠如）。

## モード確認
- トグルモード
  - `uv run presstalk run --mode toggle`
  - `shift+space` 1回押下（押して離す）で開始、再度 1回で終了すること。

## OS別チェックポイント
- macOS
  - システム設定 → プライバシーとセキュリティ → アクセシビリティ/マイク でターミナル（実行シェル）を許可。
  - 主要アプリ（ブラウザ/IDE/エディタ）で Shift+Space が致命的な衝突を起こさないこと（Firefox のスクロール等は軽微で容認）。
- Windows
  - 複数アプリで前面切替しながらもグローバルに検知されること。
  - OS予約ショートカット（Alt+Space等）と衝突しないこと（デフォルトは Shift+Space のため問題なし）。
- Linux
  - X11: グローバル・ホットキーが機能すること。
  - Wayland: セキュリティ設計上、フォーカス外のキーボードフックが制限される場合があります。動作しない場合は X11 セッションで再確認してください。

## 性能・安定性
- 連続短押し（素早い押下/離上）や長押しを繰り返しても取りこぼしや遅延がないこと。
- CPU使用率が過度に増えないこと（アクティビティモニタ/タスクマネージャで確認）。

## トラブルシューティング
- 依存不足: `pynput` が無い場合は `uv pip install pynput`。
- 権限不足（macOS）: アクセシビリティ/マイク権限の付与後、ターミナルを再起動。
- 詳細ログ: `--log-level DEBUG` を付与して動作を追跡。
- 明示的設定: `--config ./presstalk.yaml` でYAMLの有効化を強制。

## レポートテンプレート
- 環境: OS/バージョン/ディスプレイサーバ（X11/Wayland）
- 前面アプリ: アプリ名（複数）
- ホットキー: 使用した組み合わせ（例: `shift+space`, `ctrl+shift+x`）
- 結果: 開始/終了ログの有無、遅延/取りこぼしの有無
- 既知の衝突: 有/無（あればアプリ・機能名）
- ログ抜粋: `[PT] Recording...` / `[PT] Finalizing...` 付近

## 参考
- ADR: `docs/adr/ADR-001-default-hotkey-change.md`
- 分析: `docs/knowledge/report-hotkey.md`
