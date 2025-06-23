from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from telegram import Bot
from pydantic import BaseModel
import asyncio
import os
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from spl.token.async_client import AsyncToken
from fastapi import Request

app = FastAPI()

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Telegram bot setup
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')

# Solana setup
SOLANA_RPC_URL = os.getenv('SOLANA_RPC_URL')
TOKEN_MINT_ADDRESS = 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'  # USDC
MIN_TOKENS = 2000000000000  # 2 million USDC (6 decimals)

async def get_token_balance(wallet_address: str):
    async with AsyncClient(SOLANA_RPC_URL) as client:
        try:
            token_mint = Pubkey.from_string(TOKEN_MINT_ADDRESS)
            wallet_pubkey = Pubkey.from_string(wallet_address)
            token_account = await AsyncToken.get_associated_token_address(wallet_pubkey, token_mint)
            account_info = await AsyncToken.get_account(client, token_account)
            return account_info.amount
        except Exception:
            return 0  # No token account found

class Message(BaseModel):
    text: str

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.post("/send-message")
async def send_message(message: Message, request: Request):
    try:
        # Get user wallet address from headers
        user_address = request.headers.get('X-User-Address')
        if not user_address:
            raise HTTPException(status_code=400, detail="No wallet address provided")

        # Verify token balance
        balance = await get_token_balance(user_address)
        if balance < MIN_TOKENS:
            raise HTTPException(status_code=403, detail="Insufficient token balance")

        # Send Telegram message
        bot = Bot(token=BOT_TOKEN)
        await bot.send_message(chat_id=CHANNEL_ID, text=message.text)
        return {"status": "success", "message": "Message sent to Telegram"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")
