# -*- coding: utf-8 -*-
'''Get Run Data'''
__title__ = "Get Run Data"
__author__ = "romaramnani"

import csv
import time
from datetime import datetime
from Autodesk.Revit.DB import *
from pyrevit import revit, script
import time
from pyrevit.coreutils.logger import get_logger

mlogger = get_logger(__name__)

app = __revit__.Application
ui_doc = revit.uidoc
doc = revit.doc 
    
def get_run_data( __title__, runtime_seconds, element_count, est_manual_time_for_10_elements, run_result, error_occured):
       
    def get_before_last_underscore(text):
        # Find the position of the first underscore
        underscore_pos = text.find('_')
        
        # If an underscore is found, return the substring up to the underscore
        if underscore_pos != -1:
            return text[:underscore_pos]
        else:
            # If no underscore is found, return the original text
            return text

    '''
    def get_before_first_dash(text):
        # Find the position of the first underscore
        underscore_pos = text.find('-')
        
        # If an underscore is found, return the substring up to the underscore
        if underscore_pos != 0:
            return text[:underscore_pos]
        else:
            # If no underscore is found, return the original text
            return text
            '''

    def extract_data():
    
        if run_result == "Tool ran successfully":
            status = "Success"
        else: 
            status = "Fail"

        user_name = app.Username
        #print(user_name)

        rvt_year = app.SubVersionNumber
        #print(rvt_year)

        #project_code = get_before_first_dash(doc.Title)
        
        model_name = get_before_last_underscore(doc.Title)
        #print(model_name)
        #print(project_code)

        tool_name = __title__ 
        #tool_name = self.remove_after_period(script.get_bundle_name()) - '.'
        #print(tool_name)
        #time_saved = ((runtime_seconds/element_count)*1000)/est_manual_time_for_10_elements
        # Prepare the data to append (Timestamp, Runtime, and Elements Processed)
        new_data = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), rvt_year, tool_name, runtime_seconds, element_count, model_name, user_name, status, est_manual_time_for_10_elements, error_occured]

        # Path to the CSV file (use .csv extension)
        csv_file_path = "\\\darpune.com\\Projects\\_short-term-01\\DAR20093-0115D\\02_Logs\\Data.csv"

        try:
            # Append data to the CSV file
            with open(csv_file_path, mode='ab') as file:  # 'ab' for append and binary mode in Python 2.7
                writer = csv.writer(file)

                # If the file is new and empty, add the header row
                if file.tell() == 0:  # Checks if the file is empty
                    writer.writerow(["Timestamp", "Revit Version", "Tool Name", "Runtime (seconds)", "Elements Processed", "Model Name", "User Name", "Status", "Est. Manual time(for 10 elements)", "Error"])

                # Write the new data row
                writer.writerow(new_data)

            #print("Data successfully appended to CSV.")
        except:
            pass
    
    extract_data()
