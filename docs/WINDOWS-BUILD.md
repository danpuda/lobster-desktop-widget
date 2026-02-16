# 🖥️ Windows ビルド手順

## 前提条件（Windows側にインストール）

### 1. Rust
```powershell
winget install --id Rustlang.Rustup
```

### 2. Node.js
```powershell
winget install --id OpenJS.NodeJS.LTS
```

### 3. MS C++ Build Tools
Visual Studio Installerから「Desktop development with C++」にチェックしてインストール

### 4. WebView2 Runtime
Windows 10/11ならプリインストール済み。なければ Evergreen Bootstrapper をインストール。

## ビルド手順

### Step 1: WSL → Windows にコピー
```bash
# WSL上で実行
rsync -a --delete /home/yama/lobster-desktop-widget/ /mnt/c/work/lobster-desktop-widget/
```

### Step 2: ビルド（PowerShell）
```powershell
cd C:\work\lobster-desktop-widget
npm install
npx tauri build
```

### Step 3: 成果物
```
src-tauri\target\release\lobster-widget.exe
src-tauri\target\release\bundle\msi\*.msi
src-tauri\target\release\bundle\nsis\*.exe
```

## ⚠️ 注意
- `\\wsl$` パスから直接ビルドすると遅い＆パス問題が出る → **必ずWindows側にコピー**
- MSIが失敗したらVBSCRIPT機能を確認
- `tauri.conf.json` の `transparent: true` + CSS `background: transparent` の両方必要
