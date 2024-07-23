#!/usr/bin/env python3

"""
Description: Download stats for mini crossword and wordle from nyt website
"""

# Imports
import json
import requests
import pandas as pd
import numpy as np

# Constants
TESTING = True

# Functions
def get_mini_ids(date_start, date_end):
    """Return a list of mini ids for the dates between the specifed ranges"""
    response = requests.get(f'https://www.nytimes.com/svc/crosswords/v3/36569100/puzzles.json?publish_type=mini&date_start={date_start}&date_end={date_end}')
    # Check message status code
    if response.status_code != 200:
        print('Error retrieving data: '+response.status_code)
        return
    # Check body status
    data = response.json()
    if data['status'] != 'OK':
        print('Response internal status not OK')
        print(data)
        return
    # Filter response
    return [{'print_date': item['print_date'], 'puzzle_id': item['puzzle_id']} for item in data['results']]
    
def get_mini_results(token, mini_id):
    """Get results for a spefic mini by id for a given player (percentFilled, secondsSpentSolving, solved)"""
    headers = {
        'Cookie': f'nyt-s={token};',
        'Accept': 'application/JSON',
    }
    response = requests.get(f'https://www.nytimes.com/svc/crosswords/v6/game/{mini_id}.json', headers=headers)
    # Check message status code
    if response.status_code != 200:
        print('Error retrieving data: '+str(response.status_code))
        return
    # Return calculated results
    return response.json()['calcs']

def player_stats(name, df): 
    solved_col = f'{name}_solved'
    time_col = f'{name}_time'
    wins_col = f'{name}_win'

    return pd.DataFrame({
        'Player': name,
        'Total Wins': df[wins_col].sum(),
        'Total Time': df[df[solved_col]][time_col].sum(),
        'Total Solved': df[solved_col].sum(),
        'Total Unsolved': (~df[solved_col]).sum(),
        'Average Time': df[df[solved_col]][time_col].mean(),
        'Fastest Solve': df[df[solved_col]][time_col].min(),
        'Slowest Solve': df[df[solved_col]][time_col].max()
    }, index=[0])

# Classes
class Calculator:
    """A simple calculator class."""

    def __init__(self):
        pass

    def multiply(self, a, b):
        """Return the product of a and b."""
        return a * b

    def divide(self, a, b):
        """Return the division of a by b."""
        if b == 0:
            raise ValueError("Cannot divide by zero.")
        return a / b

# Main program execution
if __name__ == "__main__":
    # Read user id tokens from file
    with open('tokens.json', 'r') as file:
        tokens = json.load(file)

    if not TESTING:
        # Get ids of minis withing data range
        results_df = pd.DataFrame(get_mini_ids('2024-07-21', '2024-07-22'))
        print(results_df)

        for token in tokens:
            performance_data = [get_mini_results(token['token'], puzzle_id) for puzzle_id in results_df['puzzle_id']]
            # print(performance_data)
            performance_df = pd.DataFrame(performance_data).rename(columns={'secondsSpentSolving': 'time'}).add_prefix(token['name']+'_')
            print(performance_df)
            results_df = pd.concat([results_df, performance_df], axis=1)
    else:
        data = {
            'print_date': ['2024-07-22', '2024-07-21', '2024-07-20', '2024-07-19', '2024-07-18'],
            'Ben_solved': [True, True, True, False, True],
            'Ella_solved': [True, True, False, False, True],
            'Ben_time': [42, 160, 294, 123, 60],
            'Ella_time': [60, 85, 337, 234, 60]
        }
        results_df = pd.DataFrame(data)

    # Manipulate using Pandas  
    results_df = results_df[['print_date', 'Ben_solved', 'Ella_solved', 'Ben_time', 'Ella_time']]
   
    results_df['Ben_win'] = np.where((results_df['Ben_solved'] & results_df['Ella_solved'] & (results_df['Ben_time'] < results_df['Ella_time'])) | (results_df['Ben_solved'] & ~results_df['Ella_solved']), True, False)

    results_df['Ella_win'] = np.where((results_df['Ben_solved'] & results_df['Ella_solved'] & (results_df['Ella_time'] < results_df['Ben_time'])) | (results_df['Ella_solved'] & ~results_df['Ben_solved']), True, False)

    results_df['Ben_cum_wins'] = results_df['Ben_win'].cumsum()
    results_df['Ella_cum_wins'] = results_df['Ella_win'].cumsum()

    # Calculate stats
    stats_df = pd.DataFrame()
    for token in tokens:
        stats_df = pd.concat([stats_df, player_stats(token["name"], results_df)])
    print(stats_df)




    print(results_df)




    # Output (save to csv or print to console?)




'''

Read tokens

using first token, get list of dates + ids

For each mini id, get specific data for each player (in 'calcs' -> percentFilled, secondsSpentSolving, solved)

Save info to data structure / dataframe

Output dataframe with calculations to a csv

'''