This code was used with a Raspberry Pi 3 B that was connected to a ***INSERT SCALE INFORMATION*** for the purpose of tracking the mass of biological samples (maize)
as they gained mass while being conditioned in a humidity chamber and then lost mass while returning to an equilibrium state in ambient laboratory conditions. 
The code collects a mass measurement from the scale every 15 minutes for one entire week, giving 672 measurements total. 
When unable to collect a measurement, the code has failsafes, where it will try multiple times, and then report if the measurement failed.
This wasn't something that I encountered while testing, but it was integrated after the preceding attempts failed, which we later discovered were due to a power source
fault. 
