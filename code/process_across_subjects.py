import numpy as np
import pandas as pd
import os
from Preprocessing import Preprocessing
from datetime import date
def process_across_subjects(data_directory,output_directory,num_practice_trials,num_trials,x_cord_column,y_cord_column):
    """
    This function receives a directory and apply the functions in the above class to all of
    the subjects files in the directory.
    It also creates a unified CSV file of all subjects and saves it in the output directory.
    :Param directory: directory of the data files.
    :param num_practice_trials: int, number of practice trials (trials with mouse tracking data that are
    to be ignored in the analysis)
    :Param num_triasl: int, number of non-practice trials to analyze
    """
    df_list = []
    files = os.listdir(data_directory)
    x_list = []
    y_list = []
    sub_counter = 1
    for sub in range(len(files)):
        if files[sub][0:3] != 'all' and files[sub] != '.DS_Store':
            print("currently processing: ", files[sub], "subject number:", sub_counter)
            cur_class = Preprocessing(data_directory + os.sep + files[sub],num_practice_trials,num_trials,x_cord_column,y_cord_column)
            # preprocess
            if cur_class.isOK:
                cur_class.normalize_time_points()
                cur_class.rescale()
                cur_class.remap_trajectories()
                cur_class.calculate_all_measures()
                df_list.append(cur_class.df)
                x_list.append(cur_class.x)
                y_list.append(cur_class.y)
            else:
                cur_class.calculate_all_measures()
                df_list.append(cur_class.df)
                x_list.append(np.full([cur_class.NUM_TIMEPOINTS,cur_class.df.shape[0]],np.nan))  # add null mouse points
                y_list.append(np.full([cur_class.NUM_TIMEPOINTS,cur_class.df.shape[0]],np.nan))  # add null mouse points

            cur_class.df['subject_id'] = sub_counter
            sub_counter += 1
    big_df = pd.concat(df_list)
    big_x = np.concatenate(x_list,axis=1)
    big_y = np.concatenate(y_list,axis=1)
    big_x = pd.DataFrame(np.transpose(big_x))
    big_y = pd.DataFrame(np.transpose(big_y))
    big_x = big_x.add_prefix('x_')
    big_y = big_y.add_prefix('y_')
    big_df = big_df.reset_index()
    big_df = pd.concat([big_df,big_x,big_y],axis = 1)

    big_df.to_csv(output_directory+os.sep+'all_subjects_processed'+str(date.today())+'.csv')
