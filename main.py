import os
import psycopg2
from fastapi import FastAPI, HTTPException

app = FastAPI()
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

# --- DATA SEARCH KARNE KE LIYE ---
@app.get("/search")
async def search_user(username: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT phone_number FROM osint_records WHERE LOWER(username) = LOWER(%s)", (username,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    if result:
        return {"username": username, "phone": result[0]}
    return {"status": "not_found"}

# --- NAYA DATA DAALNE KE LIYE ---
@app.get("/add")
async def add_data(username: str, phone: str):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO osint_records (username, phone_number) VALUES (%s, %s) ON CONFLICT (username) DO UPDATE SET phone_number = EXCLUDED.phone_number", (username, phone))
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success", "message": f"Added {username}"}
    except Exception as e:
        return {"status": "error", "details": str(e)}
