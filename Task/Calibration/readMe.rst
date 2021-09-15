---------------------------------
Calibration Recordings
---------------------------------


Sounds are recorded using the same stimulus generation software and hardware used during
testing (GoFerret, Level 54, ), with an additional RZ6 device added to the system for recording 
sound input. Sound input is provided via a B&K measuring amplifier connected to a 1/4" free-field 
microphone via a preamplifier. 

Sound recordings are performed by starting the software and then sending an artificial signal that 
mimics at ferret at the center of the speaker ring, but without the need for the experimenter to 
physically enter the test chamber. Multiple sounds (250 ms broadband noise bursts ) *from one 
speaker* are presented during a single block to assess reliability. We then change the speaker
between blocks while keeping a metadata table of which blocks were associated with which speakers.
(We use blocks from a real ferret to save time, though this may not be the best idea in principle)

Recorded data is initially stored as a TDT block, from which signals must be extracted
and stored in an open format. **get_stimulus_snippets.m** does this by opening a block, selecting a 
long time window in which to search for sounds, and then extracting snippets of recordings around 
each noise burst repeat (or the first 10 repeats if there's more). Snippets are defined as a window
±250 around sound onset that therefore includes a baseline period of quiet as a reference for later
comparison. Snippets are stored as a matrix (*examples*), together with the sample rate of the 
signal (*fS*) in a .mat file (e.g. Block-11.mat)

Sound spectra are then calculated from extracted snippets using **get_stimulus_spectra.m**. This 
function generates a figure containing the spectrum of signals in the baseline and stimulus periods
(top), and a subtraction of the two periods (bottom). Spectra are calculated across the sound using
*pspectrum()* and data are plotted in decibels. Spectra for each snippet are also saved in csv 
format for easy plotting in figures if required.