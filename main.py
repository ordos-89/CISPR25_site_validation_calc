import pandas as pd
import dispatcher
import logger
import logging
import matplotlib.pyplot as plt

logger.setup_logging()
l_logger = logging.getLogger(__name__)

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
    # ATTENTION! the '+10' is here because direct measurements were made with 10 dB attenuator!
    # Normally, you should connect ONLY cables, then you'll get 10 dB more
    # TODO: remove the 10 dB addendum if M0 measurements were made correctly.
    df['M0'] = df['F, MHz'].map(direct.find_value_for_frequency) + 10

    # for vertical polarization measurements:
    df['MA_vert'] = df['F, MHz'].map(vertical.find_value_for_frequency)

    # for horizontal polarization measurements:
    # Note: hor column will contain NaN values in range up to 30 MHz
    df['MA_hor'] = df['F, MHz'].map(horizontal.find_value_for_frequency)

    # Count the Eeq
    # df['Eeq max'] = 120 + df[['vert', 'hor']].max(axis=1) - df['direct'] + df['AF'] - 10

    # Count Eeq hor and Eeq vert:
    df['Eeq_hor'] = 120 + df['MA_hor'] - df['M0'] + df['AF']
    df['Eeq_vert'] = 120 + df['MA_vert'] - df['M0'] + df['AF']

    # Find Eeq max
    df['Eeq max'] = df[['Eeq_vert', 'Eeq_hor']].max(axis=1)
    # And finally, count the delta:
    df['delta'] = df['Eeq max'] - df['Eeq_max_ref, dBuV/m']

    # add 6 dB borders for displaying on graph
    df['-6 dB'] = -6
    df['6 dB'] = 6

    # export data to csv
    df.to_csv('df.csv', sep=';', decimal=',')

    # df.plot(x='F, MHz', y=['Eeq max', 'Eeq_max_ref, dBuV/m', 'delta', '-6 dB', '6 dB', 'Eeq_hor', 'Eeq_vert'],
    #         subplots=(('Eeq max', 'Eeq_max_ref, dBuV/m',), ('Eeq_hor', 'Eeq_vert', 'Eeq_max_ref, dBuV/m'),
    #                   ('delta', '-6 dB', '6 dB')),
    #         grid=True, legend=True, kind='line', )
    # plt.show()

    return df


def test_plot():
    df = pd.read_csv('df.csv', sep=';', decimal=',')

    # Count percent of points that are within 6 dB tolerance
    ok = sum([1 for i in df['delta'] if -6 <= i <= 6])
    total_points = df['delta'].count()
    percent = ok / total_points * 100
    verdict = 'Pass' if percent >= 90 else 'Fail'
    l_logger.info(f'Percent of passed points: {percent}. Verdict: {verdict}')

    df.plot(x='F, MHz', y=['Eeq max', 'Eeq_max_ref, dBuV/m', 'delta', '-6 dB', '6 dB', 'Eeq_hor', 'Eeq_vert'],
            subplots=(('Eeq max', 'Eeq_max_ref, dBuV/m',), ('delta', '-6 dB', '6 dB'), ('Eeq_hor', 'Eeq_vert')),
            grid=True, legend=True, kind='line', title='CISPR 25')
    plt.legend()

    plt.show()


if __name__ == '__main__':
    # get_main_dataframe()
    # test_plot()
    pass
