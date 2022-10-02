import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from preprocessing import TrajectoryProcessing
from visualization import Visualization
from datetime import date




def process_across_subjects(directory):
    """
    This function gets a directory and apply the functions in the above class on all of
    the subjects files in the directory.
    It also creates a unified CSV file of all subjects and saves it in the directory
    """
    df_list = []
    files = os.listdir(directory)
    x_list = []
    y_list = []
    for sub in range(len(files)):
        if files[sub][0:3] != 'all' and files[sub][0] != '$':
            print("currently processing: ", files[sub], "subject number:", files[sub][0:2])
            cur_class = TrajectoryProcessing(directory + "\\" + files[sub])
            ###preprocess
            cur_class.normalize_time_points()
            cur_class.rescale()
            cur_class.remap_trajectories()
            cur_class.agg_by_conflict()
            # cur_class.plot_by_conflict()
            cur_class.calculate_all_measures()
            cur_class.df['subject_id'] = int(float(files[sub][0:2]))# add 'subject id' column in correspondence with the name of the original file
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

    ## Process study 1:
    directory = r"C:\Users\user\Google Drive\Kleiman lab\mouse-tracking workshop\Study 1 data" #The path for study 1 data
    process_across_subjects(directory)
    path = directory+'\\all_subjects_processed'+str(date.today())+'.csv'
    subjects_to_remove = [1,15,16,22,43,56,23] #The list of subjects id's to remove was determined based on their attention check and behavioral data,
                                                #and the code determining which subjects to remove is to be found in the corresponding R code
    viz = Visualization(path,subjects_to_remove,'Study 1')
    viz.remove_subjects()
    viz.agg_by_conflict()
    viz.plot_means_by_cond()
    viz.plot_trajectories_sample(100)

 