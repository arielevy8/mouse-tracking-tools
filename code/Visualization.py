import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

class Visualization (object):
    """
    This class gets csv path for the unified dataset of all participants in the experiment,
    and contain of functions that handle with some parts of the data visualization (other
    parts of the data visualization can be found in the R script)
    :Param path: path of the unified dat file
    :Param study_title: string, will be used as the title of the plot
    :Param subjects_to_remove: list of subject numbers to remove from the plot
    """
    def __init__(self, path, output_directory, study_title, first_condition_column, second_condition_column,
                 title_size, labels_size,ticks_size, legend_size, point_size, colormap,
                 subject_to_inspect, num_samples, trajectory_to_inspect, subjects_to_remove =[]):
        self.output_directory = output_directory
        self.NUM_TIMEPOINTS = 100
        self.df = pd.read_csv(path,index_col=None, header=0)
        self.subjects_to_remove = subjects_to_remove
        self.df = self.df[~self.df['subject_id'].isin(self.subjects_to_remove)]
        self.NUM_TRIALS = self.df.shape[0]
        columns_x = ['x_'+str(i) for i in range(self.NUM_TIMEPOINTS)]
        columns_y = ['y_'+str(i) for i in range(self.NUM_TIMEPOINTS)]
        x_df = self.df[columns_x]
        y_df = self.df[columns_y]
        self.x = np.transpose(x_df.to_numpy())
        self.y = np.transpose(y_df.to_numpy())
        self.study_title = study_title
        self.num_subjects = len(self.df['subject_id'].unique())
        self.first_condition_column = first_condition_column
        self.second_condition_column = second_condition_column
        if first_condition_column:
            self.conditions_1 = self.df[first_condition_column].unique()
        else:
            self.conditions_1 = [0]
        if second_condition_column:
            self.conditions_2 = self.df[self.second_condition_column].unique()
        else:
            self.conditions_2 = [0]
        self.title_size = title_size
        self.labels_size = labels_size
        self.ticks_size = ticks_size
        self.legend_size = legend_size
        self.colormap = colormap
        self.subject_to_inspect = subject_to_inspect
        self.num_samples = num_samples
        self.trajectory_to_inspect = trajectory_to_inspect
        self.point_size = point_size
        self.ind = []
        for i in range(len(self.conditions_2)):
            cur_ind = []
            for j in range(len(self.conditions_1)):
                cond_1 = self.conditions_1[j]
                cond_2 = self.conditions_2[i]
                if first_condition_column and second_condition_column:
                    cur_ind.append(self.df.index[(self.df[first_condition_column] == cond_1) &
                                                 (self.df[second_condition_column] == cond_2) &
                                                 (self.df['is_OK'] == True)])
                elif first_condition_column:
                    cur_ind.append(self.df.index[(self.df[first_condition_column] == cond_1) &
                                                 (self.df['is_OK'] == True)])
                elif second_condition_column:
                    cur_ind.append(self.df.index[(self.df[second_condition_column] == cond_2) &
                                                 (self.df['is_OK'] == True)])
                else:
                    cur_ind.append(self.df.index[(self.df['is_OK'] == True)])
            self.ind.append(cur_ind)

    def plot_means(self):
        """
        This function plot the average mouse trajectory in each condition.
        """
        colors = plt.cm.get_cmap(self.colormap)(np.linspace(0, 1, len(self.conditions_1)))
        plt.figure(figsize=(6.4*len(self.conditions_2), 4.8))
        for i in range(len(self.conditions_2)):
            cond_2 = self.conditions_2[i]
            ax = plt.subplot(1, len(self.conditions_2), i+1)
            for j in range(len(self.conditions_1)):
                cond_1 = self.conditions_1[j]
                cur_ind = self.ind[i][j]
                x = self.x[:,cur_ind]
                y = self.y[:,cur_ind]
                mean_x = np.mean(x, axis=1)
                mean_y = np.mean(y, axis=1)
                std_y = np.std(y, axis=1)
                se_y = std_y/np.sqrt(self.num_subjects)
                std_x = np.std(x, axis=1)
                se_x = std_y/np.sqrt(self.num_subjects)
                if type(cond_1)!= str:
                    label = self.first_condition_column + ': ' + str(cond_1)
                elif type(cond_1)==str:
                    label = cond_1
                ax.plot(mean_x, mean_y, '--o', c=colors[j], label=label, markersize=self.point_size)
                ax.fill_between(mean_x, mean_y-se_y, mean_y+se_y, color=colors[j], alpha=0.2,edgecolor = None)
                ax.fill_betweenx(mean_y, mean_x-se_x, mean_x+se_x, color=colors[j], alpha=0.2,edgecolor = None)
                ax.tick_params(labelsize=self.ticks_size)
            if self.first_condition_column:
                ax.legend(fontsize=self.legend_size)
            ax.set_xlim(-1, 1.1)
            ax.set_xlabel('X-coordinate', fontsize=self.labels_size)
            ax.set_ylabel('Y-coordinate', fontsize=self.labels_size)
            if self.second_condition_column:
                ax.set_title(cond_2, fontsize=self.title_size)
            else:
                ax.set_title(self.study_title, fontsize=self.title_size)
        plt.savefig(self.output_directory + os.sep + 'Average trajectories',
                    dpi=300)
        plt.show()

    def plot_subject(self):
        """
        This function plots all trajectories of a given subject
        :Param subject_id: int, the index of the subject
        """
        if self.subject_to_inspect:
            subject_ind = self.df.index[self.df['subject_id']==self.subject_to_inspect]
            colors = plt.cm.get_cmap(self.colormap)(np.linspace(0, 1, len(self.conditions_1)))
            plt.figure(figsize=(6.4*len(self.conditions_2), 4.8))
            for i in range(len(self.conditions_2)):
                cond_2 = self.conditions_2[i]
                ax = plt.subplot(1, len(self.conditions_2), i+1)
                for j in range(len(self.conditions_1)):
                    cond_1 = self.conditions_1[j]
                    cur_ind = self.ind[i][j]
                    sub_cur_ind = subject_ind.intersection(cur_ind)
                    x = self.x[:, sub_cur_ind]
                    y = self.y[:, sub_cur_ind]
                    if type(cond_1) != str:
                        label = self.first_condition_column+': ' +str(cond_1)
                    elif type(cond_1) == str:
                        label = cond_1
                    ax.plot(x, y, '--o', c=colors[j], label=label, markersize=self.point_size)
                    ax.tick_params(labelsize=self.ticks_size)
                if self.first_condition_column:
                    handles, labels = ax.get_legend_handles_labels()
                    temp = {k: v for k, v in zip(labels, handles)}
                    ax.legend(temp.values(), temp.keys(), loc='best',fontsize=self.legend_size)
                #ax.set_xlim(-1, 1.1)
                ax.set_xlabel('X-coordinate', fontsize=self.labels_size)
                ax.set_ylabel('Y-coordinate', fontsize=self.labels_size)
                if self.second_condition_column:
                    ax.set_title(('Subject: '+str(self.subject_to_inspect)+', Condition: '+cond_2),
                                 fontsize=self.title_size)
                else:
                    ax.set_title(('Subject: '+str(self.subject_to_inspect)), fontsize=self.title_size)
            plt.savefig(self.output_directory+os.sep+'Subject '+str(self.subject_to_inspect)+' trajectories',
                        dpi=300)
            plt.show()

    # def plot_subject_mean(self, subject_id):
    #     """
    #     This function plots the mean of the trajectories of a given subject.
    #     :Param subject_id: int, the index of the subject
    #     """
    #     self.conditions = self.df[self.first_condition_column].unique()
    #     colors = plt.cm.rainbow(np.linspace(0, 1, len(self.conditions)))
    #     counter = 0
    #     subject_ind = self.df.index[self.df['subject_id']==subject_id]
    #     for cond in self.conditions:
    #         cond_ind = self.df.index[self.df[self.first_condition_column]==cond]
    #         ind = subject_ind.intersection(cond_ind)
    #         x = self.x[:,ind]
    #         y = self.y[:,ind]
    #         mean_x = np.mean(x,axis=1)
    #         mean_y = np.mean(y,axis=1)
    #         std_y = np.std(y,axis=1)
    #         std_x = np.std(x,axis=1)
    #         if type(cond)!= str:
    #             label = 'Condition: '+ str(cond)
    #         elif type(cond)==str:
    #             label = cond
    #         plt.plot(mean_x,mean_y,'--o',c = colors[counter],label = label,markersize = 5)
    #         plt.fill_between(mean_x, mean_y-std_y, mean_y+std_y, color=colors[counter], alpha=0.2,edgecolor = None)
    #         plt.fill_betweenx(mean_y, mean_x-std_x, mean_x+std_x, color=colors[counter], alpha=0.2,edgecolor = None)
    #         counter +=1
    #     plt.legend(fontsize="x-large")
    #     plt.xlim(-1,1.1)
    #     plt.xlabel('X coordinate',fontsize = 12)
    #     plt.ylabel('Y coordinate',fontsize = 12)
    #     plt.title(self.study_title + ', subject number '+str(subject_id))
    #     plt.show()
    #
    # def plot_all_subjects (self):
    #     #fig, axs = plt.subplots(12, 5)
    #     plt.figure(figsize=(24, 32))
    #     counter = 1
    #     for i in np.sort(self.df['subject_id'].unique()):
    #         ax = plt.subplot(10, 7, counter)
    #         self.conditions = ['AV-AV','AP-AP']#self.df['Conflict'].unique()
    #         colors = ['r', 'g']
    #         counter_con = 0
    #         subject_ind = self.df.index[self.df['subject_id'] == i]
    #         for cond in self.conditions:
    #             cond_ind = self.df.index[self.df['Conflict'] == cond]
    #             ind = subject_ind.intersection(cond_ind)
    #             x = self.x[:, ind]
    #             y = self.y[:, ind]
    #             ax.plot(x, y, '--o', c=colors[counter_con], label=cond, markersize=0.05)
    #             counter_con += 1
    #             ax.title.set_text('Participant '+str(i))
    #             ax.axes.xaxis.set_ticklabels([])
    #             ax.axes.yaxis.set_ticklabels([])
    #         counter += 1
    #         handles, labels = ax.get_legend_handles_labels()
    #         temp = {k: v for k, v in zip(labels, handles)}
    #     #ax.legend(temp.values(), temp.keys(), loc='best')
    #     plt.show()
    #
    # def plot_trajectories_sample(self,num_traj):
    #     """
    #     This function plots a sample of trajectories
    #     :Param num_traj: number of trajectory to sample in each condition
    #     """
    #     ax = plt.figure()
    #     ax = ax.add_subplot(1,1,1)
    #     self.conditions = self.df[self.first_condition_column].unique()
    #     colors = plt.cm.rainbow(np.linspace(0, 1, len(self.conditions)))
    #     counter = 0
    #     for cond in self.conditions:
    #         ind = self.df.index[(self.df[self.first_condition_column] == cond) & (self.df['is_OK'] == True)]
    #         x = self.x[:,ind]
    #         y = self.y[:,ind]
    #         ind_subset = np.random.choice (ind.shape[0],num_traj)
    #         x = x[:,ind_subset]
    #         y = y[:,ind_subset]
    #         ax.plot(x,y,'--o',c = colors[counter],label = cond,markersize = 5)
    #         counter +=1
    #     handles, labels = ax.get_legend_handles_labels()
    #     temp = {k:v for k,v in zip(labels, handles)}
    #     ax.legend(temp.values(), temp.keys(), loc='best')
    #     plt.xlabel('X coordinate',fontsize = 12)
    #     plt.ylabel('Y coordinate',fontsize = 12)
    #     plt.title(self.study_title+', '+str(num_traj)+' trajectories were sampled')
    #     plt.show()

    def examine_certain_trajectory(self, subject_id, trial):
        """
        This function plot a specific trajectory along all its measures
        :Param subject_id: int, subject number
        :Param trial: int, trial number
        """
        pass
