import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import interpolate
import math


class Preprocessing(object):
    """
    This class gets csv path for a single subject in the experiment, 
    and contain of functions that handle with the preprocessing of the mouse-trajectory data
    and with the extraction of the trajectory-based measures
    :Param num_practice_trials:int, number of practice trials (trials with mouse tracking data that are
    to be ignored in the analysis)
    :Param num_trials: int, number of non-practice trials to analyze
    """
    def __init__(self,path,num_practice_trials,num_trials,x_cord_column,y_cord_column):
        self.isOK = True
        self.NUM_PRACTICE_TRIALS = num_practice_trials
        self.NUM_TRIALS = num_trials
        self.NUM_TIMEPOINTS = 100
        self.df = pd.read_csv (path,index_col=None, header=0) 
        self.df = self.df.dropna(subset = [x_cord_column])  # read only lines with mouse tracking data
        self.df = self.df.iloc[self.NUM_PRACTICE_TRIALS:,]  # drop practice trials
        self.df = self.df.reset_index()
        self.x = self.df[x_cord_column]
        self.y = self.df[y_cord_column]

        self.x = self.x.str.split(',', expand=True)
        self.x = self.x.reset_index(drop=True)
        self.x = self.x.to_numpy()  # convert to numpy matrix for future processing
        self.x = self.x.astype(np.float64)  # convert type from strings to floats
        self.x = np.transpose(self.x)  # transpose for easier processing (now matrix size is NUM_TIMEPOINTS*NUM_TRIALS)

        self.y = self.y.str.split(',', expand=True)
        self.y = self.y.reset_index(drop=True)
        self.y = self.y.to_numpy()
        self.y = self.y.astype(np.float64)
        self.y = np.transpose(self.y)
        # check input properties, and return "isOK = False" when the recorded mouse tracking data is incomplete
        if (self.x.shape[1]) != self.NUM_TRIALS or self.y.shape[1] != self.NUM_TRIALS:  # if data is missing for trials
            self.isOK = False
        else:
            for i in range(self.NUM_TRIALS):  # run over trials and check if there are enough recorded timepoints
                cur_x = self.x[:,i]
                num_recorded_timepoints = cur_x[~np.isnan(cur_x)].shape[0]
                if num_recorded_timepoints < 2:
                    self.isOK = False
        if not self.isOK:
            print('This participant did not provide mouse-data, and thus can not be processed.' +
                  'This might be because he completed the experiment without using a mouse')
        print(self.x.shape)

    def normalize_time_points(self):
        """
        This function uses linear interpolation to normalize all of the trajectories to 100 time points from start to finish.
        """ 
        #innitialize matrix
        xnew = np.empty([self.NUM_TIMEPOINTS,self.NUM_TRIALS]) 
        ynew = np.empty([self.NUM_TIMEPOINTS,self.NUM_TRIALS])

        for i in range (self.NUM_TRIALS): #run over trials
            x_for_interp = self.x[:,i] 
            x_for_interp = x_for_interp[~np.isnan(x_for_interp)] #remove Nan values in the end of cordinates vectors
            y_for_interp = self.y[:,i]
            y_for_interp = y_for_interp[~np.isnan(y_for_interp)]
            fx = interpolate.interp1d(range(x_for_interp.shape[0]),x_for_interp) #create interpolation function
            fy = interpolate.interp1d(range(y_for_interp.shape[0]),y_for_interp)
            norm_tp_x = np.linspace(0,x_for_interp.shape[0]-1,self.NUM_TIMEPOINTS) #create linear space of 100 time points
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
        self.continue_x = np.mean(self.x[0,:])#calculating the x cordinates for the continue button
        left_subset = self.x[:,self.x[self.NUM_TIMEPOINTS-1,:]<self.continue_x] #subsetting all trials where the left option is chosen
        right_subset = self.x[:,self.x[self.NUM_TIMEPOINTS-1,:]>self.continue_x]
        self.right_x, self.left_x = np.mean(right_subset[-1,:]),np.mean(left_subset[-1,:])#calculating the x cordinates for the choices
        self.x -= self.continue_x #center x coordinates
        self.x  = self.x / ((self.right_x-self.left_x)/2) #rescale x coordinates
        self.continue_y =  np.mean(self.y[0,:])
        self.targets_y = np.mean(self.y[self.NUM_TIMEPOINTS-1,:])
        self.y -=self.continue_y
        self.y = (-self.y / ((self.continue_y-self.targets_y)))*1.5

    def remap_trajectories(self):
        """
        This function remaps all of the trajectories to the right.
        IMPORTANT: The function will only work if you apply the rescale() function first!
        """
        for i in range(self.NUM_TRIALS):
            if self.x[self.NUM_TIMEPOINTS-1,i] < 0: #i.e., if the trajectory ends in the left target
                self.x[:,i] = -self.x[:,i]

    def get_x_flips(self):
        """
        This function calculates number of x flips trial by trial and saves it as a variable 'flips' of the class.
        """
        self.flips = []
        for trial in range(self.NUM_TRIALS):
            bigger, smaller = False, False
            x_count = 0
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
        self.RPB = []
        for trial in range(self.NUM_TRIALS):
            crosses = 0
            crosses_cut = 0
            last_i = 0
            cur_crosses_ycor = []
            for i in range(1,self.NUM_TIMEPOINTS):
                if (self.x[last_i, trial] > 0 > self.x[i, trial]) or (self.x[last_i, trial] < 0 < self.x[i, trial]):
                    crosses += 1
                last_i += 1
            self.RPB.append(crosses)

    def get_AUC(self):
        """
        This function calculates all area under the curve for the trajectories
        """
        self.AUC = []
        for i in range(self.NUM_TRIALS):
            cur_x = self.x[:, i]
            cur_y = self.y[:, i]
            line_x, line_y = cur_x, 1.5*cur_x  # create a straight line from (0,0) to (1,1.5).
            # integrate on the distance between the actual trajectory and a straight line
            cur_integral = np.trapz(cur_y-line_y, dx=1/self.NUM_TIMEPOINTS)
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
        for i in range(self.NUM_TRIALS):
            line_x, line_y = (np.linspace(self.x[0, i], self.x[self.NUM_TIMEPOINTS-1, i], self.NUM_TIMEPOINTS),
                              np.linspace(self.y[0, i], self.y[self.NUM_TIMEPOINTS-1, i], self.NUM_TIMEPOINTS))
            self.line = np.column_stack((line_x, line_y))
            distances = []
            for j in range(self.NUM_TIMEPOINTS):
                cur_point = np.array([self.x[j, i], self.y[j, i]])
                norm = np.linalg.norm(self.line-cur_point, axis=1)
                cur_distance = min(norm)
                distances.append(cur_distance)
            self.max_deviations.append(max(distances))

    def get_initiation_angle(self):
        """
        This function calculates the angle of the starting movement of the mouse trajectory relative to the y-axis
        """
        self.initiation_angle = []
        self.initiation_correspondence = []
        point_of_angle = 10
        for trial in range(self.NUM_TRIALS):
            # calculate angle of the beginning of trajectory from the vector [1,0](x-axis).
            # see https://stackoverflow.com/questions/42258637/how-to-know-the-angle-between-two-vectors
            angle = math.atan2(self.y[0, trial]-self.y[point_of_angle, trial],
                               self.x[point_of_angle, trial]-self.x[0, trial])
            angle = math.degrees(angle)
            angle = abs(angle)
            self.initiation_angle.append(angle)
            self.initiation_correspondence.append(angle < 90)

            # # uncomment the next lines in order to plot and check the measure validity.
            # plt.plot(self.x[:,trial],self.y[:,trial],'--o')
            # plt.plot([self.x[0,trial],self.x[point_of_angle,trial]],[self.y[0,trial],self.y[point_of_angle,trial]])
            # plt.title(angle)
            # plt.show()

    def calculate_all_measures(self):
        """
        This function calculates the measures (e,g. x flips, max deviation...)
        and saves each measure as a column in the data frame.
        """
        self.df['is_OK'] = self.isOK
        if self.isOK:
            self.get_x_flips()
            self.df['flips'] = self.flips
            self.get_max_deviation()
            self.df['max_deviation'] = self.max_deviations
            self.get_RPB()
            self.df['RPB'] = self.RPB
            self.get_AUC()
            self.df['AUC'] = self.AUC
            self.get_initiation_angle()
            self.df['initiation_angle'] = self.initiation_angle
            self.df['initiation_correspondence'] = self.initiation_correspondence
        else:  # if data is not ok, fill all columns with nan
            self.df['flips'] = (np.full([self.df.shape[0]],np.nan))
            self.df['max_deviation'] = (np.full([self.df.shape[0]],np.nan))
            self.df['RPB'] = (np.full([self.df.shape[0]],np.nan))
            self.df['AUC'] = (np.full([self.df.shape[0]],np.nan))
            self.df['initiation_angle'] = (np.full([self.df.shape[0]],np.nan))
            self.df['initiation_correspondence'] = (np.full([self.df.shape[0]],np.nan))



# exmp = Preprocessing(r'C:\Users\ariel\Desktop\github mouse tracking\example_data\1.csv',4,42)
# exmp.normalize_time_points()
# exmp.rescale()
# exmp.remap_trajectories()
# exmp.plot_by_condition()