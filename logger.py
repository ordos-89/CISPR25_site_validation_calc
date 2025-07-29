import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime


LOG_DIRECTORY = 'logs'
LOG_FILE_PATTERN = os.path.join(LOG_DIRECTORY, 'app_*.log')
LOG_FILE_LIMIT = 3
LOG_FILE_SIZE = 1024
LOG_LEVEL = 'DEBUG'


def setup_logging():
    # Проверяем и создаём директорию для логов, если она не существует
    if not os.path.exists(LOG_DIRECTORY):
        os.makedirs(LOG_DIRECTORY)

    # Создаем форматтеры
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s\n')

    # Создаем обработчик для вывода в консоль
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)

    # Генерируем имя файла лога с текущей датой и временем
    log_file_name = f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_file_path = os.path.join(LOG_DIRECTORY, log_file_name)

    # Создаем обработчик для записи в файл с ротацией
    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=1024 * 1024 * LOG_FILE_SIZE,  # Размер файла лога перед ротацией (5 МБ в данном случае)
        backupCount=LOG_FILE_LIMIT  # Максимальное количество файлов ротации
    )
    file_handler.setFormatter(formatter)

    # Получаем корневой логгер и удаляем существующие обработчики
    logger = logging.getLogger()
    logger.setLevel(LOG_LEVEL)  # Устанавливаем уровень логирования из переменной LOG_LEVEL
    logger.handlers = []  # Удаляем все существующие обработчики

    # Добавляем новые обработчики к корневому логгеру
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Удаляем старые файлы логов, если их количество превышает LOG_FILE_LIMIT
    log_files = [f for f in os.listdir(LOG_DIRECTORY) if f.startswith('app_')]
    if len(log_files) > LOG_FILE_LIMIT:
        log_files.sort(reverse=True)
        for file_name in log_files[LOG_FILE_LIMIT:]:
            os.remove(os.path.join(LOG_DIRECTORY, file_name))
