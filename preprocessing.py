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
        self.NUM_TIMEPOINTS = 101
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
        self.continue_x = np.mean(self.x[0,:])#calculating the x cordinates for the continue button
        left_subset = self.x[:,self.x[100,:]<self.continue_x] #subsetting all trials where the left option is chosen
        right_subset = self.x[:,self.x[100,:]>self.continue_x]
        self.right_x, self.left_x = np.mean(right_subset[-1,:]),np.mean(left_subset[-1,:])#calculating the x cordinates for the choices
        self.x -= self.continue_x #center x coordinates
        self.x  = self.x / ((self.right_x-self.left_x)/2) #rescale x coordinates
        self.continue_y =  np.mean(self.y[0,:])
        self.targets_y = np.mean(self.y[100,:])
        self.y -=self.continue_y
        self.y = -self.y / ((self.continue_y-self.targets_y))

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

    def agg_by_conflict(self):
        self.app_ind = self.df.index[self.df['Conflict']=='Approach']
        self.avo_ind = self.df.index[self.df['Conflict']=='Avoidance']
        self.x_app = self.x[:,self.app_ind]
        self.x_avo = self.x[:,self.avo_ind]
        self.y_app = self.y[:,self.app_ind]
        self.y_avo = self.y[:,self.avo_ind]
    

    def get_x_flips(self):
        """
        This function calculates number of x flips trial by trial and save it as a variable 'flips' of the class
        """
        self.flips = []
        for trial in  range (self.NUM_TRIALS):
            bigger, smaller = False, False
            x_count, y_count = 0, 0
            last_i = 0
            for i in range(1,self.NUM_TIMEPOINTS):
                if self.x[last_i,trial] > self.x[i,trial]:
                    last_i += 1
                    if not bigger:
                        bigger = True
                        smaller = False
                        if i != 1:
                            x_count += 1
                    else:
                        continue
                if self.x[last_i,trial] < self.x[i,trial]:
                    last_i += 1
                    if not smaller:
                        bigger = False
                        smaller = True
                        if i != 1:
                            x_count += 1
                    else:
                        continue
            self.flips.append(x_count)
    
    def get_middle_cross(self):
        """
        This funcction calculates the number of times the mouse cursor cross the middle of the X-axis
        """
        self.crosses_y_ap= []
        self.crosses_y_av = []
        self.middle_crosses = []
        for trial  in range (self.NUM_TRIALS):
            crosses = 0
            last_i = 0
            for i in range(1,self.NUM_TIMEPOINTS):
                if (self.x[last_i,trial] > 0 and self.x[i,trial] < 0) or (self.x[last_i,trial] < 0 and self.x[i,trial] > 0):
                    crosses += 1
                    if (self.df['Conflict'][trial] == 'Approach'):
                        self.crosses_y_ap.append(self.y[i,trial])#append the y position of the cross for later visualization
                    elif (self.df['Conflict'][trial] == 'Avoidance'):
                        self.crosses_y_av.append(self.y[i,trial])
                last_i += 1
            self.middle_crosses.append(crosses)

    # def create_means (self):
    #     self.mean_app_x =  se

    def get_AUC (self):
        """
        This function calculates all area under the curve for the trajectories
        """
        self.AUC =[]
        #line_x, line_y = np.linspace(0,1,101),np.linspace(0,1,101)
        #self.line = np.column_stack((line_x, line_y))
        for i in range(self.NUM_TRIALS):
            cur_x = self.x[:,i]
            cur_y = self.y[:,i]
            line_x, line_y = cur_x,cur_x # create a straight line from (0,0) to (1,1). specifically, using the trajectory x cordinates to enable integration
            ##possibility - visualize the integrated part
            # plt.plot(cur_x,cur_y,color = 'r')
            # plt.plot(line_x,line_y)
            # plt.fill_between(cur_x,cur_y,line_y,alpha = 0.4)
            # plt.ylim(0,1.3)
            # plt.show()
            cur_integral = np.trapz(cur_y-line_y)
            print(cur_integral)



    def get_max_deviation(self):
        """
        This function calculates the maximal deviation from the actual trajectory to a 
        straight line connecting the starting position and the target.
        IMPORTANT: this function will only work if you apply the rescale and remap functions first.
        """
        self.max_deviations = []
        line_x, line_y = np.linspace(0,1,101),np.linspace(0,1,101)
        self.line = np.column_stack((line_x, line_y))
        # plt.plot (line[:,0],line[:,1])
        # plt.show()
        #points = np.empty([2,self.NUM_TRIALS])
        for i in range (self.NUM_TRIALS):
            distances =[]
            for j in range (self.NUM_TIMEPOINTS):
                cur_point = np.array([self.x[j,i],self.y[j,i]])
                norm = np.linalg.norm(self.line-cur_point,axis = 1)
                cur_distance = np.min(norm)
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
        self.get_middle_cross()
        self.df['middle_crosses'] = self.middle_crosses
        self.get_AUC()
        ##TO DO: add additional measures after writing the code for them
        



    
def process_across_subjects(directory):
    """
    This function gets a directory and apply the functions in the above class on all of
    the subjects files in the directory.
    It also creates a unified CSV file of all subjects and saves it in the directory
    """
    df_list = []
    #innitialuze matrixes of all trajectorues
    all_x_app = np.empty([101,21,56])
    all_y_app = np.empty([101,21,56])
    all_x_avo = np.empty([101,21,56])
    all_y_avo = np.empty([101,21,56])
    crosses_y_av = []
    crosses_y_ap = []
    files = os.listdir(directory)
    counter = 0
    for sub in range(len(files)):
        if files[sub] != 'all_subjects.csv' and files[sub][0] != '$':
            cur_class = TrajectoryProcessing(directory + "\\" + files[sub])
            ###preprocess
            cur_class.normalize_time_points()
            cur_class.rescale()
            cur_class.remap_trajectories()
            cur_class.agg_by_conflict()
            #cur_class.plot_by_conflict()
            ###add cur subject trajecories to the big matrices
            all_x_avo[:,:,counter] =  cur_class.x_avo
            all_y_avo[:,:,counter] = cur_class.y_avo
            all_x_app[:,:,counter] = cur_class.x_app
            all_y_app[:,:,counter] = cur_class.y_app
            counter += 1

            cur_class.calculate_all_measures()
            cur_class.df['subject_id'] = counter
            df_list.append(cur_class.df)

            ### visualization of middle crosses
            # plt.subplot(1,2,1)
            # plt.title('AV-AV')
            # plt.scatter(np.zeros(len(cur_class.crosses_y_av)),cur_class.crosses_y_av,color = 'r')
            # plt.subplot(1,2,2)
            # plt.title('AP-AP')
            # plt.scatter(np.zeros(len(cur_class.crosses_y_ap)),cur_class.crosses_y_ap, color = 'g')
            # plt.show()

            crosses_y_av = crosses_y_av + cur_class.crosses_y_av #concat lists for overall y values of middle crosses.
            crosses_y_ap = crosses_y_ap + cur_class.crosses_y_ap
    big_df = pd.concat(df_list)
    ###create mean trajectories
    mean_x_app = np.mean(all_x_app,axis=(1,2))
    mean_y_app = np.mean (all_y_app,axis =(1,2))
    mean_x_avo = np.mean(all_x_avo,axis=(1,2))
    mean_y_avo = np.mean (all_y_avo,axis =(1,2))
    
    ### visualization of middle crosses
    plt.subplot(1,2,1)
    plt.title('AV-AV')
    plt.scatter(np.zeros(len(crosses_y_av)),crosses_y_av,color = 'r',s =0.5)
    plt.subplot(1,2,2)
    plt.title('AP-AP')
    plt.scatter(np.zeros(len(crosses_y_ap)),crosses_y_ap, color = 'g', s = 0.5)
    plt.show()

    ### visualization of mean trajectories
    # plt.plot(mean_x_app,mean_y_app,'--go',label = 'AP-AP')
    # plt.plot(mean_x_avo,mean_y_avo,'--ro',label = 'AV-AV')
    # plt.legend(fontsize="x-large")
    # plt.xlim(-1,1.1)
    # plt.show()

    big_df.to_csv(directory+'\\all_subjects.csv')


        


#path = r"C:\Users\ariel\Desktop\data\$5d593dbaa0c0940001ּa471be.csv"
path = r"C:\Users\ariel\Desktop\ariel_check.csv"
directory = r"C:\Users\ariel\Dropbox\Experiments\Motivational_conflicts_mouse\data"
process_across_subjects(directory)

# check = TrajectoryProcessing(path)
# check.normalize_time_points()
# check.rescale()
# check.remap_trajectories()
# #print(check.y[100,:])ּ
# check.get_x_flips()
# # print (check.flips)
# check.plot_by_conflict()
# check.get_max_deviation()
# check.get_middle_cross()
# # print(check.max_deviations)
# # # check.calculate_all_measures()
# for sub in range (check.NUM_TRIALS):
#     plt.plot(check.x[:,sub],check.y[:,sub],'--ob')
#     #plt.plot (check.line[:,0],check.line[:,1])
#     plt.xlim(-1.2,1.2)
#     #print(check.x[:,sub])
#     print(check.flips[sub])
#     print(check.max_deviations[sub])
#     print (check.middle_crosses[sub])
#     plt.show()

# plt.plot(check.x[:,0:42],check.y[:,0:42],'--o')
# plt.xlabel('X cordinate')
# plt.ylabel('Y cordinate')
# plt.show()
