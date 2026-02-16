# 🛠️ 技術選定結果

**決定: Tauri** (2026-02-16)

## スコア比較
| 技術 | 総合スコア |
|------|-----------|
| **Tauri** | **36/40** ← 選定 |
| Electron | 32/40 |
| Web Only | 31/40 |
| PyQt/Flutter | 28/40 |

## 選定理由
- 軽量（Electronの1/10サイズ）
- 透過ウィンドウ・alwaysOnTop 完全対応
- .exe配布可能（非エンジニア向け）
- WebView2ベース（HTML/CSS/JSフロントエンド → Codexのプロトタイプ流用可）
- Rust backendで高パフォーマンス

## セットアップ
```bash
winget install --id Rustlang.Rustup Microsoft.NodeJS
npm create tauri-app@latest
# tauri.conf.json: decorations=false, transparent=true, alwaysOnTop=true
```

## 開発フロー
1. Web Only プロトタイプ (HTML) → ブラウザ確認
2. Tauri wrapper追加 → デスクトップウィジェット化
3. パッケージング → .exe配布
