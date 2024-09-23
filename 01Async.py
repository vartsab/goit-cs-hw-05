import argparse
import asyncio
import os
from pathlib import Path
import shutil
import logging

from aiofiles import os as aio_os

# Налаштування логування помилок
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_folder_path(prompt_text):
    """Функція для взаємодії з користувачем та отримання шляху до папки."""
    while True:
        folder_path = input(prompt_text)
        path = Path(folder_path)
        if path.exists() and path.is_dir():
            return path
        else:
            print(f"Папка {folder_path} не знайдена або не є директорією. Спробуйте ще раз.")

def parse_arguments():
    """Парсинг аргументів командного рядка або запит аргументів у користувача."""
    parser = argparse.ArgumentParser(description='Асинхронне сортування файлів по підпапках на основі розширень.')
    parser.add_argument('source_folder', nargs='?', type=str, help='Шлях до вихідної папки')
    parser.add_argument('output_folder', nargs='?', type=str, help='Шлях до цільової папки')
    args = parser.parse_args()

    # Перевірка аргументів, якщо не вказані, запитати у користувача
    if not args.source_folder:
        args.source_folder = get_folder_path("Введіть шлях до вихідної папки: ")
    if not args.output_folder:
        args.output_folder = get_folder_path("Введіть шлях до цільової папки: ")

    return args

def print_directory_tree(directory, indent=''):
    """Функція для рекурсивного виведення структури директорій."""
    files = list(directory.iterdir())
    files.sort()
    for file in files:
        if file.is_dir():
            print(f"{indent}📁 {file.name}")
            print_directory_tree(file, indent + '    ')
        else:
            print(f"{indent}📄 {file.name}")

# Отримуємо аргументи з командного рядка або від користувача
args = parse_arguments()

# Ініціалізація асинхронних шляхів для вихідної та цільової папок
source_path = Path(args.source_folder)
output_path = Path(args.output_folder)

async def copy_file(file_path, destination_folder):
    """Асинхронна функція для копіювання файлу в цільову папку."""
    try:
        destination_folder.mkdir(parents=True, exist_ok=True)
        dest_file_path = destination_folder / file_path.name
        logger.info(f'Копіювання файлу {file_path} до {dest_file_path}')
        await aio_os.makedirs(destination_folder, exist_ok=True)
        await asyncio.to_thread(shutil.copy, file_path, dest_file_path)
    except Exception as e:
        logger.error(f'Помилка при копіюванні файлу {file_path}: {e}')

async def read_folder(folder_path, output_folder):
    """Асинхронна функція для рекурсивного читання всіх файлів у папці."""
    try:
        for root, dirs, files in os.walk(folder_path):
            for file_name in files:
                file_path = Path(root) / file_name
                # Визначаємо підпапку для файлу на основі розширення
                extension_folder = output_folder / file_path.suffix[1:].upper() if file_path.suffix else output_folder / 'NO_EXTENSION'
                await copy_file(file_path, extension_folder)
    except Exception as e:
        logger.error(f'Помилка при читанні папки {folder_path}: {e}')

async def main():
    """Основна функція для запуску асинхронного читання та копіювання файлів."""
    if not source_path.exists():
        logger.error(f'Вихідна папка не знайдена: {source_path}')
        return

    await read_folder(source_path, output_path)
    logger.info('Сортування файлів завершено.')
    print("\nСтруктура вихідної папки:")
    print_directory_tree(source_path)
    print("\nСтруктура цільової папки:")
    print_directory_tree(output_path)

# Запуск асинхронної функції read_folder у головному блоці
if __name__ == '__main__':
    asyncio.run(main())
