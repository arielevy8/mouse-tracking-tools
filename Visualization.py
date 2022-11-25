import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from seaborn import heatmap


class Visualization (object):
    """
    This class gets csv path for a the unified dataset of all participants in the experiment, 
    and contain of functions that handle with some parts of the data visualiztion (other
    parts of the data visualization can be found in the R script)
    :Param path: path of the unified dat file
    :Param study_title: string, will be used as the title of the plot
    :Param subjects_to_remove: list of subject numbers to remove from the plot
    """
    def __init__(self,path,study_title,subjects_to_remove =[]):
        
        self.NUM_TIMEPOINTS = 100
        self.df = pd.read_csv (path,index_col=None, header=0) 
        self.subjects_to_remove = subjects_to_remove
        self.df = self.df[~self.df['subject_id'].isin(self.subjects_to_remove)]
        self.NUM_TRIALS = self.df.shape[0]
        columns_x = ['x_'+str (i) for i in range (self.NUM_TIMEPOINTS)]
        columns_y = ['y_'+str (i) for i in range (self.NUM_TIMEPOINTS)]
        x_df = self.df[columns_x]
        y_df = self.df[columns_y]
        self.x = np.transpose(x_df.to_numpy())
        self.y = np.transpose(y_df.to_numpy())
        self.study_title = study_title
        self.num_subjects = len(self.df['subject_id'].unique())

        

    def plot_means(self):
        """
        This function plot the average mouse trajectory in each condition.
        """
        self.conditions = self.df['Condition'].unique()
        colors = plt.cm.rainbow(np.linspace(0, 1, len(self.conditions)))
        counter = 0
        for cond in self.conditions:
            ind = self.df.index[self.df['Condition']==cond]
            x = self.x[:,ind]
            y = self.y[:,ind]
            mean_x = np.mean(x,axis=1)
            mean_y = np.mean(y,axis=1)
            std_y = np.std(y,axis=1)
            se_y = std_y/np.sqrt(self.num_subjects)
            std_x = np.std(x,axis=1)
            se_x = std_y/np.sqrt(self.num_subjects)
            if type(cond)!= str:
                label = 'Condition: '+ str(cond)
            elif type(cond)==str:
                label = 'Condition: '+ cond
            plt.plot(mean_x,mean_y,'--o',c = colors[counter],label = label,markersize = 5)
            plt.fill_between(mean_x, mean_y-se_y, mean_y+se_y, color=colors[counter], alpha=0.2,edgecolor = None)
            plt.fill_betweenx(mean_y, mean_x-se_x, mean_x+se_x, color=colors[counter], alpha=0.2,edgecolor = None)
            counter +=1
        plt.legend(fontsize="x-large")
        plt.xlim(-1,1.1)
        plt.xlabel('X-coordinate',fontsize = 12)
        plt.ylabel('Y-coordinate',fontsize = 12)
        plt.title(self.study_title)
        plt.show()

    def plot_trajectories_sample(self,num_traj):
        """
        This function plots a sample of trajectories 
        Param :num_traj: number of trajectory to sample in each condition 
        """
        ax = plt.figure()
        ax = ax.add_subplot(1,1,1)
        self.conditions = self.df['Condition'].unique()
        colors = plt.cm.rainbow(np.linspace(0, 1, len(self.conditions)))
        counter = 0
        for cond in self.conditions:
            ind = self.df.index[self.df['Condition']==cond]
            x = self.x[:,ind]
            y = self.y[:,ind]
            ind_subset = np.random.choice (ind.shape[0],num_traj)
            x = x[:,ind_subset]
            y = y[:,ind_subset]
            ax.plot(x,y,'--o',c = colors[counter],label = cond,markersize = 5)
            counter +=1
        handles, labels = ax.get_legend_handles_labels()
        temp = {k:v for k,v in zip(labels, handles)}
        ax.legend(temp.values(), temp.keys(), loc='best')
        plt.xlabel('X coordinate',fontsize = 12)
        plt.ylabel('Y coordinate',fontsize = 12)
        plt.title(self.study_title+', '+str(num_traj)+' trajectories were sampled')
        plt.show()


    def plot_subject(self, subject_id):
        """
        This function plots all of the trajectories of a given subject.
        :Param subject_id: int, the index of the subject
        """
        ax = plt.figure()
        ax = ax.add_subplot(1,1,1)
        self.conditions = self.df['Condition'].unique()
        colors = plt.cm.rainbow(np.linspace(0, 1, len(self.conditions)))
        counter = 0
        subject_ind = self.df.index[self.df['subject_id']==subject_id]
        for cond in self.conditions:
            cond_ind = self.df.index[self.df['Condition']==cond]
            ind = subject_ind.intersection(cond_ind)
            x = self.x[:,ind]
            y = self.y[:,ind]
            ax.plot(x,y,'--o',c = colors[counter],label = cond,markersize = 5)
            counter +=1
        handles, labels = ax.get_legend_handles_labels()
        temp = {k:v for k,v in zip(labels, handles)}
        ax.legend(temp.values(), temp.keys(), loc='best')
        plt.xlabel('X coordinate',fontsize = 12)
        plt.ylabel('Y coordinate',fontsize = 12)
        plt.title(self.study_title + ', subject number '+str(subject_id))
        plt.show()

    def plot_subject_mean(self, subject_id):
        """
        This function plots the mean of the trajectories of a given subject.
        :Param subject_id: int, the index of the subject
        """
        self.conditions = self.df['Condition'].unique()
        colors = plt.cm.rainbow(np.linspace(0, 1, len(self.conditions)))
        counter = 0
        subject_ind = self.df.index[self.df['subject_id']==subject_id]
        for cond in self.conditions:
            cond_ind = self.df.index[self.df['Condition']==cond]
            ind = subject_ind.intersection(cond_ind)
            x = self.x[:,ind]
            y = self.y[:,ind]
            mean_x = np.mean(x,axis=1)
            mean_y = np.mean(y,axis=1)
            std_y = np.std(y,axis=1)
            std_x = np.std(x,axis=1)
            if type(cond)!= str:
                label = 'Condition: '+ str(cond)
            elif type(cond)==str:
                label = 'Condition: '+ cond
            plt.plot(mean_x,mean_y,'--o',c = colors[counter],label = label,markersize = 5)
            plt.fill_between(mean_x, mean_y-std_y, mean_y+std_y, color=colors[counter], alpha=0.2,edgecolor = None)
            plt.fill_betweenx(mean_y, mean_x-std_x, mean_x+std_x, color=colors[counter], alpha=0.2,edgecolor = None)
            counter +=1
        plt.legend(fontsize="x-large")
        plt.xlim(-1,1.1)
        plt.xlabel('X coordinate',fontsize = 12)
        plt.ylabel('Y coordinate',fontsize = 12)
        plt.title(self.study_title + ', subject number '+str(subject_id))
        plt.show()

