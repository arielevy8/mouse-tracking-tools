# Preserve Non-Trajectory Rows - Implementation Guide

## Overview
The mouse tracking preprocessing pipeline has been updated to preserve valuable non-trajectory rows (like questionnaires, attention checks, slider responses) that don't have mouse tracking data but contain important experimental information.

## Changes Made

### 1. Configuration (main.py)
Added a new configurable parameter:

```python
COLUMNS_TO_PRESERVE = []  # e.g., ['trial_type', 'response', 'rt', 'attention_check']
```

**Usage:** List the column names that should be checked to preserve rows. If a row has data in ANY of these columns, it will be kept even if it doesn't have trajectory data.

### 2. Core Processing (Preprocessing.py)
- Added `columns_to_preserve` parameter to `__init__` method
- Implements smart row filtering:
  - Keeps rows WITH trajectory data (has x_cord and y_cord)
  - Keeps rows WITHOUT trajectory data BUT with data in any `columns_to_preserve` columns
  - Only drops rows that have neither
- Tracks which rows are trajectory vs non-trajectory
- Processes only trajectory rows for coordinate normalization and measure calculation
- Non-trajectory rows receive NaN values for all trajectory measures (flips, AUC, RPB, etc.)

### 3. Batch Processing (process_across_subjects.py)
- Added `columns_to_preserve` parameter to function signature
- Passes parameter through to `Preprocessing` class

## How It Works

### Before (old behavior)
```python
# Line 28 in Preprocessing.py (old)
self.df = csv.dropna(subset = [x_cord_column])  # Drops ALL rows without trajectory data
```
**Result:** Lost questionnaires, attention checks, and other valuable data

### After (new behavior)
```python
# Smart filtering
if columns_to_preserve:
    has_trajectory = csv[x_cord_column].notna()
    has_preserve_data = csv[columns_to_preserve].notna().any(axis=1)
    rows_to_keep = has_trajectory | has_preserve_data
    self.df = csv[rows_to_keep].copy()
```
**Result:** Preserves both trajectory data AND valuable non-trajectory rows

## Usage Examples

### Example 1: Basic Usage
```python
# In main.py
COLUMNS_TO_PRESERVE = ['trial_type', 'response']

# This will preserve:
# - All rows with x_cord and y_cord data (trajectory trials)
# - All rows with data in 'trial_type' OR 'response' columns (questionnaires, etc.)
```

### Example 2: Attention Checks
```python
# In main.py
COLUMNS_TO_PRESERVE = ['attention_check', 'attention_response']

# Preserves attention check trials that don't have mouse tracking
```

### Example 3: Multiple Column Types
```python
# In main.py
COLUMNS_TO_PRESERVE = ['trial_type', 'response', 'rt', 'slider_value', 'attention_check']

# Preserves any row that has data in ANY of these columns
```

### Example 4: Backward Compatibility (default)
```python
# In main.py
COLUMNS_TO_PRESERVE = []  # Empty list

# Behaves exactly like before - only keeps rows with trajectory data
```

## Output Format

### Trajectory Rows
- All original data columns preserved
- x_0, x_1, ..., x_99, y_0, y_1, ..., y_99 columns added
- All measures calculated: flips, max_deviation, RPB, AUC, initiation_angle, etc.

### Non-Trajectory Rows
- All original data columns preserved
- x_0 through x_99 and y_0 through y_99 are NaN
- All trajectory measures are NaN: flips, max_deviation, RPB, AUC, etc.
- Can be easily filtered out or analyzed separately

## Benefits

1. **No Data Loss:** Important experimental data is preserved
2. **Complete Dataset:** All trials from each participant in one file
3. **Easy Filtering:** Non-trajectory rows have NaN for trajectory measures
4. **Backward Compatible:** Setting `COLUMNS_TO_PRESERVE = []` maintains old behavior
5. **Flexible:** Configure which columns to check per study

## Filtering in Analysis

After processing, you can filter the output:

```python
# Load processed data
df = pd.read_csv('all_subjects_processed_2025-10-21.csv')

# Get only trajectory data
trajectory_only = df[df['flips'].notna()]

# Get only non-trajectory data (questionnaires, etc.)
non_trajectory = df[df['flips'].isna()]

# Get specific trial types
if 'trial_type' in df.columns:
    mouse_tracking = df[df['trial_type'] == 'mouse_tracking']
    questionnaires = df[df['trial_type'] == 'questionnaire']
```

## Technical Details

### Key Variables Added
- `self.trajectory_rows`: Boolean array indicating which rows have trajectory data
- `self.num_trajectory_rows`: Count of trajectory rows (used for validation and iteration)
- `self.x_cord_column`, `self.y_cord_column`: Stored for later reference

### Validation Changes
- Subject validation (`isOK` flag) now checks only trajectory rows
- Non-trajectory rows don't affect subject validity
- Practice trial removal works on combined dataset

### Memory Considerations
- Coordinate arrays (self.x, self.y) only contain trajectory rows
- Full dataframe (self.df) contains all rows
- Slightly increased memory usage for tracking arrays

## Testing Recommendations

1. **Test with mixed data:** CSV with both trajectory and non-trajectory rows
2. **Verify preservation:** Check that non-trajectory rows appear in output
3. **Verify measures:** Confirm trajectory rows have calculated measures
4. **Check NaN handling:** Ensure non-trajectory rows have NaN for measures
5. **Test backward compatibility:** Run with empty `COLUMNS_TO_PRESERVE`

## Notes

- Practice trials are removed from BOTH trajectory and non-trajectory rows
- Non-trajectory rows count toward total rows but not toward NUM_TRIALS validation
- The `subject_id` counter continues across all subjects regardless of row types
- Visualization functions filter on `is_OK == True` so invalid subjects are excluded

