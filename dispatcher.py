"""For operating with set of objects I need a Dispatcher class. Upon receiving frequency request,
the Dispatcher instance must choose an object, whose frequency range fits the requested frequency
and call its methods."""
import logging
import antennas
import auxillary
import measurement
import os
import enum

l_logger = logging.getLogger(__name__)


class ObjectType(enum.Enum):
    antenna = 1
    measurement = 2


class Dispatcher:
    def __init__(self, folder_name=None):
        self.objects = dict()
        self.target_folder = folder_name

    def add_object(self, obj: antennas.Antenna or measurement.MeasResult):
        if isinstance(obj, antennas.Antenna) and obj.name in antennas.atnennas_operating_ranges.keys():
            frequency_range = antennas.atnennas_operating_ranges[obj.name]
        else:
            frequency_range = auxillary.freq_range(obj.min_freq, obj.max_freq)
        self.objects.update({frequency_range: obj})

    def select_object(self, frequency):
        for rng in self.objects.keys():
            if rng.min_freq <= frequency <= rng.max_freq:
                return self.objects[rng]
        # If no suitable object was found:
        else:
            return None

    def collect_objects(self, folder_name: str, type_to_apply):
        """Собирает данные в указанной папке, создаёт из них соответствующие объекты
        и наполняет коллекцию objects."""
        filenames = os.listdir(folder_name)
        if not filenames:
            l_logger.warning(f'No files found in directory: {folder_name}')
            return None
        else:
            for file in filenames:
                df = auxillary.get_dataframe(os.path.join(folder_name, file))
                if df is None:
                    l_logger.info(f'File {file} in {folder_name} was not processed.')
                else:
                    if type_to_apply == ObjectType.antenna:
                        self.add_object(antennas.Antenna(name=file.split('.')[0], af_table=df))
                    elif type_to_apply == ObjectType.measurement:
                        self.add_object(measurement.MeasResult(name=file.split('.')[0], measurements=df))
            if not self.objects:
                l_logger.warning(f'Found no matches for .csv or excel files in directory: {folder_name}')


class AntennaDispatcher(Dispatcher):
    """Диспетчер для антенн.
    При вызове метода af_count сначала выбираем подходящую антенну, а затем вызываем такой же метод у неё."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.collect_objects(self.target_folder, type_to_apply=ObjectType.antenna)

    def af_count(self, frequency) -> float or None:
        matching_antenna = self.select_object(frequency)
        return matching_antenna.af_count(frequency) if matching_antenna else None


class MeasurementsDispatcher(Dispatcher):
    """Диспетчер для результатов измерений.
    При вызове метода find_value_for_frequency выбирает подходящий объект по диапазону и вызывает его метод."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.collect_objects(self.target_folder, type_to_apply=ObjectType.measurement)

    def find_value_for_frequency(self, frequency):
        matching_meas = self.select_object(frequency)
        return matching_meas.find_value_for_frequency(frequency) if matching_meas else None
