Joel Shor, 4-1-2014
shor.joel@gmail.com

1.0 Introduction
=================================================
The goal of this project is to train a classifier that takes a sequence of
spike data returns the value of the latent variable 'context' of each moment. The spike data are unpublished data from 
Dmitriy Aronov (Tank Lab, Princeton) taken from rats running
spatial tasks in virtual reality. Recordings are LFPs taken from 8 tetrodes. Data
is organized by animal, session, and tetrode.

See Docs/Thesis.pdf for more background on the neuroscience, data, and ML algorithms.

2.0 Outline of File Dependencies
=================================================
+ UnitTests.py
	+ UnitTest/
		+ Validation files (*.validation)
		
+ LocationAnimation.py
	+ Animation/
		+ AnimationWindow.py
			+ EnironmentReader.py
			+ WaveformReader.py
			
+ MakeFig.py
	+ GenerateFigures/
		+ A folder containing scripts to visualize data

+ RunScript.py

+ RunKFoldSimulation


3.0 Classifier 1 (DP)
=================================================
Step 1) Cut the environment into bins and form an 'average' firing
		vector per bin, per cell, per context (bins can be square,
		circular, even area, or not)
	1a) For a given cell, count the number of spikes in the bin
		divided by the time spent in the bin
	1b) Vector of spike rate for all cells is 'average' firing rate
Step 2) Cut the behavior into time bins and generate a firing vector
		during that time
	PARAMETER: How large is each time bin?
Step 3) Compare the dot product of the current firing vector with the
		two baseline vectors for that bin.
Step 3(Alternate)) Transform the current firing vector according to a
		a change of basis, and compare the transformed
		vector components