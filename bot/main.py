import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramNetworkError, TelegramUnauthorizedError

from bot.config.settings import settings
from bot.database.session import init_db
from bot.handlers.user import start, common, subscription, document
from bot.handlers.admin import panel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Polling shu muddatdan uzoq ishlagan bo'lsa, uzilishni "yangi" nosozlik deb
# hisoblaymiz va backoff hisoblagichini noldan boshlaymiz.
HEALTHY_POLL_SECONDS = 120


async def main():
    """Main function to start the bot"""
    
    # Initialize database
    logger.info("Initializing database...")
    await init_db()
    
    # Initialize bot and dispatcher
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    
    # Register handlers
    dp.include_router(start.router)
    dp.include_router(subscription.router)
    dp.include_router(panel.router)
    dp.include_router(document.router)
    dp.include_router(common.router)
    
    try:
        # Tokenni polling'dan OLDIN tekshiramiz. Aks holda yaroqsiz token
        # bilan ham "Bot started successfully!" yozilib, asl sabab faqat
        # 60 soniyalik polling timeout'idan keyin traceback ichida ko'rinardi.
        try:
            me = await bot.get_me()
        except TelegramUnauthorizedError:
            logger.critical(
                "BOT_TOKEN yaroqsiz — Telegram 'Unauthorized' qaytardi. "
                "Token bekor qilingan yoki noto'g'ri ko'chirilgan bo'lishi mumkin. "
                "BotFather'dan amaldagi tokenni oling va .env dagi BOT_TOKEN ni "
                "yangilang. Qayta ishga tushirish bu xatoni TUZATMAYDI."
            )
            # EX_CONFIG (78) — sozlama xatosi. Vaqtinchalik nosozlikdan farqli
            # o'laroq bu holatda qayta urinishning ma'nosi yo'q; systemd unit'ida
            # RestartPreventExitStatus=78 bilan cheksiz restart siklini to'xtatish
            # mumkin (deploy/ hujjatiga qarang).
            return 78

        logger.info("Bot started successfully! (@%s, id=%s)", me.username, me.id)

        # Tarmoq uzilishlarida qayta ulanamiz. Ketma-ket xatoda kutish vaqti
        # oshib boradi — Telegram uzoq muddat yiqilganda log'ni to'ldirmasligi
        # va bejiz so'rov yubormasligi uchun. Polling bir muddat sog'lom
        # ishlagan bo'lsa, kutish vaqti boshlang'ich holatga qaytariladi.
        backoff = 5
        loop = asyncio.get_running_loop()
        while True:
            started_at = loop.time()
            try:
                await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
                break
            except TelegramNetworkError as exc:
                if loop.time() - started_at >= HEALTHY_POLL_SECONDS:
                    backoff = 5
                logger.warning(
                    "Telegram tarmoq xatosi: %s. %s soniyadan keyin qayta ulanamiz...",
                    exc, backoff,
                )
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 300)
    finally:
        await bot.session.close()

    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!")
        exit_code = 0
    sys.exit(exit_code or 0)