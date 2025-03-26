# Yahoo Taiwan Stock News Scraper

這個爬蟲程式會從台灣 Yahoo 股市新聞頁面擷取前 10 則新聞的標題和內容。

## 功能

- 抓取 https://tw.stock.yahoo.com/news 頁面的前 10 則新聞
- 擷取每篇新聞的標題和摘要
- 點入每篇新聞頁面擷取完整內容
- 將結果儲存為 JSON 檔案

## 需求

- Python 3.6+
- requests
- beautifulsoup4

## 安裝

1. 安裝所需套件：

```
pip install -r requirements.txt
```

## 使用方法

直接執行 Python 腳本：

```
python yahoo_news_scraper.py
```

## 輸出

程式會產生以下輸出：

1. 在終端機顯示已抓取的新聞
2. 建立 `yahoo_news_results.json` 檔案，內含所有抓取的新聞資料

## 注意事項

- 為避免過度頻繁請求，程式會在抓取每篇新聞內容後暫停 1 秒
- 網站結構可能會變更，如發生錯誤，可能需要更新選擇器 