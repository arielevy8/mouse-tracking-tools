import sys
sys.path.append('code')
from Visualization import Visualization
import pandas as pd

# Load the processed data
df_path = r'C:\Users\shale\Downloads\sntr_conflict\sntr_conflict\all_subjects_processed2025-10-21.csv'

# Create visualization object with the same parameters as main.py
viz = Visualization(df_path,
                   r'C:\Users\shale\Downloads\sntr_conflict\sntr_conflict',  # output dir
                   '',  # study_title
                   'trajectory',  # first_condition_column
                   [],  # first_condition_order
                   '',  # second_condition_column
                   [],  # second_condition_order
                   16, 12, 10, 12, 4,  # sizes
                   [(205, 92, 92), (0, 206, 209)],  # colormap
                   1,  # subject_to_inspect
                   [],  # subjects_to_remove
                   {})  # condition_labels

print('Testing plot_means()...')
try:
    viz.plot_means()
    print('SUCCESS: plot_means() completed without errors!')
except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()

print('Testing plot_subject()...')
try:
    viz.plot_subject()
    print('SUCCESS: plot_subject() completed without errors!')
except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()
