import asyncio
import logging
from dotenv import load_dotenv
from os import getenv
from aiogram import Bot, Dispatcher
from src.infrastructure.database.main import init_db
from src.bot.handlers import cleaner, admin, welcome
from src.core.services.broadcast import BroadcastService

# Load environment variables
load_dotenv()

async def main():
    log_level = getenv("LOG_LEVEL", "INFO")
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)
    
    token = getenv("BOT_TOKEN")
    if not token:
        logger.error("BOT_TOKEN is not set")
        return

    # Init DB
    await init_db()
    
    bot = Bot(token=token)
    dp = Dispatcher()
    
    # Register routers
    dp.include_router(admin.router)
    dp.include_router(welcome.router)
    dp.include_router(cleaner.router)
    
    logger.info("Starting bot...")
    
    broadcast_service = BroadcastService(bot)
    await broadcast_service.start()
    
    try:
        await dp.start_polling(bot)
    finally:
        await broadcast_service.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped")
