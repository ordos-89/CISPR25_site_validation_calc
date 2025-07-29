import pandas as pd
import logging

logger = logging.getLogger(__name__)


def get_frequency_range(frame: pd.DataFrame):
    f_column_name = frame.columns[0]
    max_freq = max(frame[f_column_name])
    min_freq = min(frame[f_column_name])
    return min_freq, max_freq


def check_frequency(frequency, min_freq, max_freq) -> float or None:
    try:
        freq = float(frequency)
    except ValueError:
        logger.info(f'Bad frequency input: {frequency}')
        return None
    else:  # проверка вхождения частоты в диапазон частот антенны
        if freq > max_freq or freq < min_freq:
            logger.info(f'Frequency {freq} is out of range! ({min_freq}, {max_freq})')
            return None
        else:
            return freq
