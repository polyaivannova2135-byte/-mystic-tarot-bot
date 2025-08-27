# main.py
import os, threading, asyncio
from tarot_bot import app, run_bot   # run_bot = async def из tarot_bot.py

def run_web():
    port = int(os.getenv("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    asyncio.run(run_bot())
