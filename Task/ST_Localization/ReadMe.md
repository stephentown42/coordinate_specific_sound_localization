# Stages

Each level function denotes a particular protocol for testing, which can be modulated by the selection of task parameters (e.g. if you want to use a longer hold time or timeout duration for one subject than another). Note that some training levels may be used only once or twice, or skipped entirely if an animal is showing promising behavior.

### [Level 01](stages/level01.m) - Welcome to the box
Designed to introduce the animal to the idea that spouts provide water and that holding at lick ports generates stimuli. Stimuli are repeating lights and sounds, with a minimal hold time (<20ms) so that rewards can be given frequently. Usuallly this stage is performed with experimenter monitorring / interacting to encourage the animal to remain near the lick ports (while not simultaneously flooding the box with water).

It is hard-coded that stimuli will repeat continuously, though the stimulus properties at this level are largely irrelevant as the animal can make any response, and is not expected to perform with any structure (i.e. to move from centre to response ports). Note also that because the behavior doesn't yet follow a trial structure, the conventional tabular results file is not saved (column headers are, to indicate the session was performed, but nothing else).

### [Level 02](stages/level02.m) - Building center-response behavior
Designed to build the underlying trial structure in which the animal goes from center port to response port. Stimuli are co-located lights and sounds presented at the response spout; the idea being to attract the ferret's interest in the stimulus and draw the response. However any response is acceptable and all responses are rewarded. The number of stimuli is given over to experimenter control, however for most cases it is expected that stimuli will be repeated until animals respond (nStimRepeats=-1). 

([*sample results file*](sample_data/11_10_2018%20level02_SpatialTraining%2015_03_55.197%20Block_J5-8.txt))

### [Level 04](stages/level04.m) - Introducing errors
This is the first point at which a reward contingency is imposed, and the animal can perform error trials. However there is no timeout after errors; the code simply moves into the correction trial without delay. The number of stimuli is expected to be large but finite (3-10) and decrease with training. 

([*sample results file*](sample_data/15_05_2019%level04_Eclair%15_39_50.572%20Block_J6-20.txt))

### [Level 54](stages/level54.m) - World-centered workhorse
This is the main testing level, with enough flexibility to support the final stages of training via changes in parameters. With the addition of timeout  fundamental task structure is complete
