import antennas
import pandas as pd

requirements_file = 'standard_requirements/CISPR_25.xlsx'


def get_main_dataframe():
    return pd.read_excel(requirements_file, names=['F, MHz', 'Eeq_max, dBuV/m'])
