=============
Matlab Modelling
=============

TO DO:
- Move input data from Matlab to pythoin
- Revise matlab output from graphics to CSV tables
- Move plotting from Matlab to python
- Remove old / redundant models that aren't relevant for this paper


**Disclaimer**
The nonlinear optimization in Matlab is pretty good, whereas I've had some poor performance issues in other contexts 
with scipy optimizers (most probably due to my own misuse). Therefore I'm going to stick with the function available
in Matlab (*fmincon*) for the paper; however a long-term goal for the repository is to move to an open source solution for fitting
models.


----------------------
Test Models
----------------------
- Wrapper that calls Fitting functions for every cross-validation fold
- Loads data and splits into cross-validation folds
- Each fold has separate train/test datasets for fitting models and then assessing performance separately
- Plots model properties and performance (to be removed)


The pattern of results obtained is not dependent on flattening, but it does eliminate a trivial 
reason that might otherwise explain why performance is better than chance. This is particularly the case 
where performance is marginally above chance (e.g. 51%)


----------------------
Fitting Functions
----------------------
- Wrappers for likelihood function that call *fmincon*
- Define the upper and lower bounds for parameters
- Return the tested parameters and associated negative log likelihoods when fitting models to input data

----------------------
Likelihood Functions
----------------------
- These are the functions that are passed to *fmincon* for optimization.
- Return the negative log likelihood of the data, given specific model parameters.

