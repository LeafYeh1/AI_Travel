# 旅行安排機器人
這是一款基於人工智慧的旅行助手，透過 Telegram 平台提供即時互動的旅行規劃服務。
使用者可以通過與 AI 聊天，簡單地輸入旅遊地點、天數與個人偏好，AI 便會根據需求生成詳細且個性化的旅行行程。

## 功能介紹
指令列表 :
/start or /help：顯示使用說明 
/travel：可以選擇縣市地點、天數以及特別的需求 
/map：會提示如何數入地點，並且給予靜態地圖以及時間

## 安裝與設定
請確認已安裝以下工具： Python 3.8 以上版本 Poetry 依賴管理工具 poetry install(即可安裝所有套件)
你需要擁有自己的tg bot api 、 gemini api 、 mapbox api
export AI_API_KEY="Your gemini api key"