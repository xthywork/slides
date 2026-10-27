# 我的簡報室

集中瀏覽圖像動畫簡報、互動展示與摘要講稿的個人入口。使用原生 HTML／CSS／JavaScript，無須安裝前端套件或編譯框架。

- 公開入口：https://slides.xthy.work/
- 原始碼：https://github.com/xthywork/slides

## 日常使用

搜尋主題、依類別篩選，或把常用簡報加入收藏。簡報會記住這個瀏覽器上次的頁碼，回到入口可接續閱讀。收藏、閱讀進度與下一份簡報的需求草稿存放在自己的瀏覽器，不會上傳 GitHub。

「準備下一份簡報」會整理並複製製作需求，交由助理製作，不會直接呼叫 AI 或自動產生新內容。

目前收錄：

| 簡報 | 內容 | 頁數 |
| --- | --- | --- |
| [Service Harbor](presentations/service-harbor/) | 服務管理的圖像動畫、原版前端展示與摘要講稿 | 13 |
| [Fork Quest](presentations/fork-quest/) | Codex Fork、Git 分支、Worktree 與 GitHub 協作的互動課程 | 6 章 |

Service Harbor 的主機、服務與日誌使用虛構資料；介面不會連接正式系統。

## 本機啟動

需要 Python 3.9 以上，不需額外安裝套件：

```bash
python3 serve.py
```

預設綁定 `0.0.0.0:49183`。用 `http://<這台電腦的區網 IP>:49183/` 開啟入口。可用 `--host` 與 `--port` 改變監聽位置。

舊的 `/notes` 與 `/speaker-notes.md` 會轉向 Service Harbor 的新位置；舊入口的 `#slide-數字` 也會轉到對應簡報。帶有查詢參數的本機網址會轉到不帶參數的網址。

如需以使用者服務常駐：

```bash
python3 scripts/install_user_service.py
systemctl --user status presentation-hub.service
```

這會安裝目前 checkout 的服務並在失敗時重啟。若已用 `python3 serve.py` 手動啟動同一個 Port，請先停止該手動程序。使用者未登入時能否開機啟動，依主機的 linger 設定；此程式不改動登入設定。

## 新增一份簡報

每份簡報有自己的資料夾與永久 slug，更新現有作品時保留原 slug。

```text
presentations/
  service-harbor/
    index.html
    notes.html
    speaker-notes.md
  new-topic/
    index.html
    speaker-notes.md
```

先完成 `presentations/new-topic/index.html`，有講稿時放入同目錄的 `speaker-notes.md`，再執行：

```bash
python3 scripts/register_presentation.py \
  --id new-topic \
  --title '新的簡報主題' \
  --subtitle '一個容易理解的副標題' \
  --description '介紹這份簡報能幫聽眾理解什麼。' \
  --category '主題介紹' \
  --slides 10 \
  --tags '圖像動畫' '新手入門'
```

捲動式課程可加上 `--unit 章`，並以章節數填入 `--slides`；省略時以頁數顯示。

此命令會新增或更新 `presentations.json`、在有 Markdown 講稿時產生 `notes.html`，並在封面不存在時建立 SVG 封面。已有精心設計的封面不會被覆蓋。入口會自動讀取清單中的新項目，無須修改首頁。

只更新講稿時：

```bash
python3 scripts/render_notes.py presentations/new-topic/speaker-notes.md
```

新簡報可在切頁時記錄進度，供入口「接續閱讀」使用：

```javascript
try {
  localStorage.setItem('presentation-hub:progress:new-topic', JSON.stringify({
    slide: currentPage,
    total: pageCount,
    visitedAt: Date.now()
  }));
} catch {}
```

頁碼從 `1` 開始。簡報的 `#slide-N` 必須能直接開啟對應頁；加入返回入口的連結時使用 `../../`，以相容區網與 GitHub Pages 的 repository 子路徑。

## 檔案與維護

- `index.html`：入口外觀、搜尋、篩選、收藏與需求草稿。
- `presentations.json`：簡報清單；只收錄實際完成的內容。
- `presentations/`：簡報與講稿，每份獨立保存。
- `assets/`：SVG 封面與公開資源。
- `serve.py`：本機 HTTP 服務與舊網址導向。
- `scripts/`：登錄簡報與產生靜態講稿的輔助程式。

GitHub Pages 從 `main` 的根目錄發布；`.nojekyll` 保持原始靜態檔案。更新時先在新分支開發，驗證後合併到 `main`，再使用 SSH 推送；GitHub 會更新公開入口。

公開 repository 不應放登入密碼、API key、私人備份、真實主機設定或個資。第三方程式的保留聲明見 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
