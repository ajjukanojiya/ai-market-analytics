# 🔧 PostgreSQL Migration Setup Guide

Aapka project ab **PostgreSQL** use karega MySQL ki jagh. Yeh guide aapko step-by-step poora setup karne mein help karega.

---

## ✅ Kya Change Hua? (What's Changed?)

| Item | Pehle (MySQL) | Ab (PostgreSQL) |
|------|---------------|-----------------|
| Database System | MySQL | PostgreSQL |
| Python Driver | `pymysql` | `psycopg2` |
| Database Port | 3306 | 5432 |
| Default User | `root` | `postgres` |
| All Python Scripts | Updated ✅ | Updated ✅ |
| Laravel Config (.env) | Updated ✅ | Updated ✅ |

---

## 📋 Setup Steps

### Step 1: PostgreSQL Install Kro (Windows)

1. **Download PostgreSQL:**
   - Visit: https://www.postgresql.org/download/windows/
   - Version 15+ recommend kar rahe hain

2. **Installation ke doran:**
   - Default port **5432** rakho
   - Password yaad rakh lo (superuser password)
   - Default user: `postgres`

3. **Installation verify karo:**
   ```powershell
   psql --version
   ```

---

### Step 2: Database Banao

1. **PostgreSQL ke andar open karo:**
   ```powershell
   psql -U postgres
   ```

2. **Database create karo:**
   ```sql
   CREATE DATABASE market_data;
   ```

3. **Database verify karo:**
   ```sql
   \l
   ```
   
4. **Exit karo:**
   ```sql
   \q
   ```

---

### Step 3: Python Packages Install Karo

```powershell
# PostgreSQL driver
pip install psycopg2-binary

# Baki packages jo pehle se hain
pip install pandas yfinance tensorflow scikit-learn joblib feedparser google-genai
```

---

### Step 4: Environment Variables Set Karo

**Agar aapne PostgreSQL ko password diya hai, toh `.env` file update karo:**

```env
DB_HOST=127.0.0.1
DB_PORT=5432
DB_DATABASE=market_data
DB_USERNAME=postgres
DB_PASSWORD=aapka_postgres_password_yahan_likho
DB_CONNECTION=pgsql
```

---

### Step 5: Tables Auto-Create Ho Jayenge

Jab aap script run karange, toh tables automatically ban jayenge:

```powershell
# Stock data fetch karo
python fetch_stock_data.py SBIN.NS

# Model train karo
python train_lstm_model.py SBIN.NS

# Prediction karo
python predict_daily.py SBIN.NS
```

---

## 🚀 Complete Pipeline Chalaao

```powershell
# Ek stock ke liye poora pipeline chalaao
python run_pipeline.py RELIANCE.NS

# Ya sab stocks update karo (agar database mein already hain)
python update_all_stocks.py
```

---

## 🐛 Agar Error Aaye Toh?

### Error: "psycopg2 not found"
```powershell
pip install psycopg2-binary
```

### Error: "Could not connect to server"
- PostgreSQL service chalu hai? Check karo Windows Services mein
- Password sahi hai?
- Port 5432 chalu hai?

### Error: "database market_data does not exist"
```sql
psql -U postgres
CREATE DATABASE market_data;
```

---

## ✨ Fayide (Benefits of PostgreSQL)

1. **Zyada Powerful:** Large datasets ke liye better
2. **Reliable:** Enterprise-grade database
3. **Free & Open Source:** MySQL jaise hi free
4. **Better Performance:** Complex queries mein faster

---

## 📊 Database Structure

```
market_data (Database)
├── historical_stock_data (Table)
│   ├── symbol (VARCHAR)
│   ├── date (DATE)
│   ├── open (DECIMAL)
│   ├── high (DECIMAL)
│   ├── low (DECIMAL)
│   ├── close (DECIMAL)
│   └── volume (BIGINT)
├── stock_predictions (Table)
│   ├── id (SERIAL)
│   ├── symbol (VARCHAR)
│   ├── prediction_for_date (DATE)
│   ├── predicted_price (DECIMAL)
│   ├── actual_price (DECIMAL)
│   └── created_at (TIMESTAMP)
└── news_sentiments (Table)
    ├── id (SERIAL)
    ├── symbol (VARCHAR)
    ├── date (DATE)
    ├── sentiment_score (DECIMAL)
    ├── verdict (VARCHAR)
    ├── summary (TEXT)
    └── created_at (TIMESTAMP)
```

---

## 🎯 Kya Abhi Change Kar Diya Gaya?

✅ `.env` file - PostgreSQL settings ke sath  
✅ `fetch_stock_data.py` - psycopg2 driver ke sath  
✅ `train_lstm_model.py` - PostgreSQL connection ke sath  
✅ `predict_daily.py` - PostgreSQL connection ke sath  
✅ `update_all_stocks.py` - PostgreSQL connection ke sath  
✅ `news_sentiment.py` - PostgreSQL connection ke sath  
✅ `AI_Project_Guide.md` - PostgreSQL references  

---

## ❓ Aur Sawaal?

Agar koi problem ho ya aur questions hon, toh pocho! Pura system abhi setup ready hai. Bas upper wale steps follow karo aur sab thik ho jayega! 🚀
