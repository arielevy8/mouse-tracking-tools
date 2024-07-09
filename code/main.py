import os
from Visualization import Visualization
from datetime import date
from process_across_subjects import process_across_subjects

# Define Global Variables
# Set directory to be the parent directory of the current file
DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Alternatively, define your own path, and output will be saved with data
NUM_PRACTICE_TRIALS = 4
num_trials = 42

if __name__ == "__main__":
    # Process study:
    if DIRECTORY == os.path.dirname(os.path.dirname(os.path.abspath(__file__))):
        data_directory = DIRECTORY+os.sep+'data'
        output_directory = DIRECTORY+os.sep+'output'
    else:
        data_directory = DIRECTORY
        output_directory = DIRECTORY
    process_across_subjects(data_directory,output_directory,NUM_PRACTICE_TRIALS, num_trials)
    viz = Visualization(output_directory+os.sep+'all_subjects_processed'+str(date.today())+'.csv','Example Data')
    viz.plot_means() #plots the mean of the experiment
    viz.plot_trajectories_sample(5) #plots randomly sampled 5 trajectories for each condition
    viz.plot_subject_mean(3) # plots the mean trajectories of subject 3
    viz.plot_subject(3) # plots all trajectories of subject 3


