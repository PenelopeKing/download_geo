from geofetch import Geofetcher
import pysradb.sraweb
import pandas as pd
import os
import urllib.request
import sys
from IPython.display import display
from ipywidgets import interact, Dropdown, Button, Text
import traitlets
from traitlets import dlink

from geo_downloader.downloader import *

def set_up():
    pd.set_option('display.max_rows', None)
    
def print_pretty_table(csv_path):
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_path)
    # Display the DataFrame using IPython display
    display(df)

def get_maximum_k(directory):
    # Get all files in the directory
    files = os.listdir(directory)
    
    # Filter for files starting with Partial_
    partial_files = [f for f in files if f.startswith("Partial_")]
    if len(partial_files) == 0:
        return 0
   
    # Extract the k values from each filename
    k_values = [int(f.split("_")[1]) for f in partial_files]
   
    # Return the maximum k value
    return max(k_values)

def browse_and_select_rows(csv_path, column_name):
    """
    modified original method for binder use
    """
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_path)
    df = df.rename(columns={'Unnamed: 0':'index'})

    # Create a dropdown widget to select items from the column
    options_list = [''] +df[column_name].unique().tolist()
    dropdown = Dropdown(options= options_list)
    
    save_path_input = os.path.join(os.getcwd(), 'downloaded_files')
    
    # Create a button widget for saving and downloading
    button = Button(description='Save and Download')
    
    # Create an empty DataFrame to store selected rows
    selected_rows_df = pd.DataFrame()
    
    # Function to display filtered rows based on the selected item
    def display_filtered_rows(selected_item):
        nonlocal selected_rows_df
        
        # Filter the DataFrame based on the selected item
        filtered_df = df[df[column_name] == selected_item]
        
        # Append the filtered rows to the selected rows DataFrame
        selected_rows_df = pd.concat([selected_rows_df, filtered_df], ignore_index=True)
        
        # Display the selected rows
        display(filtered_df)
        
        # Print the growing list of selected rows
        print("Selected Rows:")
        for i in range(len(selected_rows_df)):
            row_entry = str(selected_rows_df.loc[i, column_name])[:60] + '...' if len(str(selected_rows_df.loc[i, column_name])) else str(selected_rows_df.loc[i, column_name])
            print(f"Row {i+1}: {row_entry}")
        print()  # Print an empty line for separation
        
    # Function to handle the save and download button click event
    def save_and_download(_):
        nonlocal selected_rows_df
        
        # Check if any rows are selected
        if selected_rows_df.empty:
            print("No rows are selected.")
            return
        
        # Get the save path directory from the input text widget
        save_directory = save_path_input
        
        # Get the directory and file part of the original CSV file path
        directory = os.path.dirname(csv_path)
        file_name = os.path.basename(csv_path)
        file_part = os.path.splitext(file_name)[0]
        file_extension = os.path.splitext(file_name)[1]
        
        # Find the next available k for the Partial_k file name in the directory
        k = get_maximum_k(save_directory)
        
        # Create the Partial_k file name
        partial_k_filename = f"Partial_{k+1}_{file_part}.csv"
        
        # Combine the save directory, partial_k file name, and save path to form the final save path
        save_path = os.path.join(save_directory, partial_k_filename)
        
        # Write the selected rows to a new CSV file
        selected_rows_df.to_csv(save_path, index=False)
        
        # Print the save path and exit the program
        print(f"Saved CSV file: {save_path}")
        
        # download the files in partial csv
        download_files(save_path, save_directory)
        
        # Clear the selected rows DataFrame for the next iteration
        selected_rows_df = pd.DataFrame()
    
    # Connect the dropdown widget to the display function
    interact(display_filtered_rows, selected_item=dropdown)
    
    # Connect the button widget to the save and download function
    button.on_click(save_and_download)
    
    # Display the input text widget and button widget
    display(button) 
    
# makes selection easier for user end on binder
def preview_data_visual(gse):
    '''
    input: gse (str) - GSE accession number
    '''
    
    import downloader
    
    
    download_path = os.path.join(os.getcwd(), 'downloaded_files')
    try: 
        os.mkdir(download_path)
    except:
        pass

    get_descriptions(gse, download_path)
    
def display_csv(csv_path):
    """
    displays csv for binder
    input: csv_path (str) - path of csv to turn into a dataframe
    """
    return pd.read_csv(csv_path, index_col=0)