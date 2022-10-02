# Mouse tracking preprocessing and analysis tools
This repository contains of scripts to help with the preprocessing, measures extraction and visualization of raw mouse-tracking data, that were obtained in
online experiments.
Constracted after [Freeman & Ambady (2010)](https://link.springer.com/article/10.3758/BRM.42.1.226), all trial's mouse trajectories are interpulated to 100 time points, rescaled, and remmaped. 
It additionaly calculate classical mouse tracking measures, such as area under the curve and x-flips, as well as new measures. 

The scripts are built for experimental data that were obtained in Kleiman lab at the Hebrew University of Jerusalem, using a jsPsych-based implementation of mouse-tracker. 
Thus, in order for it to work on your dataset, the dataset should be structured such that there are indevidual .csv files for each participants. In addition, 
all x and y coordinates should be under the columns 'x_cord' and 'y_cord', respectively.
