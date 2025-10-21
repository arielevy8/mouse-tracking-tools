"""
Example Configuration for Preserving Non-Trajectory Rows
========================================================

Copy the relevant sections to your main.py file and adjust as needed.
"""

# ============================================================================
# EXAMPLE 1: Experiment with questionnaires after each trial
# ============================================================================
"""
CSV Structure:
- Some rows: Mouse tracking trials (have x_cord, y_cord)
- Some rows: Questionnaire responses (have 'response', 'question_type' but no x_cord/y_cord)
"""

# In main.py, set:
COLUMNS_TO_PRESERVE = ['response', 'question_type']

# Result:
# - Mouse tracking rows → Full trajectory data + calculated measures
# - Questionnaire rows → Original data preserved, trajectory measures = NaN


# ============================================================================
# EXAMPLE 2: Experiment with attention checks
# ============================================================================
"""
CSV Structure:
- Most rows: Mouse tracking trials
- Some rows: Attention checks (have 'attention_check', 'attention_response')
"""

# In main.py, set:
COLUMNS_TO_PRESERVE = ['attention_check', 'attention_response']

# Result:
# - Attention check trials preserved with their response data
# - Can later filter: df[df['attention_check'].notna()]


# ============================================================================
# EXAMPLE 3: Mixed experiment with multiple trial types
# ============================================================================
"""
CSV Structure:
- Mouse tracking trials (x_cord, y_cord present)
- Rating trials (have 'slider_rating')
- RT trials (have 'reaction_time')
- Demographics (have 'demographic_question', 'demographic_answer')
"""

# In main.py, set:
COLUMNS_TO_PRESERVE = [
    'trial_type',           # Column indicating type of trial
    'slider_rating',        # Rating scale responses
    'reaction_time',        # Simple RT trials
    'demographic_question', # Demographics questions
    'demographic_answer'    # Demographics answers
]

# Result: ALL trial types preserved in one file


# ============================================================================
# EXAMPLE 4: Experiment with explicit trial type column
# ============================================================================
"""
CSV Structure:
- All rows have a 'trial_type' column
- Values: 'mouse_tracking', 'questionnaire', 'slider', 'attention_check'
- Only 'mouse_tracking' rows have x_cord/y_cord data
"""

# In main.py, set:
COLUMNS_TO_PRESERVE = ['trial_type']

# Result:
# - ALL rows preserved (because all have 'trial_type')
# - Later analysis can filter: df[df['trial_type'] == 'mouse_tracking']


# ============================================================================
# EXAMPLE 5: Backward compatible (default behavior)
# ============================================================================
"""
If you want the OLD behavior (drop all non-trajectory rows):
"""

# In main.py, set:
COLUMNS_TO_PRESERVE = []  # Empty list = old behavior

# Result: Only rows with x_cord/y_cord are kept (original behavior)


# ============================================================================
# Post-Processing: Filtering the output
# ============================================================================
"""
After processing, you can easily filter the unified CSV:
"""

import pandas as pd

# Load processed data
df = pd.read_csv('output/all_subjects_processed_2025-10-21.csv')

# Filter only trajectory data (has calculated measures)
trajectory_data = df[df['flips'].notna()]

# Filter only non-trajectory data
non_trajectory_data = df[df['flips'].isna()]

# Filter by specific trial type (if you have that column)
if 'trial_type' in df.columns:
    mouse_tracks = df[df['trial_type'] == 'mouse_tracking']
    questionnaires = df[df['trial_type'] == 'questionnaire']
    attention_checks = df[df['trial_type'] == 'attention_check']

# Get all valid subjects (regardless of row type)
valid_subjects = df[df['is_OK'] == True]['subject_id'].unique()

# Analyze only valid subjects
valid_data = df[df['subject_id'].isin(valid_subjects)]


# ============================================================================
# CSV Format Examples
# ============================================================================
"""
BEFORE (row would be LOST):
+-----------+-------+-------+----------+----------------+
| x_cord    | y_cord| choice| response | trial_type     |
+-----------+-------+-------+----------+----------------+
| "100,200" | "50"  | "left"| NaN      | mouse_tracking |
| NaN       | NaN   | NaN   | 7        | questionnaire  | ← LOST!
+-----------+-------+-------+----------+----------------+

AFTER (with COLUMNS_TO_PRESERVE = ['response', 'trial_type']):
+-----------+-------+-------+----------+----------------+-------+-----+
| x_cord    | y_cord| choice| response | trial_type     | flips | AUC |
+-----------+-------+-------+----------+----------------+-------+-----+
| "100,200" | "50"  | "left"| NaN      | mouse_tracking | 2     | 0.5 |
| NaN       | NaN   | NaN   | 7        | questionnaire  | NaN   | NaN | ← KEPT!
+-----------+-------+-------+----------+----------------+-------+-----+
"""

