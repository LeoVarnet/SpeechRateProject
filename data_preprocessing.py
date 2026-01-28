## Code for preprocessing of raw .txt files from MindProbe to get .csv per participants
## 2026
#%% import libraries
import os
import csv
import json
import pandas as pd
import re

#%% functions

## each raw .txt file is an array of JSON per participant, one JSON per line. This function is to get multiples .txt files, one per participant.
def split_lines_to_files(input_file, output_folder):

    # Open the input file
    with open(input_file, 'r') as f:

        # Read lines from the input file
        lines = f.readlines()

        # Iterate over each line
        for i, line in enumerate(lines):
            # Generate output file name based on input file name and line number
            input_filename = os.path.basename(input_file)
            output_file = os.path.join(output_folder, f'{input_filename}_line_{i+1}.txt')
            
            # Write line to the output file
            with open(output_file, 'w') as out_f:
                out_f.write(line)
            
            print(f"Line {i+1} from {input_filename} exported to {output_file}")

# usage:
input_folder = 'data_raw'
output_folder = 'data_raw_individuals'

for filename in os.listdir(input_folder):
    if filename.endswith('.txt'):
        input_file = os.path.join(input_folder, filename)
        split_lines_to_files(input_file, output_folder)

# %% check txt file issues, if some JSON have a different form than others.

def check_json_files(folder_path):
    bad_files = []
    good_files = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = file.read()
                    json.loads(data)  # attempt to parse
                good_files.append(filename)
            except json.JSONDecodeError as e:
                bad_files.append((filename, str(e)))
    return good_files, bad_files

good, bad = check_json_files(folder_path)

print("✅ Good files:", len(good))
print("❌ Bad files:", len(bad))
print("\nList of bad files with errors:")
for f, err in bad:
    print(f" - {f} -> {err}")

# %% from .txt to raw .csv per individual
def convert_folder_to_csv(folder_path):
    # Ensure output folder exists
    os.makedirs(folder_path2, exist_ok=True)

    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(folder_path, filename)
            file_path2 = os.path.join(folder_path2, filename)

            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                data = f.read().strip()

            idx = 0
            pos = 0
            decoder = json.JSONDecoder()
            while pos < len(data):
                try:
                    json_data, end = decoder.raw_decode(data, pos)
                except json.JSONDecodeError as e:
                    print(f"Skipping invalid JSON in {filename} at position {pos}: {e}")
                    break

                # Extract trials
                trials = json_data['trials']

                # Collect fieldnames
                fieldnames = set()
                for trial in trials:
                    fieldnames.update(trial.keys())

                # CSV file name
                base_name = os.path.splitext(file_path2)[0]
                if idx == 0:
                    csv_file = base_name + '.csv'
                else:
                    csv_file = f"{base_name}_bis{idx}.csv"

                # Write CSV
                with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(trials)

                print(f"CSV file generated successfully for {filename}, block {idx}")

                idx += 1
                pos = end  # move position to the end of the last JSON parsed
                while pos < len(data) and data[pos].isspace():  # skip whitespace
                    pos += 1

folder_path = 'data_raw_individuals'
folder_path2 = 'data_raw_individuals_csv'

convert_folder_to_csv(folder_path)

# %% To get one CSV per participant, with usefull columns and rosw

def process_csv_files(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            df = pd.read_csv(os.path.join(folder_path, filename))

            # Columns we want to keep
            columns = [
                'ID', 
                'date', 
                'condition', 
                'age', 
                'sex', 
                'prolific',
                'stim', 
                'participant_answer'
            ]

            # Keep only rows where ID is not NaN (only keep data rows)
            selected_data = df.loc[df['ID'].notna(), columns]

            if selected_data.empty:
                print(f"No valid ID rows in {filename}")
                continue

            # Assuming one participant per file → take the first ID
            name = selected_data['ID'].iloc[0]

            selected_data.to_csv(
                os.path.join(folder_path2, f'{name}_data.csv'),
                index=False
            )

            print(f"Selected data exported to {folder_path2}/{name}_data.csv")


folder_path = 'data_raw_individuals_csv'
folder_path2 = 'data_csv'

process_csv_files(folder_path)


# %% get all individual CSV to one CSV with all participants in each rows. 

def concatenate_csv_files(folder_path, output_file):
    # Initialize an empty DataFrame to store concatenated data
    concatenated_df = pd.DataFrame()

    # Iterate over each file in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            # Load CSV into a DataFrame
            df = pd.read_csv(os.path.join(folder_path, filename))

            # Concatenate the DataFrame to the main DataFrame
            concatenated_df = pd.concat([concatenated_df, df], ignore_index=True)

    # Write concatenated DataFrame to a single CSV file
    concatenated_df.to_csv(output_file, index=False)

    print(f"All CSV files concatenated and exported to {output_file}")

# Example usage:
folder_path = 'modified_data_csv'  # Replace with your folder path containing CSV files
output_file = '2IAFC_150m_zalana_summer_2023_data.csv'

concatenate_csv_files(folder_path, output_file)
