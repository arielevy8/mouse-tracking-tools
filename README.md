# Mouse tracking preprocessing and analysis tools
In this repository, you will find scripts for preprocessing, extracting measurements, and visualizing raw mouse-tracking data collected from online experiments.
Based on [Freeman & Ambady (2010)](https://link.springer.com/article/10.3758/BRM.42.1.226), mouse trajectories are interpolated to 100 time points, rescaled, and remapped for each trial. 
Additionally, it calculates classical mouse tracking measures, such as the area under the curve and x-flips, as well as new ones. A variety of data visualization options are also available. 

## Usage guidelines
The scripts were originally built for experimental data obtained in the Kleiman lab at the Hebrew University of Jerusalem, using a jsPsych-based implementation of a mouse tracker. 

Thus, for it to work on your dataset:
- The dataset should be structured so that there are individual .csv files for each participant. 
- All x coordinates should be in a specific column, and all y coordinates should be in another column. The names of these columns should be stated in the main.py file, using the global variables X_CORD_COLUMN and Y_CORD_COLUMN

The visualization functionality can work with up to 2 condition factors. The first factor controls the color, and the second factor controls the subplot. The number of conditions in each factor is unlimited. Each factor's condition information should be in a different column, and the names of these columns should be stated in the main.py file, using the global variables FIRST_CONDITION_COLUMN and SECOND_CONDITION_COLUMN.

Please feel free to contact me (ariel.levy2@mail.huji.ac.il) for any further clarification.

## Contents

### Data
The data folder includes mock data of three 'participants' in a generic experiment with one factor containing two conditions. This is only for demonstration purposes.
You can copy your own data files to this folder in order to process them. Alternatively, you can define 

### Code:

#### Preprocessing.py

This class contains all preprocessing-related functions for mouse tracking data, including normalization, rescaling (to deal with data from different browsers and coordinate systems), and remapping. It also extracts six mouse-mouse-tracking-based measures:
1. x-flips: the number of times a participant shifted direction during the trial.
2. RPB (Returns to the Point of Balance): the number of times a participant crossed the line from one side of the screen to the other.
3. AUC (Area Under the Curve): the area between the actual trajectory and a straight line connecting the starting point and the chosen option.
4. MD (Maximal Deviation): the maximal deviation from the actual trajectory to a straight line connecting the starting position and the chosen option.
5. initiation angle: the angle between the starting of the trajectory to the x-axis
6. initiation correspondence: determines whether the initiation angle is below 90, i.e., whether it corresponds to the direction of the chosen option.

#### process_across_subjects.py

This function runs preprocessing iteratively over all data files in the data folder and outputs a unified data file with all mouse measures calculated.

#### Visualization.py

This class contains functions that visualize the raw mouse trajectories and mean trajectories of participants in the experiment.

Example plots made by this script can be found in the 'output' folder.

#### main.py

The main file, in which you can define global variables, such as column names and visualizations' design parameters, and run preprocessing and visualization.

### Output
This folder includes example output files: preprocessed unified data file and visualization results.

