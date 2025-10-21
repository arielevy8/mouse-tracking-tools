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
    normalized_x = 1
    normalized_y = 1.5
    def __init__(self,path,num_practice_trials,num_trials,x_cord_column,y_cord_column, response_column = "", columns_to_preserve = []):
        self.isOK = True
        self.normalized_x = 1
        self.normalized_y = 1.5
        self.max_length = 0
        self.NUM_PRACTICE_TRIALS = num_practice_trials
        self.NUM_TRIALS = num_trials
        self.NUM_TIMEPOINTS = 101
        self.x_cord_column = x_cord_column
        self.y_cord_column = y_cord_column
        csv = pd.read_csv (path,index_col=None, header=0)
        
        # Smart filtering: keep rows with trajectory data OR rows with data in columns_to_preserve
        if columns_to_preserve:
            # Keep rows that have trajectory data OR have data in any of the preserve columns
            has_trajectory = csv[x_cord_column].notna()
            has_preserve_data = csv[columns_to_preserve].notna().any(axis=1)
            rows_to_keep = has_trajectory | has_preserve_data
            self.df = csv[rows_to_keep].copy()
        else:
            # Default behavior: only keep rows with trajectory data
            self.df = csv.dropna(subset = [x_cord_column]).copy()
        
        self.df = self.df.iloc[self.NUM_PRACTICE_TRIALS:,]  # drop practice trials
        self.df = self.df.reset_index(drop=True)
        
        # Track which rows have trajectory data vs non-trajectory data
        self.trajectory_rows = self.df[x_cord_column].notna().values
        self.num_trajectory_rows = self.trajectory_rows.sum()
        if response_column != "": #  if there is response
            self.df['explicit_slider'] = self.add_slider_data(csv,response_column)
        
        # Only process x/y coordinates for rows that have trajectory data
        trajectory_df = self.df[self.trajectory_rows]
        self.x = trajectory_df[x_cord_column]
        self.y = trajectory_df[y_cord_column]
        self.x = self.x.str.split(',', expand=True)
        self.x = self.x.reset_index(drop=True)
        self.x = self.x.to_numpy()  # convert to numpy matrix for future processing
        self.x = self.x.astype(np.float64)  # convert type from strings to floats
        self.x = np.transpose(self.x)  # transpose for easier processing (now matrix size is NUM_TIMEPOINTS*NUM_TRAJECTORY_ROWS)

        self.y = self.y.str.split(',', expand=True)
        self.y = self.y.reset_index(drop=True)
        self.y = self.y.to_numpy()
        self.y = self.y.astype(np.float64)
        self.y = np.transpose(self.y)

    def get_coordinate_arrays(self):
        """
        Create full coordinate arrays matching the dataframe shape.
        Trajectory rows get interpolated coordinates, non-trajectory rows get NaN.
        Returns: (x_full, y_full) where each has shape (NUM_TIMEPOINTS, total_rows)
        """
        # Always return arrays matching dataframe shape
        x_full = np.full([self.NUM_TIMEPOINTS, self.df.shape[0]], np.nan)
        y_full = np.full([self.NUM_TIMEPOINTS, self.df.shape[0]], np.nan)

        # If subject is valid and has trajectory data, fill in the coordinates
        if self.isOK and hasattr(self, 'x') and hasattr(self, 'y') and self.x is not None and self.y is not None:
            # Fill in trajectory row coordinates
            trajectory_indices = np.where(self.trajectory_rows)[0]
            if len(trajectory_indices) > 0:
                x_full[:, trajectory_indices] = self.x
                y_full[:, trajectory_indices] = self.y

        return x_full, y_full
    def add_slider_data (self, csv, response_column):
        """
        This function adds the slider information that comes after each trial to the data frame
        """
        response = csv.dropna(subset=[response_column])
        response = response['response']
        response = response.dropna().tolist()
        response = response[self.NUM_PRACTICE_TRIALS:]  # drop practice trials
        response = [x/100 for x in response]
        return response

    def normalize_time_points(self):
        """
        This function uses linear interpolation to normalize all of the trajectories to 100 time points from start to finish.
        """
        #innitialize matrix
        xnew = np.empty([self.NUM_TIMEPOINTS,self.num_trajectory_rows])
        ynew = np.empty([self.NUM_TIMEPOINTS,self.num_trajectory_rows])

        for i in range (self.num_trajectory_rows): #run over trajectory trials
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
        and the right and left targets are where normalized_x (plus and minus) and normalized_y are.
        default and recommended is - [1,1.5] and [-1,1.5] respectively
        """

        self.continue_x = np.mean(self.x[0,:])#calculating the x cordinates for the continue button
        left_subset = self.x[:,self.x[self.NUM_TIMEPOINTS-1,:]<self.continue_x] #subsetting all trials where the left option is chosen
        right_subset = self.x[:,self.x[self.NUM_TIMEPOINTS-1,:]>self.continue_x]
        self.right_x, self.left_x = np.mean(right_subset[-1,:]),np.mean(left_subset[-1,:])#calculating the x cordinates for the choices
        self.x -= self.continue_x #center x coordinates
        self.x  = (self.x / ((self.right_x-self.left_x)/2))*self.normalized_x #rescale x coordinates
        self.continue_y =  np.mean(self.y[0,:])
        self.targets_y = np.mean(self.y[self.NUM_TIMEPOINTS-1,:])
        self.y -=self.continue_y
        self.y = (-self.y / ((self.continue_y-self.targets_y)))*self.normalized_y

    def remap_trajectories(self):
        """
        This function remaps all of the trajectories to the right.
        IMPORTANT: The function will only work if you apply the rescale() function first!
        """
        for i in range(self.num_trajectory_rows):
            if self.x[self.NUM_TIMEPOINTS-1,i] < 0: #i.e., if the trajectory ends in the left target
                self.x[:,i] = -self.x[:,i]

    def get_x_flips(self):
        """
        This function calculates number of x flips trial by trial and saves it as a variable 'flips' of the class.
        """
        self.flips = []
        for trial in range(self.num_trajectory_rows):
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
        for trial in range(self.num_trajectory_rows):
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
        for i in range(self.num_trajectory_rows):
            cur_x = self.x[:, i]
            cur_y = self.y[:, i]
            line_x, line_y = self.normalized_x*cur_x, self.normalized_y *cur_x  # create a straight line from (0,0) to the normalized location (default and recommended - 1,1.5).
            # integrate on the distance between the actual trajectory and a straight line
            cur_integral = np.trapz(cur_y-line_y, dx=1/self.NUM_TIMEPOINTS)
            self.AUC.append(cur_integral)

            #possibility - uncomment this section to visualize the integrated part and compare it to the calculated MD and AUC

            #print('AUC='+str(cur_integral))
            #print('MD=' +str(self.max_deviations[i]))
            #plt.plot(cur_x,cur_y,color = 'r')
            #plt.plot(line_x,line_y)
            #plt.fill_between(cur_x,cur_y,line_y,alpha = 0.4)
            #plt.ylim(0,1.7)
            #plt.show()

    def get_max_deviation(self):
        """
        This function calculates the maximal deviation from the actual trajectory to a
        straight line connecting the starting position and the target.
        IMPORTANT: this function will only work if you apply the rescale and remap functions first.
        """
        self.max_deviations = []
        for i in range(self.num_trajectory_rows):
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
        for trial in range(self.num_trajectory_rows):
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
    def measure_trajectory_length(self):
      """
        This function measures the length of the trajectory course for each trial.
        note that it essential to rescale the data before using this function!
      """
      self.length = []
      for j in range (self.num_trajectory_rows):
        length = 0
        #every row is in size of the longest row where all the extra cells are nan
        for i in range(len (self.x[:,j])-1):
            #finish when the values become nan
         #   if (np.isnan(self.x[i + 1,j])):
         #     continue
            length += math.sqrt((self.x[i, j] - self.x[i + 1,j]) ** 2 + (self.y[i, j] - self.y[i+1, j]) ** 2)
        self.length.append(length)
    def calculate_all_measures(self):
        """
        This function calculates the measures (e,g. x flips, max deviation...)
        and saves each measure as a column in the data frame.
        For trajectory rows: calculates all measures
        For non-trajectory rows: fills with NaN
        """
        self.df['is_OK'] = self.isOK
        if self.isOK:
            # Calculate measures for trajectory rows only
            self.get_x_flips()
            self.get_max_deviation()
            self.get_RPB()
            self.get_AUC()
            self.get_initiation_angle()
            self.measure_trajectory_length()
            
            # Calculate the real minimum trajectory length for each trajectory trial
            real_min_lengths = []
            for i in range(self.num_trajectory_rows):
                start_x = self.x[0, i]
                start_y = self.y[0, i]
                end_x = self.x[self.NUM_TIMEPOINTS-1, i]
                end_y = self.y[self.NUM_TIMEPOINTS-1, i]
                real_min_length = math.sqrt((end_x - start_x) ** 2 + (end_y - start_y) ** 2)
                real_min_lengths.append(real_min_length)
            
            # Create arrays for all rows (trajectory + non-trajectory), filled with NaN
            flips_all = np.full(self.df.shape[0], np.nan)
            max_dev_all = np.full(self.df.shape[0], np.nan)
            rpb_all = np.full(self.df.shape[0], np.nan)
            auc_all = np.full(self.df.shape[0], np.nan)
            init_angle_all = np.full(self.df.shape[0], np.nan)
            init_corr_all = np.full(self.df.shape[0], np.nan)
            traj_length_all = np.full(self.df.shape[0], np.nan)
            real_min_all = np.full(self.df.shape[0], np.nan)
            
            # Fill in values only for trajectory rows
            trajectory_indices = np.where(self.trajectory_rows)[0]
            flips_all[trajectory_indices] = self.flips
            max_dev_all[trajectory_indices] = self.max_deviations
            rpb_all[trajectory_indices] = self.RPB
            auc_all[trajectory_indices] = self.AUC
            init_angle_all[trajectory_indices] = self.initiation_angle
            init_corr_all[trajectory_indices] = self.initiation_correspondence
            traj_length_all[trajectory_indices] = self.length
            real_min_all[trajectory_indices] = real_min_lengths
            
            # Assign to dataframe
            self.df['flips'] = flips_all
            self.df['max_deviation'] = max_dev_all
            self.df['RPB'] = rpb_all
            self.df['AUC'] = auc_all
            self.df['initiation_angle'] = init_angle_all
            self.df['initiation_correspondence'] = init_corr_all
            self.df['trajectory_length'] = traj_length_all
            self.df['real_min_length'] = real_min_all
        else:  # if data is not ok, fill all columns with nan
            self.df['flips'] = (np.full([self.df.shape[0]],np.nan))
            self.df['max_deviation'] = (np.full([self.df.shape[0]],np.nan))
            self.df['RPB'] = (np.full([self.df.shape[0]],np.nan))
            self.df['AUC'] = (np.full([self.df.shape[0]],np.nan))
            self.df['initiation_angle'] = (np.full([self.df.shape[0]],np.nan))
            self.df['initiation_correspondence'] = (np.full([self.df.shape[0]],np.nan))
            self.df['trajectory_length'] = (np.full([self.df.shape[0]],np.nan))
            self.df['real_min_length'] = (np.full([self.df.shape[0]],np.nan))

# exmp = Preprocessing(r'C:\Users\mhavi\shalevproject\mouse-tracking-tools-master\data\5a0c4184fe645f0001e9f5dd.csv',3,120,"x_cord","y_cord")
# exmp.normalize_time_points()
# exmp.rescale()
# exmp.remap_trajectories()
# exmp.plot_by_condition()
