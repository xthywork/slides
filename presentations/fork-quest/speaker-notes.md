# Fork Quest｜Codex × Git 互動學院

簡易摘要講稿。這份作品採用捲動式互動課程，共六章；入口的頁碼對應章節。

## 1. 課程導覽：想法與程式碼都可以分岔

今天要分清楚四個容易混淆的名字：Codex Fork、Git Branch、Worktree、GitHub Fork。先記住：它們各自處理不同的對象，不會互相自動完成。

- 操作：按「開始互動學習」，進入核心概念。

## 2. 四種機制：到底分開了什麼？

Codex Fork 分開對話；Git Branch 分開版本路線；Worktree 提供另一個工作資料夾，並共享 Git 歷史；GitHub Fork 則是在自己的帳號建立一份遠端專案。

- 操作：逐一切換四個頁籤，對照圖解、影響範圍與指令。
- 提醒：分岔對話不代表檔案已經隔離，獨立工作資料夾才是 Worktree 的用途。

## 3. 對話分岔：同一個問題，試兩個方案

先討論登入需求，再把對話分成帳號密碼與 Email Magic Link 兩條路。兩條對話沿用共同歷史，後續各自發展，方便比較做法。

- 操作：切換方案 A 與方案 B，觀察共同內容和後續差異。

## 4. Git 分支：讓修改有自己的路線

從 main 建立 feature/login，完成修改並 commit，再合併回 main。示範中 main 沒有另外前進，所以可以快轉合併；合併的是程式碼版本，不是聊天紀錄。

- 操作：按「下一步」走完四個狀態，觀察分支標籤與 commit 的位置。

## 5. 實戰情境：依需求選工具

只是比較想法，可以先分岔對話；同時修改兩種版本，需要考慮分支和 Worktree；參與他人的 GitHub 專案，則依權限採用 Fork 與 Pull Request。

- 操作：切換情境卡片，對照建議組合與示範指令。

## 6. Worktree × GitHub：把本機修改送去協作

先確認 origin 與 upstream，再建立 Worktree。接著可以留在 Worktree 建分支、提交、推送，也可以 Handoff 回 Local 後完成這些步驟。最後在 GitHub 提出 PR，合併後再回本機同步 main。

- 操作：切換 Worktree／Handoff 路線，以及自己的 Repo／GitHub Fork，點選流程節點查看說明。
- 提醒：Handoff 不等於 Push；Push 不等於 Merge；GitHub 合併後，本機 main 仍要更新。
- 收尾：確認修改已保存，再決定是否清理 Worktree。頁面上的指令為教學範例，互動本身不會修改實際 Git 專案。
