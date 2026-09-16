import os.path
import shutil
from dataclasses import dataclass
from pathlib import Path
from urllib.request import urlretrieve

from loguru import logger


@dataclass
class SSLPaths:
    cert: str
    key: str

    def exists(self) -> bool:
        return Path(self.cert).exists() and Path(self.key).exists()


def is_root() -> bool:
    return os.getuid() == 0


def check_root():
    """ Raise error if user is not root """

    if not is_root():
        raise RuntimeError("Require root")


def check_status(status: bool):
    if not status:
        raise RuntimeError("Status is down")


def download_file(link: str, save_path: Path, rewrite: bool = False):
    """ Download archive if it not exists (or if rewrite is True) """

    basename = os.path.basename(link)

    if not save_path.exists() or rewrite:
        logger.info(f"Downloading {basename}")
        urlretrieve(link, save_path)


def unpack_clean(archive_path: Path, unpack_path: Path):
    """ Unpack archive and move items on one level top """

    shutil.unpack_archive(archive_path, unpack_path)

    file_basename = (archive_path.name
                     .replace(".tar", "")
                     .replace(".gz", ""))
    inner_folder = unpack_path / file_basename

    for item in inner_folder.iterdir():
        shutil.move(item, unpack_path / item.name)

    inner_folder.rmdir()
