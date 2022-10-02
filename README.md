# Mouse tracking preprocessing and analysis tools
In this repository, you will find scripts for preprocessing, extracting measurements, and visualizing raw mouse-tracking data collected from online experiments.
Based on [Freeman & Ambady (2010)](https://link.springer.com/article/10.3758/BRM.42.1.226), mouse trajectories are interpolated to 100 time points, rescaled, and remapped for each trial. 
Additionally, it calculates classical mouse tracking measures, such as the area under the curve and x-flips, as well as new ones. A variety of data visualization options are also available. 

The scripts are built for experimental data that were obtained in Kleiman lab at the Hebrew University of Jerusalem, using a jsPsych-based implementation of mouse-tracker. 
Thus, for it to work on your dataset, the dataset should be structured so that there are individual .csv files for each participant. In addition, all x and y coordinates should be under the columns 'x_cord' and 'y_cord', respectively. Experimental condition should be stated in an additional 'Condition' column.
