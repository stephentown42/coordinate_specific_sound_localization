==============
Speaker Swaps
==============

A swap refers to the manual switch of two speakers between known locations in the world. For example, if we start with Speaker A at the North Pole, and Speaker B at the South Pole, then after the swap we end with Speaker B at the North Pole and Speaker A at the South Pole.

-------------
Organization
-------------
The repository includes the original data for each test session before and after swap, using a file tree that labels each swap by number.

Summary metrics (total number of trials, number of trial correct) are obtained for each file using `summarize_swaps.py <summarize_swaps.py>`_ and stored for convenience in `Speaker_Summary.csv <Speaker_Summary.csv>`_ 

-------------
Why do this?
-------------
Although we calibrated for sound level and generated sounds with the same broadband spectrum, there's always the possibility that somehow we missed something about the spectral output of speakers that differs between sources (i.e. an unknown unknown). If such a feature was available to animals, they might use it to discriminate between sources based on their acoustic output, rather than sound location. Regardless of how good your calibration method is, there's always the possibility that you miss something. 

The best way to control for potential differences between sound sources is to directly swap them. If subjects are making decisions based on non-spatial cues, their behavior should follow the speaker, resulting in a dramatic decrease in performance (either to sub-chance levels or 50% if the listener gives up and starts guessing). Alternatively, if subjects are using spatial cues, then swapping speakers should have no effect on performance.

---------------
Technical notes
---------------
The test chamber in which we performed these experiments were not designed for moving speakers. We initially tried several times to access speakers on the south side of the box without success, before hiring someone in 2018 who was shorter and thinner enough to squeeze into the small gaps in the chamber and perform the swap. We ultimately decided this wasn't safe or practical and so stopped swaps in 2019, before adapting the chamber in 2020 to make the speakers slightly more accessible (though it was still a huge pain and I hurt my back several times). In future (and for anyone considering making your own setup), we will revise the organization of the experiment so that all speakers are on a mobile ring that can be independently rotated around the chamber center.

