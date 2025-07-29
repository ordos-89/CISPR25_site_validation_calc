import logging
import auxillary

l_logger = logging.getLogger(__name__)


class MeasResult:
    """Организуем класс для хранения измерений определённого вида. В нашем случае будут
    прямые измерения, вертикальная и горизонтальная поляризации.
    Класс будет состоять из дата-фрейма, в который необходимо собрать измерения из нескольких файлов;
    также нужен метод получения измеренного значения для заданной частоты - методом поиска максимума
    из нескольких точек, лежащих наиболее близко к исходной частоте.
    ВНИМАНИЕ: данный класс рассчитан на работу с csv-файлами, полученными от FSH-8"""

    def __init__(self, name: str, path_to_file: str):
        self.name = name
        self.measurements = auxillary.read_FSH8_csv_file(path_to_file, convert_to_MHz=True)
        self.min_freq, self.max_freq = auxillary.get_frequency_range(self.measurements)

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
            subrange = df.iloc[(df[f_col_name] - freq).abs().argsort()][:choose_from]
            l_logger.debug(subrange.sort_index())

            return round(max(subrange[val_col_name]), ndigits=3)

