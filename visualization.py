import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from seaborn import heatmap


class Visualization (object):
    """
    This class gets csv path for a the unified dataset of all participants in the experiment, 
    and contain of functions that handle with some parts of the data visualiztion (other
    parts of the data visualization can be found in the R script)
    """
    def __init__(self,path,subjects_to_remove,study_title):
        
        self.NUM_TIMEPOINTS = 101
        self.df = pd.read_csv (path,index_col=None, header=0) 
        self.NUM_TRIALS = self.df.shape[0]
        columns_x = ['x_'+str (i) for i in range (101)]
        columns_y = ['y_'+str (i) for i in range (101)]
        x_df = self.df[columns_x]
        y_df = self.df[columns_y]
        self.x = np.transpose(x_df.to_numpy())
        self.y = np.transpose(y_df.to_numpy())
        self.study_title = study_title
        self.subjects_to_remove = subjects_to_remove
        
    def remove_subjects(self):
        
        # good_subjects_ind = self.df.index[~self.df['subject_id'].isin(self.subjects_to_remove)]
        # # self.x = self.x[:,good_subjects_ind]
        # # self.y = self.y[:,good_subjects_ind]
        self.df = self.df[~self.df['subject_id'].isin(self.subjects_to_remove)]
        

    def plot_means_by_cond(self):
        """
        This function plot the average mouse trajectory in each condition.
        """
        mean_x_app = np.mean(self.x_app,axis=1)
        mean_y_app = np.mean(self.y_app,axis=1)
        mean_x_avo = np.mean(self.x_avo,axis=1)
        mean_y_avo = np.mean(self.y_avo,axis=1)
        plt.plot(mean_x_app,mean_y_app,'--go',label = 'AP-AP',markersize=3)
        plt.plot(mean_x_avo,mean_y_avo,'--ro',label = 'AV-AV',markersize=3)
        plt.legend(fontsize="x-large")
        plt.xlim(-1,1.1)
        plt.xlabel('X-coordinate',fontsize = 12)
        plt.ylabel('Y-coordinate',fontsize = 12)
        plt.title(self.study_title)
        plt.show()

    def plot_trajectories_sample(self,num_traj):
        """
        This function plots a sample of trajectories 
        """
        cur_idx_app = np.random.choice (self.x_app.shape[1],num_traj)
        cur_idx_avo = np.random.choice (self.x_avo.shape[1],num_traj)
        subset_x_app = self.x_app[:,cur_idx_app]
        subset_y_app = self.y_app[:,cur_idx_app]
        subset_x_avo = self.x_avo[:,cur_idx_app]
        subset_y_avo = self.y_avo[:,cur_idx_app]
        plt.plot (subset_x_app,subset_y_app,'--go',label = 'AP-AP',alpha = 0.6)
        plt.plot (subset_x_avo,subset_y_avo,'--ro',label = 'AV-AV',alpha = 0.6)
        plt.xlabel('X-coordinate',fontsize = 12)
        plt.ylabel('Y-coordinate',fontsize = 12)
        plt.title(self.study_title)
        plt.show()