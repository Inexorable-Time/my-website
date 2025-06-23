from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from telegram import Bot
from pydantic import BaseModel
import asyncio
import os

app = FastAPI()

# Mount static files directory to serve HTML
app.mount("/static", StaticFiles(directory="static"), name="static")

# Get bot token and channel ID from environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')

# Pydantic model for request validation
class Message(BaseModel):
    text: str

# Serve the frontend HTML
@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read())

# Endpoint to send message to Telegram
@app.post("/send-message")
async def send_message(message: Message):
    try:
        bot = Bot(token=8135097014:AAHpEGrsDhbwK9-_MSzfz4ojXIvWuEAqZ2A)
        await bot.send_message(chat_id=-1002875532157, text=message.text)
        return {"status": "success", "message": "Message sent to Telegram"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")