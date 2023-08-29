import csv
import numpy as np

def run():

    input_file = 'csv/data_AGMP_19July2022_v2.csv'
    output_file = 'csv/output.csv'

    with open(input_file, 'r') as file:
        csv_reader = csv.reader(file)
    
        # Skip the header if present
        header = next(csv_reader)
    
        # Process the rows
        for row in csv_reader:
            # Assuming the column you want to split is the second column (index 1)
            column_to_split = row[1]
        
            # Split the string using a delimiter (e.g., comma)
            split_values = column_to_split.split(',')
        
            # Process the split values as needed
            # ..
            with open(output_file, 'w', newline='') as file:
                csv_writer = csv.writer(file)
    
                # Write the header
                csv_writer.writerow(header)

                for row, split_vals in zip(csv_reader, split_values):
                        # Assuming you want to replace the second column with the split values
                    row[1] = split_vals
        
                        # Write the modified row
                    csv_writer.writerow(row)









  