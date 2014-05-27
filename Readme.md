Joel Shor, 5-26-2014
shor.joel@gmail.com

1.0 Introduction
=================================================
The goal of this project is to train a classifier that takes a sequence of
spike data returns the value of the latent variable 'context' of each moment. The spike data are unpublished data from 
Dmitriy Aronov (Tank Lab, Princeton) taken from rats running
spatial tasks in virtual reality. Recordings are LFPs taken from 8 tetrodes. Data
is organized by animal, session, and tetrode.

See Docs/Thesis.pdf for more background on the neuroscience, data, and ML algorithms.

Drivers are

python LocationAnimation.py

python MakeFig.py [fig_name]

python RunScript.py [script_name]

python RunScript.py {number_of_folds}
