from typing import Callable

from pydantic_settings import BaseSettings

IsInstallCallback = Callable[[], bool]
ReloadControllerCallback = Callable[[], None]
GetRequiredSettings = Callable[[], tuple[BaseSettings, ...]]
