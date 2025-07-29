import pandas as pd
import os
import logging
import auxillary
import logger

logger.setup_logging()

l_logger = logging.getLogger(__name__)


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


class MeasResult:
    """Организуем класс для хранения измерений определённого вида. В нашем случае будут
    прямые измерения, вертикальная и горизонтальная поляризации.
    Класс будет состоять из дата-фрейма, в который необходимо собрать измерения из нескольких файлов;
    также нужен метод получения измеренного значения для заданной частоты - методом поиска максимума
    из нескольких точек, лежащих наиболее близко к исходной частоте.
    ВНИМАНИЕ: данный класс рассчитан на работу с csv-файлами, полученными от FSH-8"""

    def __init__(self, name: str, path_to_file: str):
        self.name = name
        self.measurements = read_FSH8_csv_file(path_to_file, convert_to_MHz=True)
        self.min_freq, self.max_freq = auxillary.get_frequency_range(self.measurements)

    def _collect_meas_data(self, folder_name: str) -> pd.DataFrame or None:
        """На тестах выяснилось, что такой подход даёт серьёзную ошибку на стыке диапазонов.
        В 'сшитом' датасете частоты 29,95 и 30,00 находятся вплотную. Функция find_value_for_frequency
        будет возвращать максимальное значение для любой из них.
        Решено диапазоны загружать по отдельности в объекты и использовать диспетчер."""
        filenames = os.listdir(folder_name)
        if not filenames:
            l_logger.warning(f'No csv files found in directory: {folder_name}')
            return None
        else:
            data_frames = []
            for file in filenames:
                df = read_FSH8_csv_file(os.path.join(folder_name, file), convert_to_MHz=True)
                if df is not None:  # we only want real DataFrames here
                    data_frames.append(df)

            # Concatenate together all the chunks
            final = pd.concat(data_frames, ignore_index=True)

            # Sort by frequency (0 column)
            f_col_name = final.columns.to_list()[0]
            final = final.sort_values(by=f_col_name)

            # Drop duplicates if any
            final.drop_duplicates(subset=f_col_name, keep='first', inplace=True, ignore_index=True)

            return final

    def find_value_for_frequency(self, frequency, choose_from=3) -> float or None:
        """Функция поиска максимального значения возле заданной частоты.
        Частоты в CISPR идут достаточно часто, дистанция = 0,2 до 30 МГц. Рассматривая 5 частот
        (choose_from=5) уже есть шансы попасть на соседнюю и получить неверный результат."""
        # Проверка введённого значения частоты.
        freq = auxillary.check_frequency(frequency, self.min_freq, self.max_freq)
        if freq:
            # introduce a shortcut
            df = self.measurements

            f_col_name, val_col_name = self.measurements.columns.to_list()

            # Получаем дата-фрейм из choose_from строк, среди которых лежит искомое значение:
            subrange = df.iloc[(df[f_col_name] - freq).abs().argsort()][choose_from]
            l_logger.debug(subrange.sort_index())

            return round(max(subrange[val_col_name]), ndigits=3)


def create_dataset():
    return MeasResult(name='Direct', target_folder='measured_data/direct_measurements')
