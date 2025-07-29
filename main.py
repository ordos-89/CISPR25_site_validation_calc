import pandas as pd
import dispatcher
import logger
import matplotlib.pyplot as plt

logger.setup_logging()

requirements_file = 'standard_requirements/CISPR_25.xlsx'
direct_folder = 'measured_data/direct_measurements'
vertical_folder = 'measured_data/vertical_polarization'
horizontal_folder = 'measured_data/horizontal_polarization'
antenna_folder = 'antenna_factors'


def get_main_dataframe():
    # Preparing main DataFrame:
    df = pd.read_excel(requirements_file, names=['F, MHz', 'Eeq_max_ref, dBuV/m'])

    # Collecting all the data to objects
    antennas = dispatcher.AntennaDispatcher(folder_name=antenna_folder)
    direct = dispatcher.MeasurementsDispatcher(folder_name=direct_folder)
    vertical = dispatcher.MeasurementsDispatcher(folder_name=vertical_folder)
    horizontal = dispatcher.MeasurementsDispatcher(folder_name=horizontal_folder)

    # Adding new columns to main DataFrame with the help of Dispatchers

    # Column for AntennaFactor:
    df['AF'] = df['F, MHz'].map(antennas.af_count)
    # column for direct measurements:
    df['direct'] = df['F, MHz'].map(direct.find_value_for_frequency)
    # for vertical polarization measurements:
    df['vert'] = df['F, MHz'].map(vertical.find_value_for_frequency)
    # for horizontal polarization measurements:
    df['hor'] = df['F, MHz'].map(horizontal.find_value_for_frequency)

    # Note: hor column will contain NaN values

    # Count the Eeq
    df['Eeq max'] = 120 + df[['vert', 'hor']].max(axis=1) - df['direct'] + df['AF'] - 10
    # And finally, count the delta:
    df['delta'] = df['Eeq max'] - df['Eeq_max_ref, dBuV/m']
    # add 6 dB borders for displaying on graph
    df['-6 dB'] = -6
    df['6 dB'] = 6

    df.to_csv('df.csv', sep=';', decimal=',')
    df.plot(x='F, MHz', y=['Eeq max', 'Eeq_max_ref, dBuV/m', 'delta', '-6 dB', '6 dB'], kind='line',
            subplots=(('Eeq max', 'Eeq_max_ref, dBuV/m',), ('delta', '-6 dB', '6 dB')),
            grid=True, legend=True,)
    plt.show()
    return df

df = get_main_dataframe()
# df['AF'] = df['F, MHz'].map(ant_d.af_count)