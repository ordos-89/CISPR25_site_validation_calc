"""Функционал антенн. Класс антенны должен принимать в конструктор таблицу коэффициентов калибровки и
обладать методом, позволяющим вычислить к-т калибровки на произвольной частоте из своего диапазона."""
import logging
import pandas as pd
import logger
import auxillary

# use pd.read_excel to obtain DataFrame for antenna factors.
# Excel file must contain single sheet with headers. Or, specify sheet name.


# Set up l_logger
logger.setup_logging()
#  create file-level l_logger?
local_logger = logging.getLogger(__name__)


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
                # Получаем дата-фрейм из двух строк, между которыми лежит искомое значение:
                subrange = af.iloc[(af[f_col_name] - freq).abs().argsort()][:2]
                local_logger.debug(subrange)

                # Добавляем новую строку с указанной частотой и NaN для AF
                subrange.loc[-1] = [freq, None]

                local_logger.debug(subrange)

                # Сортируем по частоте (важно для корректной интерполяции)
                subrange = subrange.sort_values(f_col_name).reset_index(drop=True)
                local_logger.debug(subrange)
                # Выполняем линейную интерполяцию
                subrange[af_col_name] = subrange[af_col_name].interpolate(method='linear')

                local_logger.info('calculated AF: success!')
                # Возвращаем интерполированное значение для новой частоты
                return round(subrange.loc[subrange[f_col_name] == freq, af_col_name].values[0], ndigits=2)


def create_vulb():
    af = pd.read_excel('antenna_factors/VULB.xlsx')
    vulb = Antenna(name='VULB', af_table=af)
    return vulb
