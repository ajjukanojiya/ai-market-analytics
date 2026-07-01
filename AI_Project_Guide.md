# 📈 AI Stock Predictor - Aasaan Hinglish Guide

Yeh guide isliye banayi gayi hai taaki project khatam hone ke baad bhi aap aasaani se samajh sakein ki system kaise kaam karta hai aur isme changes kaise karne hain. Hum is guide ko project ke sath-sath update karte rahenge.

---

## 🛠️ 1. Abhi tak humne kya banaya hai? (The Core Engine)
Humara system filhal 3 main scripts par chalta hai:

1. **`fetch_stock_data.py` (Data Collector):** Yeh script internet (Yahoo Finance) se kisi bhi stock ka pichla 5 saal ka data download karti hai aur aapke local PostgreSQL database (`historical_stock_data` table) mein safe rakh deti hai.
2. **`train_lstm_model.py` (The AI Brain):** Yeh script database se data uthati hai, usme patterns dhundhti hai, aur ek AI model (LSTM) ko train karti hai. Train hone ke baad yeh apna "dimaag" ek file (`stock_lstm_model.keras`) mein save kar deti hai.
3. **`predict_daily.py` (The Fortune Teller):** Yeh script us trained dimaag ka use karke kal ka price predict karti hai aur prediction ko `stock_predictions` table mein save kar deti hai.

---

## 🔄 2. Isey "Dynamic" kaise banayein? (Kisi bhi stock par nazar rakhne ke liye)
Abhi humari scripts me `SYMBOL = 'SBIN.NS'` fix (hardcoded) likha hua hai. Isey dynamic banane ka humara plan yeh hai:

**Dashboard UI (Humara Final Goal):** 
Hum hardcoding ko puri tarah hata denge. Hum ek khubsurat **Web Dashboard** banayenge. 
* Wahan ek **Search Box** hoga. 
* Agar aap wahan `RELIANCE.NS` type karke "Analyze" dabayenge, toh Dashboard backend mein automatically in teeno scripts ko call karega. 
* Aapko code open karne ki zaroorat hi nahi padegi. Saara kaam browser mein ek button dabane se hoga!

*Technical Note (Agar bina Dashboard ke dynamic karna ho):* Hum code me thoda change karke isey aisa bana sakte hain ki aap terminal se hi command de sakein, jaise: `python predict_daily.py RELIANCE.NS`. Lekin Dashboard wala tarika sabse asaan aur professional hai.

---

## 🧠 3. Important baatein jo yaad rakhni hain
* **Har Stock ka Dimaag Alag Hota Hai:** SBI ke data se train hua model (dimaag) Reliance ka price sahi nahi bata sakta. Agar aapko naya stock track karna hai, toh pehle us naye stock ka data fetch karna hoga aur naya model train karna hoga. (Fikar mat kijiye, yeh saara lamba kaam hum Dashboard me automate kar denge taaki ek click me ho jaye!)
* **Data Scaling:** AI ko data 0 aur 1 ke beech me chahiye hota hai. Prediction karte waqt humein wahi purana data chahiye hota hai taaki scale same rahe (jaisa `predict_daily.py` me kiya gaya hai).

---
*Yeh guide humare safar ke sath aur detail hoti jayegi!*
