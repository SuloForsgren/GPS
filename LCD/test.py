import pandas as pd

# Load the CSV data
df = pd.read_csv('road_segments.csv')

# Function to print the speed limits for all segments
def print_speed_limits(dataframe):
    for index, row in dataframe.iterrows():
        segment_id = row['SEGM_ID']
        speed_limit = row['ARVO']
        start_m = row['ALKU_M']
        end_m = row['LOPPU_M']
        print(f"Segment ID: {segment_id}, Speed Limit: {speed_limit} km/h, Start: {start_m} m, End: {end_m} m")

# Display the speed limits
print_speed_limits(df)

# Function to get the speed limit of a specific segment by its ID
def get_speed_limit_by_segment_id(dataframe, segment_id):
    segment = dataframe[dataframe['SEGM_ID'] == segment_id]
    if not segment.empty:
        for index, row in segment.iterrows():
            speed_limit = row['ARVO']
            start_m = row['ALKU_M']
            end_m = row['LOPPU_M']
            print(f"Segment ID: {segment_id}, Speed Limit: {speed_limit} km/h, Start: {start_m} m, End: {end_m} m")
    else:
        print(f"No segment found with ID: {segment_id}")

# Example: Get the speed limit for a specific segment
segment_id = '927_99969'
get_speed_limit_by_segment_id(df, segment_id)
