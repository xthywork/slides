# Grok Bot：Agent 團隊架構

12 頁固定滿版 SVG 流程圖，依使用者要求省略前置帳號與設定操作。桌機使用橫式圖，手機使用直式圖；主畫面不捲動。

## 檔案

- `index.html`：單檔簡報，內嵌樣式、程式、圖形與資料。
- `notes.html`／`speaker-notes.md`：摘要講稿。
- `slides.json`：可編輯內容與來源資料。
- `sources.md`：來源與查核範圍。
- `grok-bot-slides.pdf`：12 頁 PDF。
- `grok-bot-slides.zip`：這份簡報的離線包。

使用方向鍵或空白鍵翻頁；`O` 目錄、`N` 補充筆記、`F` 全螢幕、`P` 列印。頁碼網址使用 `#slide-N`。左上角返回簡報室，「更多」可開啟講稿與下載檔案。

進度保存在瀏覽器的 `presentation-hub:progress:grok-bot-agent-architecture`，不傳送到伺服器。停用儲存仍可正常翻頁。

修改講稿後，在 repository 根目錄執行：

```bash
python3 scripts/render_notes.py presentations/grok-bot-agent-architecture/speaker-notes.md
```

HTML 的可見圖形與內嵌資料需同步維護；只修改 `slides.json` 不會自動改變已內嵌的 HTML 或 PDF。原始影片與完整字幕不包含在此。
