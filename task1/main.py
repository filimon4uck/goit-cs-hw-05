import asyncio
import os
import aiofiles
import aiofiles.os
import shutil
import logging
from argparse import ArgumentParser
from pathlib import Path


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s [%(levelname)s] %(message)s",
)


async def copy_file(src: Path, dest_dir: Path, sem: asyncio.Semaphore):
    async with sem:
        try:
            ext = src.suffix[1:] if src.suffix else "no_extention"
            target_folder = dest_dir / ext
            await aiofiles.os.makedirs(target_folder, exist_ok=True)

            dest_file = target_folder / src.name

            await asyncio.to_thread(shutil.copy2, src, dest_file)

            logging.info(f"Copied: {src} > {dest_file}")
        except Exception as e:
            {logging.error(f"Error copying {src}: {e}")}


async def read_folder(src_dir: Path, dest_dir: Path):
    loop = asyncio.get_running_loop()
    walk_results = await loop.run_in_executor(None, lambda: list(os.walk(src_dir)))
    sem = asyncio.Semaphore(10)
    tasks = []
    for root, _, files in walk_results:
        for file in files:
            src_path = Path(root) / file
            tasks.append(copy_file(src_path, dest_dir, sem))
    await asyncio.gather(*tasks)


async def main():
    parser = ArgumentParser(description="Asynchroning coping files for extentions")
    parser.add_argument("source", type=str, help="Source folder with files")
    parser.add_argument("output", type=str, help="Output folder with files")
    args = parser.parse_args()

    src_dir = Path(args.source)
    dest_dir = Path(args.output)

    if not src_dir.exists():
        logging.error(f"Source folder is not exists")
        return
    await read_folder(src_dir, dest_dir)
    logging.info("Coping finished")


if __name__ == "__main__":
    asyncio.run(main())
