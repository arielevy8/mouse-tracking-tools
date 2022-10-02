from tabnanny import check
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import interpolate


class TrajectoryProcessing(object):
    """
    This class gets csv path for a single subject in the experiment, 
    and contain of functions that handle with the preprocessing of the mouse-trajectory data
    and with the extraction of the trajectory-based measures
    """
    def __init__(self,path):
        self.NUM_PRACTICE_TRIALS = 4
        self.NUM_TRIALS = 42
        self.NUM_TIMEPOINTS = 101
        self.df = pd.read_csv (path,index_col=None, header=0) 
        if 'response' in self.df.columns: #if there is a column for subjective difficulty data (as in Study 2), it will be concatenated to the filtered df
            response = self.df['response']
            response = response.dropna() #read only lines with mouse tracking data
            response = response[self.NUM_PRACTICE_TRIALS:] #drop practice trials
        self.df = self.df.dropna(subset = ["x_cord"]) #read only lines with mouse tracking data
        self.df = self.df.iloc[self.NUM_PRACTICE_TRIALS:,] #drop practice trials
        if 'response' in self.df.columns:
            self.df['response'] =   list(response)
        self.df = self.df.reset_index()
        self.x = self.df["x_cord"]
        self.y = self.df["y_cord"]

        self.x = self.x.str.split(',', expand=True)
        self.x = self.x.reset_index(drop=True)
        self.x = self.x.to_numpy() #convert to numpy matrix for future processing
        self.x = self.x.astype(np.float64) #convert type from strings to floats
        self.x = np.transpose(self.x) #transpose for easier processing (now the matrix size is NUM_TIMEPOINTS*NUM_TRIALS)

        self.y = self.y.str.split(',', expand=True)
        self.y = self.y.reset_index(drop=True)
        self.y = self.y.to_numpy()
        self.y = self.y.astype(np.float64)
        self.y = np.transpose(self.y)        

    def normalize_time_points(self):
        """
        This function uses linear interpolation to normalize all of the trajectories to 101 time points from start to finish.
        """ 
        #innitialize matrix
        xnew = np.empty([101,self.NUM_TRIALS]) 
        ynew = np.empty([101,self.NUM_TRIALS])

        for i in range (self.NUM_TRIALS): #run over trials
            x_for_interp = self.x[:,i] 
            x_for_interp = x_for_interp[~np.isnan(x_for_interp)] #remove Nan values in the end of cordinates vectors
            y_for_interp = self.y[:,i]
            y_for_interp = y_for_interp[~np.isnan(y_for_interp)]
            fx = interpolate.interp1d(range(x_for_interp.shape[0]),x_for_interp) #create interpolation function
            fy = interpolate.interp1d(range(y_for_interp.shape[0]),y_for_interp)
            norm_tp_x = np.linspace(0,x_for_interp.shape[0]-1,self.NUM_TIMEPOINTS) #create linear space of 101 time points
            norm_tp_y = np.linspace(0,y_for_interp.shape[0]-1,self.NUM_TIMEPOINTS)
            xnew[:,i] = fx(norm_tp_x) #apply interpolation function on the linear space
            ynew[:,i] = fy(norm_tp_y)

        self.x = xnew
        self.y = ynew

    def rescale(self):
        """
        This function rescales the coordiantes space so that the continue button is in [0,0]
        and the right and left targets are in [1,1.5] and [-1,1.5] respectively
        """
        #left_target_x, right_target_x = 445,975
        self.continue_x = np.mean(self.x[0,:]) #calculate the x cordinates for the continue button
        left_subset = self.x[:,self.x[100,:]<self.continue_x] #subset all trials where the left option is chosen
        right_subset = self.x[:,self.x[100,:]>self.continue_x]
        self.right_x, self.left_x = np.mean(right_subset[-1,:]),np.mean(left_subset[-1,:]) #calculate the x cordinates for the choices
        self.x -= self.continue_x #center x coordinates
        self.x  = self.x / ((self.right_x-self.left_x)/2) #rescale x coordinates
        self.continue_y =  np.mean(self.y[0,:])
        self.targets_y = np.mean(self.y[100,:])
        self.y -=self.continue_y
        self.y = (-self.y / ((self.continue_y-self.targets_y)))*1.5

    def remap_trajectories(self):
        """
        This function remaps all of the trajectories to the right.
        IMPORTANT: The function will only work if you apply the rescale() function first!
        """
        for i in range(self.NUM_TRIALS):
            if self.x[100,i] < 0: #i.e., if the trajectory ends in the left target
                self.x[:,i] = -self.x[:,i]


    def plot_by_condition(self):
        """
        This function plots all of the trajectories of a given subject.
        """
        ax = plt.figure()
        ax = ax.add_subplot(1,1,1)
        self.app_ind = self.df.index[self.df['Condition']==1]
        self.avo_ind = self.df.index[self.df['Condition']==2]
        self.x_app = self.x[:,self.app_ind]
        self.x_avo = self.x[:,self.avo_ind]
        self.y_app = self.y[:,self.app_ind]
        self.y_avo = self.y[:,self.avo_ind]
        ax.plot(self.x_app[:,0:42],self.y_app[:,0:42],'--go',label = 'Condition 1',markersize = 5)
        ax.plot(self.x_avo[:,0:42],self.y_avo[:,0:42],'--ro',label = 'Condition 2',markersize = 5)
        handles, labels = ax.get_legend_handles_labels()
        temp = {k:v for k,v in zip(labels, handles)}
        ax.legend(temp.values(), temp.keys(), loc='best')
        plt.show()

    def agg_by_condition(self):
        """
        This function aggregates all trajectories by their condition - 1 or 2, 
        and creates datasets of aggregated trajectories.  
        """
        self.app_ind = self.df.index[self.df['Condition']==1]
        self.avo_ind = self.df.index[self.df['Condition']==2]
        self.x_app = self.x[:,self.app_ind]
        self.x_avo = self.x[:,self.avo_ind]
        self.y_app = self.y[:,self.app_ind]
        self.y_avo = self.y[:,self.avo_ind]
    

    def get_x_flips(self):
        """
        This function calculates number of x flips trial by trial and saves it as a variable 'flips' of the class.
        """
        self.flips = []
        for trial in  range (self.NUM_TRIALS):
            bigger, smaller = False, False
            x_count= 0
            last_i = 0
            cur_trial_xcor = []
            for i in range(1,self.NUM_TIMEPOINTS):
                
                if self.x[last_i,trial] > self.x[i,trial]:
                    last_i += 1
                    if not bigger:
                        bigger = True
                        smaller = False
                        if i != 1:
                            x_count += 1
                            cur_trial_xcor.append (self.x[last_i,trial])
                    else:
                        continue
                if self.x[last_i,trial] < self.x[i,trial]:
                    last_i += 1
                    if not smaller:
                        bigger = False
                        smaller = True
                        if i != 1:
                            x_count += 1
                            cur_trial_xcor.append (self.x[last_i,trial])
                    else:
                        continue
            self.flips.append(x_count)


    
    def get_RPB(self):
        """
        This funcction calculates the number of times the mouse cursor cross the middle of the X-axis
        """
        self.crosses_y_ap= []
        self.crosses_y_av = [] #initialize two lists for the later visualization
        self.crosses_ycor = []
        self.RPB = []
        for trial  in range (self.NUM_TRIALS):
            crosses = 0
            crosses_cut = 0
            last_i = 0
            cur_crosses_ycor = []
            for i in range(1,self.NUM_TIMEPOINTS):
                if (self.x[last_i,trial] > 0 and self.x[i,trial] < 0) or (self.x[last_i,trial] < 0 and self.x[i,trial] > 0):
                    crosses += 1
                    if self.y[i,trial]<1.5:
                        crosses_cut +=1
                    cur_crosses_ycor.append(self.y[i,trial])
                    if (self.df['Conflict'][trial] == 'Approach'):
                        self.crosses_y_ap.append(self.y[i,trial]) #append the y position of the cross for later visualization
                    elif (self.df['Conflict'][trial] == 'Avoidance'):
                        self.crosses_y_av.append(self.y[i,trial])
                last_i += 1
            self.RPB.append(crosses)
            self.crosses_ycor.append(cur_crosses_ycor)


    def get_AUC (self):
        """
        This function calculates all area under the curve for the trajectories
        """
        self.AUC =[]
        for i in range(self.NUM_TRIALS):
            cur_x = self.x[:,i]
            cur_y = self.y[:,i]
            line_x, line_y = cur_x, 1.5 *cur_x #create a straight line from (0,0) to (1,1.5). specifically, using the trajectory x cordinates to enable integration
            cur_integral = np.trapz(cur_y-line_y,dx = 1/101) #integrate on the distance between the actual trajectory and a straight line
            self.AUC.append(cur_integral)
            
            # #possibility - uncomment this section to visualize the integrated part and compare it to the calculated MD and AUC

            # print('AUC='+str(cur_integral))
            # print('MD=' +str(self.max_deviations[i]))
            # plt.plot(cur_x,cur_y,color = 'r')
            # plt.plot(line_x,line_y)
            # plt.fill_between(cur_x,cur_y,line_y,alpha = 0.4)
            # plt.ylim(0,1.7)
            # plt.show()
            
    def get_max_deviation(self):
        """
        This function calculates the maximal deviation from the actual trajectory to a 
        straight line connecting the starting position and the target.
        IMPORTANT: this function will only work if you apply the rescale and remap functions first.
        """
        self.max_deviations = []
        for i in range (self.NUM_TRIALS):
            line_x, line_y = np.linspace(self.x[0,i],self.x[self.NUM_TIMEPOINTS-1,i],self.NUM_TIMEPOINTS),np.linspace(self.y[0,i],self.y[self.NUM_TIMEPOINTS-1,i],self.NUM_TIMEPOINTS)
            self.line = np.column_stack((line_x, line_y))
            distances =[]
            for j in range (self.NUM_TIMEPOINTS):
                cur_point = np.array([self.x[j,i],self.y[j,i]])
                norm = np.linalg.norm(self.line-cur_point,axis = 1)
                cur_distance = min(norm)
                distances.append (cur_distance)
            self.max_deviations.append(max(distances))

    def calculate_all_measures(self):
        """
        This function calculates the measures (e,g. x flips, max deviation...)
        and saves each measure as a column in the data frame.
        """
        self.get_x_flips()
        self.df['flips'] = self.flips
        self.get_max_deviation()
        self.df['max_deviation'] = self.max_deviations
        self.get_RPB()
        self.df['RPB'] = self.RPB
        self.get_AUC()
        self.df['AUC'] = self.AUC

