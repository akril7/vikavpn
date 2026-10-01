START_NOT_AUTHORIZED = (
    "👋 Добро пожаловать!\n\n"
    "Похоже, вы здесь впервые. Авторизуйтесь по ссылке, "
    "которую вам выдал администратор, или зарегистрируйтесь."
)

BTN_AUTH_BY_LINK = "🔗 Авторизоваться по ссылке"
BTN_REGISTER = "🆕 Регистрация"

AUTH_ASK_LINK = (
    "Пришлите ссылку, которую вы получили ранее "
    "(Clash-подписка или Telegram-прокси)."
)

AUTH_SUCCESS = "✅ Вы успешно авторизованы!"
AUTH_USER_NOT_FOUND = "❌ Пользователь не найден."
AUTH_ALREADY_BOUND = "❌ Этот аккаунт уже привязан к другому пользователю."

REGISTER_CHOOSE_PLATFORM = (
    "📱 У вас iOS?\n\n"
    "Это влияет на формат конфигурации подписки."
)
BTN_PLATFORM_IOS = "Да, iOS"
BTN_PLATFORM_OTHER = "Нет, Android/ПК/другое"

REGISTER_SUCCESS = (
    "✅ Вы зарегистрированы!\n\n"
    "🎁 Пробный период: 5 дней (VPN + TG Proxy)\n\n"
)

BTN_PROFILE = "👤 Профиль"
BTN_RENEW = "💳 Продлить"
BTN_HELP = "❓ Помощь"
BTN_BACK = "⬅️ Назад"

PROFILE_HEADER = "👤 Профиль"
PROFILE_BODY = (
    "📊 Статус: {status}, до {expires_at}"
)

STATUS_ACTIVE = "активна ({days} дн.)"
STATUS_EXPIRED = "истекла"

RENEW_CHOOSE_MODE = "Выберите, кому продлить:"
BTN_RENEW_SELF = "Продлить себе"
BTN_RENEW_SELF_AND_MANAGED = "Продлить себе и своим"
BTN_RENEW_OTHER = "Продлить другому"

RENEW_CHOOSE_TARIFF = "Выберите тариф:"
BTN_TARIFF_PROXY = "TG Proxy — {price} ₽"
BTN_TARIFF_FULL = "VPN + TG Proxy — {price} ₽"

RENEW_CHOOSE_DAYS = "Выберите срок:"
BTN_DAYS = "{days} дней — {price} ₽"

RENEW_CHOOSE_TARGET = "Выберите пользователя:"

PAYMENT_CREATED = (
    "💳 Платёж создан на сумму {amount} ₽\n\n"
    "Оплатите по ссылке ниже, после чего нажмите «Проверить оплату»."
)
BTN_PAY = "Оплатить"
BTN_CHECK_PAYMENT = "🔄 Проверить оплату"

BTN_COPY_CLASH_LINK = "Скопировать ссылку VPN"
BTN_CONNECT_PROXY = "Подключиться к прокси"

PAYMENT_NOT_FOUND = "❌ Платёж не найден."
PAYMENT_NOT_PAID = "⏳ Оплата ещё не поступила. Попробуйте позже."
PAYMENT_PAID = (
    "✅ Оплата подтверждена!\n"
    "Подписка продлена до {expires_at}."
)

RENEW_PROXY_BLOCKED_BY_VPN = (
    "⛔ Сначала дождитесь окончания подписки на VPN.\n\n"
)

IOS_URL = "https://apps.apple.com/us/app/clash-mi/id6744321968?l=ru"
ANDROID_URL = "https://github.com/KaringX/clashmi/releases/download/v1.0.30.1605/clashmi_1.0.30.1605_android_arm.apk"
WINDOWS_URL = "https://github.com/KaringX/clashmi/releases/download/v1.0.30.1605/clashmi_1.0.30.1605_windows_x64.exe"

HELP_TEXT = """
❓ Как настроить VPN?

1. Качаем приложение:
<a href='{ios_url}'>IOS</a>
<a href='{android_url}'>ANDROID</a>
<a href='{windows_url}'>WINDOWS</a>
2. Далее следуем шагам из <a href='{video_url}'>видео</a>

😎 Перестало работать или медленно грузит? - админ @{admin} 
"""
