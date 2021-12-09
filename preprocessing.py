#from os import path
import numpy as np
from numpy.core.fromnumeric import shape
import pandas as pd
import matplotlib.pyplot as plt
from scipy import interpolate
import os


class TrajectoryProcessing(object):
    """
    This class gets csv path for a single subject in the experiment, 
    and contain of functions that help with the preprocessing, measures extraction, and plotting of the data
    """
    def __init__(self,path):
        self.NUM_PRACTICE_TRIALS = 4
        self.NUM_TRIALS = 42
        self.df = pd.read_csv (path,index_col=None, header=0) 
        self.df = self.df.dropna(subset = ["x_cord"]) #read only lines with mouse tracking data
        self.df = self.df.iloc[self.NUM_PRACTICE_TRIALS:,] #drop practice trials
        self.df = self.df.reset_index()
        self.x = self.df["x_cord"]
        self.y = self.df["y_cord"]
        
        self.x = self.x.str.split(',', expand=True)
        self.x = self.x.reset_index(drop=True)
        self.x = self.x.to_numpy() #convert to numpy matrix for future processing
        self.x = self.x.astype(np.float64)#convert type from strings to floats
        self.x = np.transpose(self.x)#transpose for easier processing (now the matrix size is NUM_TIMEPOINTS*NUM_TRIALS)

        self.y = self.y.str.split(',', expand=True)
        self.y = self.y.reset_index(drop=True)
        self.y = self.y.to_numpy()
        self.y = self.y.astype(np.float64)
        self.y = np.transpose(self.y)
        #self.y = self.y[self.NUM_PRACTICE_TRIALS:,] 
        

    def normalize_time_points(self):
        """
        This function uses linear interpolation to normalize all of the trajectories to 101 time points from start to finish.
        """ 
        #innitialize matrix
        xnew = np.empty([101,self.NUM_TRIALS]) 
        ynew = np.empty([101,self.NUM_TRIALS])

        for i in range (self.NUM_TRIALS):#runs over trials
            x_for_interp = self.x[:,i] 
            x_for_interp = x_for_interp[~np.isnan(x_for_interp)] #remove Nan values in the end of cordinates vectors
            y_for_interp = self.y[:,i]
            y_for_interp = y_for_interp[~np.isnan(y_for_interp)]
            fx = interpolate.interp1d(range(x_for_interp.shape[0]),x_for_interp) #creates interpolation function
            fy = interpolate.interp1d(range(y_for_interp.shape[0]),y_for_interp)
            norm_tp_x = np.linspace(0,x_for_interp.shape[0]-1,101) #creates linear space of 101 time points
            norm_tp_y = np.linspace(0,y_for_interp.shape[0]-1,101)
            xnew[:,i] = fx(norm_tp_x) #applies interpolation function on the linear space
            ynew[:,i] = fy(norm_tp_y)

        self.x = xnew
        self.y = ynew

    def rescale(self):
        """
        This function rescales the coordiantes space so that the continue button is in [0,0]
        and the right and left targets are in [1,1] and [-1,1] respectively
        """
        #left_target_x, right_target_x = 445,975
        continue_x = np.mean(self.x[0,:])#calculating the x cordinates for the continue button
        left_subset = self.x[:,self.x[100,:]<continue_x] #subsetting all trials where the left option is chosen
        right_subset = self.x[:,self.x[100,:]>continue_x]
        right_x, left_x = np.mean(right_subset[-1,:]),np.mean(left_subset[-1,:])#calculating the x cordinates for the choices
        self.x -= continue_x #center x coordinates
        self.x  = self.x / ((right_x-left_x)/2) #rescale x coordinates
        continue_y =  np.mean(self.y[0,:])
        targets_y = np.mean(self.y[100,:])
        self.y -=continue_y
        self.y = -self.y / ((continue_y-targets_y))

    def remap_trajectories(self):
        """
        This function remaps all of the trajectories to the right.
        IMPORTANT: The function will only work if you apply the rescale() function first!
        """
        for i in range(self.NUM_TRIALS):
            if self.x[100,i] < 0: ## i.e., if the trajectory ends in the left target
                self.x[:,i] = -self.x[:,i]


    def plot_by_conflict(self):
        ax = plt.figure()
        ax = ax.add_subplot(1,1,1)
        self.app_ind = self.df.index[self.df['Conflict']=='Approach']
        self.avo_ind = self.df.index[self.df['Conflict']=='Avoidance']
        self.x_app = self.x[:,self.app_ind]
        self.x_avo = self.x[:,self.avo_ind]
        self.y_app = self.y[:,self.app_ind]
        self.y_avo = self.y[:,self.avo_ind]
        ax.plot(self.x_app[:,0:42],self.y_app[:,0:42],'--go',label = 'APP-APP',markersize = 5)
        ax.plot(self.x_avo[:,0:42],self.y_avo[:,0:42],'--ro',label = 'AVO-AVO',markersize = 5)
        handles, labels = ax.get_legend_handles_labels()
        temp = {k:v for k,v in zip(labels, handles)}
        ax.legend(temp.values(), temp.keys(), loc='best')
        plt.show()
                

    

    def x_flips(self):
        """
        This function calculates number of x flips trial by trial and save it as a variable 'flips' of the class
        """
        self.flips = []
        for sub in  range (self.NUM_TRIALS):
            bigger, smaller = False, False
            x_count, y_count = 0, 0
            last_i = 0
            for i in range(1,101):
                if self.x[last_i,sub] >= self.x[i,sub]:
                    last_i += 1
                    if not bigger:
                        bigger = True
                        smaller = False
                        x_count += 1
                    else:
                        continue
                if self.x[last_i,sub] < self.x[i,sub]:
                    last_i += 1
                    if not smaller:
                        bigger = False
                        smaller = True
                        x_count += 1
                    else:
                        continue
            self.flips.append(x_count)


    def AUC (self):
        """
        TO DO: this function calculates all area under the curve for the 
        """
        pass

    def max_deviation(self):
        """

        """
        pass
    def calculate_all_measures(self):
        """
        This function calculates the measures (e,g. x flips, max deviation...)
        and saves each measure as a column in the data frame.
        """
        self.x_flips()
        self.df['flips'] = self.flips
        ##TO DO: add additional measures after writing the code for them
        



    
def process_across_subjects(directory):
    """
    This function gets a directory and apply the functions in the above class on all of
    the subjects files in the directory.
    It also creates a unified CSV file of all subjects and saves it in the directory
    """
    df_list = []
    files = os.listdir(directory)
    for sub in range(len(files)):
        if files[sub][0] == '$':
            cur_class = TrajectoryProcessing(directory + "\\" + files[sub])
            cur_class.normalize_time_points()
            cur_class.rescale()
            cur_class.remap_trajectories()
            cur_class.calculate_all_measures()
            cur_class.df['subject_id'] = sub+1
            df_list.append(cur_class.df)
    big_df = pd.concat(df_list)
    big_df.to_csv(directory+'\\all_subjects.csv')
        


path = r"C:\Users\ariel\Desktop\innitial_data"

process_across_subjects(path)

# check = TrajectoryProcessing(path)
# check.normalize_time_points()
# check.rescale()
# check.remap_trajectories()
# #print(check.y[100,:])
# check.x_flips()
# print (check.flips)
# check.plot_by_conflict()
# check.calculate_all_measures()
# # for sub in range (check.NUM_TRIALS):
# #     plt.plot(check.x[:,sub],check.y[:,sub],'--o')
# #     plt.show()

# # plt.plot(check.x[:,0:42],check.y[:,0:42],'--o')
# plt.xlabel('X cordinate')
# plt.ylabel('Y cordinate')
# plt.show()
