Joel Shor, 4-1-2014
shor.joel@gmail.com

1.0 Introduction
=================================================
The goal of this project is to train a classifier that takes a sequence of
spike data returns the value of the latent variable 'context' of each moment. The spike data are unpublished data from Dmitriy Aronov (Tank Lab, Princeton) taken from rats running
spatial tasks in virtual reality. Recordings are LFPs taken from 8 tetrodes. Data
is organized by animal, session, and tetrode.

Neuroscience predicts that 'place cells' having high firing rates when an animal
is located in the cell's 'place field', which is a region in its environment. These
cells exist in the hippocampus, and that is where these recordings are taken from.

Global remapping is the phenomenon where place fields appear, disappear, or relocate.
This experiment extends work in global remapping that occurs without changing
the environment (Jezek, 2011; Kelemen, Fenton, 2010; Kloosterman et al, 2013) making the term 'place cell' somewhat of a misnomer.

We seek to leverage the fact that place cells remap when the rat changes contexts
ie changes from chasing the counterclockwise-moving marker to chasing the clockwise-moving marker.

2.0 Outline of File Dependencies
=================================================
+ UnitTests.py
	+ UnitTest/
		+ Validation files (*.validation)
+ LocationAnimation.py
	+ Data/
		+ readData.py
		+ Analysis/
			+ Files to analyze data
	+ LiveData/
		+ AnimationWindow.py
+ MakeFig.py
	+ GenerateFigures/
		+ generateClusterGraphs.py
		+ generateSpikeRateGraphs.py

HMM/ is currently not functional