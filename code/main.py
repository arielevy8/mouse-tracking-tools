import os
from Visualization import Visualization
from datetime import date
from process_across_subjects import process_across_subjects

# Define Global Variables

# Set directory to be the parent directory of the current file
DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Alternatively, define your own path

# Set number of practice trials and number of experimental trials
NUM_PRACTICE_TRIALS = 4  # First n trials for each subject, to be discarded . Could be 0 if there was no practice
NUM_TRIALS = 42  # Required, number of experimental trials.

# Set column names
X_CORD_COLUMN = 'x_cord'  # The name of the column of x coordinates
Y_CORD_COLUMN = 'y_cord'  # The name of the column of y coordinates
FIRST_CONDITION_COLUMN = 'Condition'  # Optional, name of the column describe the experimental condition
SECOND_CONDITION_COLUMN = ''  # Optional, name of the column describe an experimental condition of second order

# Set visualization parameters
STUDY_TITLE = ''  # This will be the title of the graph
TITLE_SIZE = 16
LABELS_SIZE = 12
TICKS_SIZE = 10
LEGEND_SIZE = 12
POINT_SIZE = 4
COLORMAP = 'rainbow'  # Other common options: RdYlGn, viridis

# Parameters for additional visualization options
SUBJECT_TO_INSPECT = 6  # Integer, subject ID to plot. If 0, will not plot specific subject.

#TODO
# NUM_SAMPLES = 0  # Integer, number of sample trajectories to plot. If 0, will not plot sample trajectory
# TRAJECTORY_TO_INSPECT = [6, 13]  # list, where first value is subject number and second value is trial number

# Alternative usage
PREPROCESS = True  # Change to False if the data is already processed, and you only want to do visualization
ALTERNATIVE_VIS_PATH = ''  # add file path if you want to visualize different file other than what was preprocessed

if __name__ == "__main__":
    # Process study:
    if DIRECTORY == os.path.dirname(os.path.dirname(os.path.abspath(__file__))):
        data_directory = DIRECTORY+os.sep+'data'
        output_directory = DIRECTORY+os.sep+'output'
    else:
        data_directory = DIRECTORY
        output_directory = DIRECTORY
    if PREPROCESS:
        process_across_subjects(data_directory, output_directory, NUM_PRACTICE_TRIALS, NUM_TRIALS,
                                X_CORD_COLUMN,Y_CORD_COLUMN)
    if ALTERNATIVE_VIS_PATH:
        vis_path = ALTERNATIVE_VIS_PATH
    else:
        vis_path = output_directory + os.sep + 'all_subjects_processed' + str(date.today()) + '.csv'
    viz = Visualization(vis_path, output_directory,
                        STUDY_TITLE,
                        FIRST_CONDITION_COLUMN, SECOND_CONDITION_COLUMN,
                        TITLE_SIZE, LABELS_SIZE, TICKS_SIZE , LEGEND_SIZE, POINT_SIZE,COLORMAP,
                        SUBJECT_TO_INSPECT)
    viz.plot_means()  # plots the mean of the experiment
    viz.plot_subject()  # plots all trajectories of the subject defined for inspection

    #TODO
    # viz.examine_certain_trajectory()
    # viz.plot_trajectories_sample(5)  # plots randomly sampled 5 trajectories for each condition
    # viz.plot_subject_mean(3)  # plots the mean trajectories of subject 3

    #
