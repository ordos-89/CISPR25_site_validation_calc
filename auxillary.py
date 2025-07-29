import pandas as pd
import logging

l_logger = logging.getLogger(__name__)


def get_frequency_range(frame: pd.DataFrame):
    f_column_name = frame.columns[0]
    max_freq = max(frame[f_column_name])
    min_freq = min(frame[f_column_name])
    return min_freq, max_freq


def check_frequency(frequency, min_freq, max_freq) -> float or None:
    try:
        freq = float(frequency)
    except ValueError:
        l_logger.info(f'Bad frequency input: {frequency}')
        return None
    else:  # проверка вхождения частоты в диапазон частот антенны
        if not min_freq < freq < max_freq:
            l_logger.info(f'Frequency {freq} is out of range! ({min_freq}, {max_freq})')
            return None
        else:
            return freq


def read_FSH8_csv_file(path_to_file: str, convert_to_MHz: bool = False) -> pd.DataFrame or None:
    """Передаём путь к файлу, 'снятому' с анализатора спектра FSH8.
    Получаем дата-фрейм"""
    # Read data from a specific CSV file. Drop preceding 45 rows of instrument data
    try:
        fsh8_meas = pd.read_csv(path_to_file, skiprows=45, sep=';', decimal=',')
    except UnicodeDecodeError or FileNotFoundError as e:
        l_logger.warning(f'Error while opening csv file: {path_to_file}.\nException:\n{e}')
        return None

    if ' ' in fsh8_meas.columns:
        if all(map(lambda i: i.isspace(), fsh8_meas[' '])):
            fsh8_meas.drop(columns=[' ', ], inplace=True)
        else:
            l_logger.warning(f'Unexpected data encountered in file!\n{path_to_file}')
            raise Exception(f'Unexpected data in FSH8 file! {path_to_file}')
    # In general, we work with MHz. FSH-8 files give frequency in Hz. So...
    if convert_to_MHz:
        # Name of frequency column
        f_col_name = fsh8_meas.columns.to_list()[0]
        l_logger.debug(f'Freq col name\n{f_col_name}')

        # Add a new column, F in MHz
        fsh8_meas['Freq. [MHz]'] = fsh8_meas[f_col_name] / 1e6
        l_logger.debug(f'Added new column:\n{fsh8_meas.head(3)}')
        l_logger.debug(f'columns:\n{fsh8_meas.columns.to_list()}')

        # Drop original Hz column
        fsh8_meas.drop(columns=[f_col_name, ], inplace=True)
        l_logger.debug(f'Dropped original column:\n{fsh8_meas.head(3)}')
        l_logger.debug(f'columns:\n{fsh8_meas.columns.to_list()}')

        # Since new column was added to end of columns, switch column order
        fsh8_meas = fsh8_meas[fsh8_meas.columns.to_list()[::-1]]
        l_logger.debug(f'Sorted columns:\n{fsh8_meas.head(3)}')
        l_logger.debug(f'columns:\n{fsh8_meas.columns.to_list()}')

    return fsh8_meas