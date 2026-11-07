import os.path
import shutil
from pathlib import Path
from urllib.request import urlretrieve

from loguru import logger


def download_file(link: str, save_path: Path, rewrite: bool = False):
    """ Download archive if it not exists (or if rewrite is True) """

    basename = os.path.basename(link)

    if not save_path.exists() or rewrite:
        logger.info(f"Downloading {basename}")
        urlretrieve(link, save_path)


def unpack_clean(archive_path: Path, unpack_path: Path):
    """ Unpack archive and move items on one level top """

    shutil.unpack_archive(archive_path, unpack_path)

    items_dir = list(unpack_path.iterdir())
    if len(items_dir) != 1:
        raise ValueError(f"Target archive has many subdirs: {", ".join(map(str, items_dir))}")

    inner_folder = unpack_path / items_dir[0]

    for item in inner_folder.iterdir():
        shutil.move(item, unpack_path / item.name)

    inner_folder.rmdir()
