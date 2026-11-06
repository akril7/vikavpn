from src.configuration import Settings
from src.domain.models import User
from src.domain.urls.file import (
    build_clash_config_url as _build_clash_config_url, build_origin,
    build_clash_video_guide_url as _build_clash_video_guide_url
)


def build_clash_config_url(settings: Settings, user: User):
    return _build_clash_config_url(user=user,
                                   origin=build_origin(settings.tls.domain, settings.site.port),
                                   path=settings.clash.configs_urlpath)


def build_clash_video_guide_url(settings: Settings):
    return _build_clash_video_guide_url(
        origin=build_origin(settings.tls.domain, settings.site.port)
    )
