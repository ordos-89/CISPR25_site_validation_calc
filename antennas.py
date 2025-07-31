"""Функционал антенн. Класс антенны должен принимать в конструктор таблицу коэффициентов калибровки и
обладать методом, позволяющим вычислить к-т калибровки на произвольной частоте из своего диапазона."""
import logging
import pandas as pd
import numpy as np
import auxillary

# use pd.read_excel to obtain DataFrame for antenna factors.
# Excel file must contain single sheet with headers. Or, specify sheet name.


#  create file-level l_logger
l_logger = logging.getLogger(__name__)

# Here we determine, which antenna to use in which frequency range
atnennas_operating_ranges = {
    'AH010': auxillary.freq_range(0.15, 29.99),
    'VULB': auxillary.freq_range(30, 1000)
}


class Antenna:
    def __init__(self, name: str, af_table: pd.DataFrame):
        self.name = name
        self.af_table = af_table
        self.min_freq, self.max_freq = auxillary.get_frequency_range(self.af_table)

    def af_count(self, frequency) -> float or None:
        """
        Рассчитывает коэффициент калибровки для произвольной частоты из своего диапазона.
        :param frequency: int, float or str value of desired frequency
        :return: antenna factor for given frequency, float
        """
        # Проверка введённого значения частоты.
        freq = auxillary.check_frequency(frequency, self.min_freq, self.max_freq)
        if freq:
            # introduce a shortcut
            af = self.af_table
            f_col_name, af_col_name = af.columns.to_list()

            # If there is an exact match in frequency values, return corresponding AF value.
            if freq in af[f_col_name].values:
                return float(af.loc[af[f_col_name] == freq][af_col_name].values[0])

            # In other cases, count the AF value by linear interpolation
            else:
                # находим индекс ближайшего к искомой частоте значения в столбце частоты:
                nearest_idx = np.abs(af[f_col_name] - freq).idxmin()

                # Определяем шаг: какой брать второй индекс
                step = 1 if af[f_col_name].iloc[nearest_idx] < freq else -1

                # Получаем дата-фрейм из двух строк, между которыми лежит искомое значение
                subrange = af.iloc[[nearest_idx, nearest_idx + step]][:]

                # subrange = af.iloc[(af[f_col_name] - freq).abs().argsort()][:1]
                # l_logger.debug(subrange)

                # Добавляем новую строку с указанной частотой и NaN для AF
                subrange.loc[-1] = [freq, None]
                # l_logger.debug(subrange)

                # Сортируем по частоте (важно для корректной интерполяции)
                subrange = subrange.sort_values(f_col_name).reset_index(drop=True)
                # l_logger.debug(subrange)

                # Выполняем линейную интерполяцию
                subrange[af_col_name] = subrange[af_col_name].interpolate(method='linear')
                # l_logger.debug(subrange)

                # Возвращаем интерполированное значение для новой частоты
                return round(float(subrange.loc[subrange[f_col_name] == freq, af_col_name].values[0]), ndigits=2)
