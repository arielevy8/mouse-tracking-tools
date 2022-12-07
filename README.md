# Mouse tracking preprocessing and analysis tools
In this repository, you will find scripts for preprocessing, extracting measurements, and visualizing raw mouse-tracking data collected from online experiments.
Based on [Freeman & Ambady (2010)](https://link.springer.com/article/10.3758/BRM.42.1.226), mouse trajectories are interpolated to 100 time points, rescaled, and remapped for each trial. 
Additionally, it calculates classical mouse tracking measures, such as the area under the curve and x-flips, as well as new ones. A variety of data visualization options are also available. 

## Usage guidlines
The scripts were originally built for experimental data that were obtained in Kleiman lab at the Hebrew University of Jerusalem, using a jsPsych-based implementation of mouse-tracker. 

Thus, for it to work on your dataset:
- The dataset should be structured so that there are individual .csv files for each participant. 
- All x and y coordinates should be under the columns 'x_cord' and 'y_cord', respectively. 
- Experimental condition should be stated in an additional 'Condition' column. 

Please contact me (arielevy8) regarding any need for clarification. 

## Contents

#### Preprocessing.py

This class contains all preprocessing-related functions for mouse tracking data, including normalization, rescaling (to deal with data from different browsers and coordinate systems), and remapping. It also extracts all mouse-mouse-tracking-based measures.

#### Visualization.py

This class contains functions that handle some parts of the data visualization (other parts of the data visualization can be found in the R script).

Example plots made by this script can be found in 'images' folder.
#### main.py

Script for using the two classes mentioned above to process the mouse tracking data of multiple subjects iteratively.

#### rprocessing.R (down for maintanance)

R script for extensive visualization and analysis of the preprocessed data.
Example plots made by this script can be found in 'images' folder.

#### example data
Mock data of three 'participants' in a generic experiment with two conditions.


