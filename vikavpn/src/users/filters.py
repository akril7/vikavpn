from src.db.models import Users


def filter_vpn_users(users: Users) -> Users:
    return filter(lambda user: user.vpn_user, users)


def filter_proxy_users(users: Users) -> Users:
    return filter(lambda user: user.proxy_user, users)
