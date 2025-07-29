"""For operating with set of objects I need a Dispatcher class. Upon receiving frequency request,
the Dispatcher instance must choose an object, whose frequency range fits the requested frequency
and call its methods."""
import logging
import antennas
import measurement
import os
from collections import namedtuple
import pandas as pd


l_logger = logging.getLogger(__name__)
freq_range = namedtuple('Freq_range', ('min_freq', 'max_freq'))


class Dispatcher:
    def __init__(self, folder_name=None):
        self.objects = dict()
        if folder_name:
            self._collect_objects(folder_name)

    def add_object(self, obj: antennas.Antenna or measurement.MeasResult):
        frequency_range = freq_range(obj.min_freq, obj.max_freq)
        self.objects.update({frequency_range: obj})

    def select_object(self, frequency):
        for rng in self.objects.keys():
            if rng.min_freq <= frequency <= rng.max_freq:
                return self.objects[rng]
        # If no suitable object was found:
        else:
            return None

    def _collect_objects(self, folder_name: str):
        """Собирает данные в указанной папке, создаёт из них соответствующие объекты и наполняет коллекцию objects"""
        filenames = os.listdir(folder_name)
        if not filenames:
            l_logger.warning(f'No files found in directory: {folder_name}')
            return None
        else:
            for file in filenames:
                if '.csv' in file:
                    path_to_file = os.path.join(folder_name, file)
                    obj = measurement.MeasResult(name=file.split('.')[0], path_to_file=path_to_file)
                    self.add_object(obj)
                elif any(x in file for x in ('.xlsx', '.xls')):
                    af = pd.read_excel(os.path.join(folder_name, file))
                    self.add_object(antennas.Antenna(name=file.split('.')[0], af_table=af))
                else:
                    l_logger.warning(f'Found no matches for .csv or excel files in directory: {folder_name}')


class AntennaDispatcher(Dispatcher):
    """Диспетчер для антенн.
    При вызове метода af_count сначала выбираем подходящую антенну, а затем вызываем такой же метод у неё."""
    def af_count(self, frequency) -> float or None:
        matching_antenna = self.select_object(frequency)
        return matching_antenna.af_count(frequency) if matching_antenna else None


class MeasurementsDispatcher(Dispatcher):
    """Диспетчер для результатов измерений.
    При вызове метода find_value_for_frequency выбирает подходящий объект по диапазону и вызывает его метод."""
    def find_value_for_frequency(self, frequency):
        matching_meas = self.select_object(frequency)
        return matching_meas.find_value_for_frequency(frequency) if matching_meas else None
