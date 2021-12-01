#from os import path
import numpy as np
from numpy.core.fromnumeric import shape
import pandas as pd
import matplotlib.pyplot as plt
from scipy import interpolate


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
        self.x = self.x.astype(np.float)#convert type from strings to floats
        self.x = np.transpose(self.x)#transpose for easier processing (now the matrix size is NUM_TIMEPOINTS*NUM_TRIALS)

        self.y = self.y.str.split(',', expand=True)
        self.y = self.y.reset_index(drop=True)
        self.y = self.y.to_numpy()
        self.y = self.y.astype(np.float)
        self.y = np.transpose(self.y)
        #self.y = self.y[self.NUM_PRACTICE_TRIALS:,] 
        

    def normalize_time_points(self):
        """
        this function uses linear interpolation to normalize all of the trajectories to 101 time points from start to finish.
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

    def plot_by_conflict(self):
        ax = plt.figure()
        ax = ax.add_subplot(1,1,1)
        self.app_ind = self.df.index[self.df['Conflict']=='Approach']
        self.avo_ind = self.df.index[self.df['Conflict']=='Avoidance']
        self.x_app = self.x[:,self.app_ind]
        self.x_avo = self.x[:,self.avo_ind]
        self.y_app = self.y[:,self.app_ind]
        self.y_avo = self.y[:,self.avo_ind]
        ax.plot(self.x_app[:,0:42],-self.y_app[:,0:42],'--go',label = 'APP-APP',markersize = 5)
        ax.plot(self.x_avo[:,0:42],-self.y_avo[:,0:42],'--ro',label = 'AVO-AVO',markersize = 5)
        handles, labels = ax.get_legend_handles_labels()
        temp = {k:v for k,v in zip(labels, handles)}
        ax.legend(temp.values(), temp.keys(), loc='best')
        plt.show()
                

        

    def x_flips(self):
        pass

    







    

  
    

        



path = r"C:\Users\ariel\Desktop\mayacheckmayatest.csv"
check = TrajectoryProcessing(path)
check.normalize_time_points()
check.plot_by_conflict()
plt.plot(check.x[:,0:42],-check.y[:,0:42],'--o')
plt.xlabel('X cordinate')
plt.ylabel('Y cordinate')
plt.show()





# fx = interpolate.interp1d(range(check.x.shape[0]),np.transpose(check.x))
# fy = interpolate.interp1d(range(check.y.shape[0]),np.transpose(check.y))
# xnew = fx(np.linspace(0,check.x.shape[0]-1,101))
# ynew = fy(np.linspace (0,check.y.shape[0]-1,101))
# plt.plot(np.transpose(xnew),-np.transpose(ynew),'--o')
# plt.show()