import numpy as np
import pandas as pd
import os
from Preprocessing import Preprocessing
from datetime import date
def process_across_subjects(data_directory,output_directory, x_cord_column,y_cord_column, response_column = "", columns_to_preserve = []):
    """
    This function receives a directory and apply the functions in the above class to all the subjects files in the directory.
    It also creates a unified CSV file of all subjects and saves it in the output directory.
    Practice trials are automatically filtered out based on the 'test_part' column containing 'practice'.
    :Param data_directory: directory of the data files.
    :Param x_cord_column: column name containing x-coordinates
    :Param y_cord_column: column name containing y-coordinates
    :Param response_column: optional column name containing response data
    :Param columns_to_preserve: list, column names to check for preserving rows without trajectory data
    """
    df_list = []
    files = os.listdir(data_directory)
    x_list = []
    y_list = []
    sub_counter = 1
    for sub in range(len(files)):
        if (files[sub][0:3] != 'all' and 
            files[sub] != '.DS_Store' and 
            files[sub] != '.gitkeep' and 
            files[sub].endswith('.csv')):
            print("currently processing ", "subject :",files[sub] )
            cur_class = Preprocessing(data_directory + os.sep + files[sub],x_cord_column,y_cord_column, response_column, columns_to_preserve)
            # preprocess
            if cur_class.isOK:
                cur_class.normalize_time_points()
                cur_class.rescale()
                cur_class.remap_trajectories()
            cur_class.calculate_all_measures()
            df_list.append(cur_class.df)

            # Get coordinate arrays that match dataframe shape (NaN for non-trajectory rows)
            x_full, y_full = cur_class.get_coordinate_arrays()
            x_list.append(x_full)
            y_list.append(y_full)

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
