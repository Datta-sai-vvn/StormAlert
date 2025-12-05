import os
import smtplib
from email.mime.text import MIMEText
from twilio.rest import Client
from telegram import Bot
import asyncio
from backend.models import SettingsInDB

class NotificationService:
    def __init__(self):
        # Email
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")

        # WhatsApp (Twilio)
        self.twilio_sid = os.getenv("TWILIO_SID")
        self.twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_from = os.getenv("TWILIO_FROM_NUMBER")
        self.twilio_client = None
        if self.twilio_sid and self.twilio_token:
            self.twilio_client = Client(self.twilio_sid, self.twilio_token)

        # Telegram
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_bot = None
        if self.telegram_token:
            self.telegram_bot = Bot(token=self.telegram_token)

    async def send_email(self, to_email: str, subject: str, body: str):
        if not (self.smtp_username and self.smtp_password):
            return
        
        def _send():
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = self.smtp_username
            msg['To'] = to_email

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            print(f"Email sent to {to_email}")

        loop = asyncio.get_running_loop()
        # Wrap in retry
        async def _async_send():
            await loop.run_in_executor(None, _send)
            
        await self._retry(_async_send)

    async def send_whatsapp(self, to_number: str, message: str):
        if not self.twilio_client:
            return
        
        def _send():
            # Ensure 'whatsapp:' prefix
            dest = to_number
            if not dest.startswith("whatsapp:"):
                dest = f"whatsapp:{dest}"

            self.twilio_client.messages.create(
                body=message,
                from_=self.twilio_from,
                to=dest
            )
            print(f"WhatsApp sent to {dest}")

        loop = asyncio.get_running_loop()
        # Wrap in retry
        async def _async_send():
            await loop.run_in_executor(None, _send)
            
        await self._retry(_async_send)

    async def send_telegram(self, chat_id: str, message: str):
        if not self.telegram_bot:
            return
        
        try:
            await self.telegram_bot.send_message(chat_id=chat_id, text=message)
            print(f"Telegram sent to {chat_id}")
        except Exception as e:
            print(f"Failed to send Telegram: {e}")

    async def send_all(self, settings: SettingsInDB, message: str):
        # Check if Redis is available for queuing
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            try:
                import redis
                import json
                r = redis.from_url(redis_url)
                task = {
                    "settings": settings.model_dump(),
                    "message": message
                }
                r.rpush("notifications", json.dumps(task))
                print(f"Enqueued notification for {settings.user_id}")
                return
            except Exception as e:
                print(f"Redis enqueue failed: {e}. Falling back to direct send.")

        # Direct Send (Fallback or Dev Mode)
        tasks = []
        if settings.email_enabled and settings.email_address:
            tasks.append(self.send_email(settings.email_address, "StormAlert Notification", message))
        
        if settings.whatsapp_enabled and settings.whatsapp_number:
            tasks.append(self.send_whatsapp(settings.whatsapp_number, message))
            
        if settings.telegram_enabled and settings.telegram_chat_id:
            tasks.append(self.send_telegram(settings.telegram_chat_id, message))
            
        if tasks:
            await asyncio.gather(*tasks)

    async def _retry(self, func, *args, retries=3, delay=1):
        """Helper to retry async functions"""
        for attempt in range(retries):
            try:
                await func(*args)
                return
            except Exception as e:
                if attempt == retries - 1:
                    print(f"Failed after {retries} attempts: {e}")
                else:
                    print(f"Attempt {attempt+1} failed, retrying in {delay}s...")
                    await asyncio.sleep(delay)
                    delay *= 2 # Exponential backoff

notification_service = NotificationService()
