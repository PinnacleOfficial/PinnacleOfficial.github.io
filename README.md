# 巔峰人工智能金融研究院（Pinnacle AI 金融研究院）網站

這是一套可直接部署至 GitHub Pages 的繁體中文靜態網站，僅使用 HTML、CSS 與原生 JavaScript。

## 部署方式

1. 將本資料夾中的所有檔案上傳至 `PinnacleOfficial.github.io` 儲存庫根目錄。
2. 在儲存庫建立 `images` 資料夾。
3. 把原始圖片以原檔名放入 `images`：`1.png` 至 `13.png`、`LOGO-1.png`、`LOGO.png`。
4. 在 GitHub 儲存庫的 Settings → Pages 中選擇由主要分支根目錄部署。

網站網址：<https://PinnacleOfficial.github.io/>

## 本機預覽

在本資料夾執行：

```bash
python3 -m http.server 8000
```

然後開啟 `http://localhost:8000/`。

## 自动驗收

```bash
python3 tests/validate_site.py
```

驗收會檢查必要頁面、五篇文章字數、20 條 FAQ、SEO 標籤、favicon、圖片引用、站內連結、sitemap 與 robots。

## 聯絡表單說明

本網站為無後端的 GitHub Pages 靜態網站。Contact 頁面的表單只做瀏覽器端欄位驗證，不會上傳或儲存訪客資料。若之後要接收表單，可另行接入經核准的表單服務或官方信箱。
