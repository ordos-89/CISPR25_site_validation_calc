# Intro
This script was created to calculate measurement results of test site validation according to standard CISPR 25:2001.
Frequency range - from 150 kHz to 1 GHz. Test site - ALSE (absorber lined shielded enclosure).
Test method - according to CISPR 25 Annex I.

*Note:* It would be much easier (in terms of code) to perform all the calculations in MS Excel.
When I did this project, I pursued some personal goals as follows:
 * get familiar with Pandas library;
 * get more familiar with Git and GitHub;
 * create an automation script that will cover this task;
 * do as little manual work in future as possible.

# Test method description
Radiating devicce is placed inside ALSE, within a certain test setup, in accordatce with standard requirements.
At 1m distance from the radiating device measuring antenna is placed.
Signal of 120 dBuV level should be applied to radiating device on each frequency, listed in CISPR 25 Annex I.
Measurements are done by different antennas and a receiver or, in our case, we used spectrum analyzer.
Field strength measurements are performed, then the result on each frequency is compared to modeled value, listed in Annex I CISP 25.
Then the percentage of points, that are within [-6 dB; +6 dB] tolerance must be calculated.
The validation is considered successfull, if the percentage is 90% or more.

## Direct measurements
First, we connect the cables together, so we get setup for direct measurements like this:

`[RF_Generator - cable_1 - cable_2 - Spectrum_Analyzer]`

The Generator forms signal on each frequency and we get corresponding spectrum measurements on Spectrum_Analyzer.
These values will be marked as "M0" on each frequency.

## Field measurements
Second, we connect cable_1 to radiating device and cable_2 - to measuring antenna:

`[RF_Generator - cable_1 - radiating_device]  free space  [measuring_antenna - cable_2 - Spectrum_Analyzer]`

Field measurements are performed and results are marked as "MA"

## Calculations
On each freauency the Equivalent Field Strength then calculated, using formula:

`Eeq = 120[dBuV] + (MA - M0) + kAF`

where kAF - antenna factor of the measuring antenna on corresponding frequency.
Note that in frequency range 30 MHz - 1000 MHz measurements are done in two polarizations.
And Eeq_max is considered maximum value of (Eeq_vertical, Eeq_horizontal)

The resulting Eeq_max is then compared to Eeq_max_ref - the value from standard.

# Problem
## 1. Antennas
For frequency range 150 kHz to 30 MHz monopole antenna is used. Only vertical polarization measurements are done here.
In range 30-1000 MHz logoperiodic antenna is used and measurements are done in two polarizations.

The frequency ranges of the antennas themselves are different from these measurement ranges.
So I need to forcedly choose, which antenna to use on a certain frequency.

The antenna factors are tabulated, like this:
| F, MHz | AF, dB |
|---|---|
|30|17.2|
|100|21.3|
....

Thus, I must be able to get interpolated value of AF on any frequency within antenna frequency range.

So I decided to:
a) Create Antenna object that will obtain Antenna Factor table as one of it's parameters and will have method to calculate AF on any frequency within it's range;
b) A Dispatcher class that will control existing antennas and 'call' certain antenna for certain frequency range of my test.

## 2. Measurements
The measurement results in this case were obtained in a form of .csv files from R&S FSH-8 spectrum analyzer.
They have a certain structure (I have to skip like 45 rows in file to get to actual data); more than that,
spectrum analyzer has it's own frequency step which does not correlate with standard or generator frequencies.

`For example, Generator sends signal on 5 MHz. In .csv file I'll get frequencies like 4.899, 5.002, but not exactly 5.
I need to pick the maximum measured result among measured on those frequencies.`

Interpolation is not appliable here, because when frequency increases, the frequency step also increases;
interpolating will lead to miscalculations.

So, we create classes:
a) Measurement; it will obtain a .csv file with measured data in a certain subrange and implement a method of picking maximum measurement near 'desired' frequency;
b) A Dispatcher class, similar to the one for antennas. That will pick up needed file for a certain frequency.

*Note:* it is required, that frequency ranges do not overlap in measurement files for each configuration.

The Measurement and Antenna Dispatcher classes will both inherit from base Dispatcher class, that incapsulates common logic.

## 3. File managemment
All the input files with data should be stored in folders: one - for antenna factors and three - for measurement results:
direct measurements, horizontal and vertical measurements.
The Dispatcher class can get it's objects as all files in a given directory. Then, for each object, it can determine it's frequency range.
For antennas, though, additional dict is specified, that determines frequency ranges for certain antennas.

# Conclusion
In main.py file all the 'buisness-logic' is connected into one piece. In addition, results are exported into df.csv file and displayed via pyplot.
Finally, I saved data to Excel file to create better diagrams.

For the first test, the final result was about 82% points, which is fail.
So next, we will make some improvements to the test site, maybe, use different antennas - and new calculations will be required.
Which may be easily done now, just by placing new files in corresponding folders and, maybe, specifying new antennas.
