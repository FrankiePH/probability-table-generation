import os
import logging
from rsLogger.logger import Logger
import functions as fn
import pandas as pd
import json


# Starts logger for file
current_path = os.getcwd()
folder_name = os.path.basename(current_path)
my_log = Logger().get_logger(__name__)
my_file_logger = Logger()
if os.environ.get('DEBUG') == 'True':
    logging.root.setLevel(logging.DEBUG)
else:
    logging.root.setLevel(logging.INFO)

def to_snake_case(name):
    return name.lower().replace(' ', '_').replace('-', '_')

def get_probabilities(next_paths):
    probabilities = {}
    for arr in next_paths:
        path = arr[0]
        
        #if '.' not in path:
        #    if 'None' in probabilities:
        #        probabilities['None'] += 1
        #    else:
        #        probabilities['None'] = 1
        #else:
        start = path.split('.')[0]
        if start in probabilities:
            probabilities[start] += 1
        else:
            probabilities[start] = 1
                
    # convert probability numbers too percentages
    total = sum(probabilities.values())
    for key in probabilities:
        probabilities[key] = (probabilities[key]/total) * 100
    
    return probabilities
        
        


def make_decision_tree(prior_path, sorted_caseloads_paths, ret={}):
    '''
    A recursive function to get the probabilities of the next path from the prior path.
    :param prior_path: str: The prior path
    :param sorted_caseloads_paths: pd.DataFrame: The sorted caseloads paths
    :param ret: dict: The dictionary to store the probabilities
    '''
    # get all the paths that begin with the prior path
    if prior_path == '':
        next_paths = sorted_caseloads_paths.copy()  # Work on a copy when prior_path is empty
    else:
        next_paths = sorted_caseloads_paths[sorted_caseloads_paths['path'].str.startswith(prior_path)].copy()

    # Exit condition: If no next paths are found, stop recursion
    if next_paths.empty:
        print(f"No more paths for {prior_path}, stopping recursion.")
        return ret

    # Remove the prior path from the beginning of the 'path' string
    next_paths['path'] = next_paths['path'].apply(lambda x: x.replace(prior_path + '.', '', 1) if prior_path else x)

    # If all paths are already identical to `prior_path`, avoid recursion
    if all(next_paths['path'] == ''):
        print(f"All paths match the prior path {prior_path}, stopping recursion.")
        return ret

    # Count occurrences of each next step in the path
    next_paths = next_paths.groupby('path').count().reset_index()

    # Sort paths and calculate probabilities
    next_paths_as_list = next_paths[['path', 'IDReferralin']].values.tolist()  # Ensure to reference correct columns
    probabilities = get_probabilities(next_paths_as_list)  # Assuming get_probabilities exists

    # Add probabilities to the return dictionary
    ret[prior_path] = probabilities

    # Recurse into each path
    for path in next_paths['path'].values:
        if path.strip():  # Avoid empty string paths
            new_prior_path = prior_path + '.' + path if prior_path else path
            print(f"Recursing into {new_prior_path}")
            make_decision_tree(new_prior_path, sorted_caseloads_paths, ret)

    return ret


def main(): 
    pd.set_option('display.max_colwidth', None)  # Show full width of the columns
    pd.set_option('display.max_rows', None)     # Show all rows (if needed)

    # Load csv to pandas dataframe
    df = pd.read_csv('caseload_analysis.csv')
    
    # Sort data by id and time and convert dates too YYYYMMDD
    df = df.sort_values(by=['IDReferralin', 'date_from'])
    df['CaseloadName'] = df['CaseloadName'].apply(to_snake_case)
    
    # sort id and get the path they took
    df_paths = df.groupby('IDReferralin')['CaseloadName'].apply(lambda x: '.'.join(x)).reset_index()
    df_paths.columns = ['IDReferralin', 'path']
    
    # Convert the date columns to the desired format YYYYMMDD
    df['date_from'] = pd.to_datetime(df['date_from']).dt.strftime('%Y%m%d')
    df['date_to'] = pd.to_datetime(df['date_to']).dt.strftime('%Y%m%d')
    
    # save the data
    df.to_csv('sorted_caseload_analysis.csv', index=False)
    df_paths.to_csv('sorted_caseload_paths.csv', index=False)
    
    ret = make_decision_tree('',df_paths)
    
    # save the data to json
    with open('probabilities_tree.json', 'w') as f:
        json.dump(ret, f, indent=4)
        
    
    # convert the 
    


if __name__ == '__main__':
    main()