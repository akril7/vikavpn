import asyncio
from datetime import UTC

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger

from src.settings import TelegramBotSettings
from src.db.connection import Session
from src.db.repo import UserRepository, options


class SubscriptionNotifier:
    """Планировщик уведомлений об истекающих подписках.

    Запускает фоновую задачу по cron-расписанию, которая раз в сутки
    рассылает пользователям напоминание о скором истечении подписки.
    Отправка устойчива к блокировке бота (``TelegramForbiddenError``)
    и rate-limit'ам Telegram (``TelegramRetryAfter``).

    Attributes:
        _bot: Экземпляр aiogram-бота для отправки сообщений.
        _settings: Настройки расписания (час, минута).
        _scheduler: APScheduler с ``AsyncIOScheduler``.
    """

    JOB_ID = "notify_expiring_subscriptions"
    RETRY_ATTEMPTS = 5
    SEND_DELAY = 0.2
    NOTIFICATION_HOURS = 24

    def __init__(self, bot: Bot, settings: TelegramBotSettings) -> None:
        """Создать планировщик уведомлений.

        Args:
            bot: Бот для отправки сообщений.
            settings: Настройки с полями ``expire_notif_hour`` и
                ``expire_notif_minute``.
        """
        self._bot = bot
        self._settings = settings
        self._scheduler = AsyncIOScheduler(timezone=UTC)

    def start(self) -> None:
        """Запустить планировщик и зарегистрировать задачу.

        Идемпотентно: повторный вызов не создаёт вторую задачу
        и не перезапускает уже работающий планировщик.
        """
        self._scheduler.add_job(
            self._notify_expiring_subscriptions,
            trigger=CronTrigger(
                hour=self._settings.expire_notif_hour,
                minute=self._settings.expire_notif_minute,
            ),
            id=self.JOB_ID,
            replace_existing=True,
            misfire_grace_time=3600,
            max_instances=1,
            coalesce=True,
        )

        if not self._scheduler.running:
            self._scheduler.start()
            logger.info(
                "Subscription notifier started (at {:02d}:{:02d} UTC)",
                self._settings.expire_notif_hour,
                self._settings.expire_notif_minute,
            )

    def shutdown(self, wait: bool = False) -> None:
        """Остановить планировщик.

        Args:
            wait: Если ``True`` — дождаться завершения текущих задач.
                По умолчанию ``False`` (мгновенная остановка).
        """
        if self._scheduler.running:
            self._scheduler.shutdown(wait=wait)
            logger.info("Subscription notifier stopped")

    @property
    def running(self) -> bool:
        """Запущен ли планировщик."""
        return self._scheduler.running

    async def notify_now(self) -> None:
        """Разослать уведомления немедленно, вне расписания.

        Полезно при старте приложения, чтобы не ждать ближайшего cron-тика.
        """
        await self._notify_expiring_subscriptions()

    async def _notify_expiring_subscriptions(self) -> None:
        """Разослать напоминания пользователям с истекающей подпиской.

        Выбирает пользователей, у которых подписка истекает в течение
        ближайших ``NOTIFICATION_HOURS`` часов, и отправляет каждому
        сообщение. Пользователи без привязанного Telegram пропускаются.
        """
        async with Session() as session:
            repo = UserRepository(session)
            users = await repo.list_expiring_within(
                hours=self.NOTIFICATION_HOURS,
                options=options.messenger_options(),
            )

        logger.info(
            "Subscription notification: {} users expiring within {}h",
            len(users),
            self.NOTIFICATION_HOURS,
        )

        for user in users:
            telegram_id = user.telegram_id
            if telegram_id is None:
                continue

            await self._send_with_retry(telegram_id)
            await asyncio.sleep(self.SEND_DELAY)

    async def _send_with_retry(self, telegram_id: int) -> None:
        """Отправить уведомление с обработкой ошибок Telegram.

        При ``TelegramRetryAfter`` ждёт указанное время и повторяет
        попытку (до ``RETRY_ATTEMPTS`` раз). При ``TelegramForbiddenError``
        логирует и прекращает попытки для этого пользователя.

        Args:
            telegram_id: Telegram ID получателя.
        """
        text = (
            "⚠️ <b>Ваша подписка истекает завтра!</b>\n\n"
            "Продлите её, чтобы не потерять доступ к сервису."
        )

        for attempt in range(1, self.RETRY_ATTEMPTS + 1):
            try:
                await self._bot.send_message(chat_id=telegram_id, text=text)
                return
            except TelegramForbiddenError:
                logger.info("User {} blocked bot", telegram_id)
                return
            except TelegramRetryAfter as e:
                logger.warning(
                    "Rate limit for {}: retry after {}s (attempt {}/{})",
                    telegram_id,
                    e.retry_after,
                    attempt,
                    self.RETRY_ATTEMPTS,
                )
                await asyncio.sleep(e.retry_after)

        logger.warning(
            "Failed to send notification to {} after {} attempts",
            telegram_id,
            self.RETRY_ATTEMPTS,
        )
