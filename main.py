import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from Preprocessing import Preprocessing
from visualization import Visualization
from datetime import date

num_practice_trials = 4
num_trials = 42

def process_across_subjects(directory,num_practice_trials,num_trials):
    """
    This function gets a directory and apply the functions in the above class on all of
    the subjects files in the directory.
    It also creates a unified CSV file of all subjects and saves it in the directory.
    :Param directory: directory of the data files.
    :param num_practice_trials: int, number of practice trials (trials with mouse tracking data that are
    to be ignored in the analysis)
    :Param num_triasl: int, number of non-practice trials to analyze 
    """
    df_list = []
    files = os.listdir(directory)
    x_list = []
    y_list = []
    for sub in range(len(files)):
        if files[sub][0:3] != 'all':
            print("currently processing: ", files[sub], "subject number:", files[sub][0:2])
            cur_class = Preprocessing(directory + "\\" + files[sub],num_practice_trials,num_trials)
            ###preprocess
            cur_class.normalize_time_points()
            cur_class.rescale()
            cur_class.remap_trajectories()
            cur_class.calculate_all_measures()
            cur_class.df['subject_id'] = int(float(files[sub][0:2]))# add 'subject id' column in correspondence with 
                                                                    # the name of the original file
            df_list.append(cur_class.df)
            x_list.append(cur_class.x)
            y_list.append(cur_class.y)  
    big_df = pd.concat(df_list)
    big_x = np.concatenate(x_list,axis=1)
    big_y = np.concatenate(y_list,axis=1)
    big_x = pd.DataFrame(np.transpose(big_x))
    big_y = pd.DataFrame(np.transpose(big_y))
    big_x = big_x.add_prefix('x_')
    big_y = big_y.add_prefix('y_')
    big_df = big_df.reset_index()
    big_df = pd.concat([big_df,big_x,big_y],axis = 1)

    big_df.to_csv(directory+'\\all_subjects_processed'+str(date.today())+'.csv')

if __name__ == "__main__":

    ## Process study:
    directory = os.getcwd()+'\\'+'example_data' #The path for study data
    process_across_subjects(directory,num_practice_trials,num_trials)
    viz = Visualization(directory+'\\all_subjects_processed'+str(date.today())+'.csv','Example Data')
    viz.plot_means() #plots the mean of the experiment
    viz.plot_trajectories_sample(5) #plots randomly sampled 5 trajectories for each condition
    viz.plot_subject_mean(3) # plots the mean trajectories of subject 3
    viz.plot_subject(3) # plots all trajectories of subject 3 


