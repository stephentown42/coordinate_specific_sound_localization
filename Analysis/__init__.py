"""

To determine the coordinate frames in which non-human listeners experience sound location,
we can test their ability to solve psychoacoustic problems. Here, we trained ferrets to 
discriminate two sounds sources based on their location in the world, or relative to the 
head. Full details of the task are available in the documentation.

The current package includes modules to organise (cf_behavior.py), analyse (cf_analysis.py)
and plot (cf_plot.py) the data collected. 

"""

__version__ = '0.1.0'

# Subjects involved in the study
#   - valid_loc = codes for test locations
ferrets = [
    dict(num=1701, color='#517e97', task='World', valid_loc=[6, 12], train='North=>East,South=>West', name="Pendleton"),
    dict(num=1703, color='#586ebd', task='World', valid_loc=[6, 12], train='North=>East,South=>West', name="Grainger"),
    dict(num=1811, color='#4e4bc9', task='World', valid_loc=[6, 12], train='North=>East,South=>West', name="Dory"),
    dict(num=1902, color='#293457', task='World', valid_loc=[5, 11], train='SouthEast=>East,NorthWest=>West', name="Eclair"),
    dict(num=1810, color='#c54450', task='Head', valid_loc=[-90, 90], train='Left=>Left,Right=>Right', name="Ursula"),
    dict(num=1901, color='#cc438f', task='Head', valid_loc=[-180, 0, 180], train='Back=>Left,Front=>Right', name="Crumble"),
    dict(num=1905, color='#d5462c', task='Head', valid_loc=[-180, 0, 180], train='Back=>Left,Front=>Right', name="Sponge")
]
