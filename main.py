import os
import psycopg2
from fastapi import FastAPI, HTTPException

app = FastAPI()

# Render automatic ye URL provide karega
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

@app.on_event("startup")
def setup_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS osint_records (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            phone_number TEXT NOT NULL
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()

@app.get("/")
def home():
    return {"message": "User-to-Number API is Live on Render!"}

@app.get("/search")
async def search_user(username: str):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT phone_number FROM osint_records WHERE LOWER(username) = LOWER(%s)", (username,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        if result:
            return {"username": username, "phone": result[0]}
        return {"status": "error", "message": "User not found"}
    except Exception as e:
        return {"error": str(e)}
