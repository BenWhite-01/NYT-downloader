#!/usr/bin/env python3

"""
Description: Download stats for mini crossword and wordle from nyt website
"""

# Imports
import json
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Constants
TESTING = False

# Functions
def get_dates():
    last = datetime.today().replace(day=1) - timedelta(days=1)
    first = last.replace(day=1)
    return first.strftime("%Y-%m-%d"), last.strftime("%Y-%m-%d")

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

def player_mini_stats(name, df): 
    solved_col = f'{name}_solved'
    time_col = f'{name}_time'
    wins_col = f'{name}_win'

    return pd.DataFrame({
        'Player': name,
        'Total Wins': df[wins_col].sum(),
        'Total Time': df[df[solved_col]][time_col].sum(),
        'Total Solved': df[solved_col].sum(),
        'Total Unsolved': (~df[solved_col]).sum(),
        'Average Time': df[df[solved_col]][time_col].mean().round(),
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
    # Get dates from user
    start_date, end_date = get_dates()
    print(f'Dates currently set to {start_date} -> {end_date}')
    while input('Would you like to change the dates (y/n): ') == 'y':
        try:
            start_date = datetime.strptime(input('Start Date: '), "%Y-%m-%d").strftime("%Y-%m-%d")
            end_date = datetime.strptime(input('End Date: '), "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError as e:
            print("Error: Date needs to be in format YYYY-MM-DD")
        finally:
            print(f'\nDates currently set to {start_date} -> {end_date}')
    
    # Read user id tokens from file
    with open('tokens.json', 'r') as file:
        tokens = json.load(file)

    if not TESTING:
        # Get ids of minis withing data range
        print(' Getting puzzle ids for date range...', end='')
        results_df = pd.DataFrame(get_mini_ids(start_date, end_date))
        print('done')

        for token in tokens:
            print(f' Getting results for {token["name"]}...', end='')
            performance_data = [get_mini_results(token['token'], puzzle_id) for puzzle_id in results_df['puzzle_id']]
            performance_df = pd.DataFrame(performance_data).rename(columns={'secondsSpentSolving': 'time'})
            performance_df['time'] = performance_df['time'].fillna(0)
            performance_df['solved'] = performance_df['solved'].fillna(False)
            performance_df = performance_df.astype({'time': 'int'}).add_prefix(token['name']+'_')
            results_df = pd.concat([results_df, performance_df], axis=1)
            print('done')
    else:
        data = {
            'print_date': ['2024-07-22', '2024-07-21', '2024-07-20', '2024-07-19', '2024-07-18'],
            'Ben_solved': [True, True, True, None, True],
            'Ella_solved': [True, True, False, False, True],
            'Ben_time': [42, 160, 294, None, 60],
            'Ella_time': [60, 85, 337, 234, 60]
        }
        results_df = pd.DataFrame(data)

    # Manipulate using Pandas  
    results_df = results_df[['print_date', 'Ben_solved', 'Ella_solved', 'Ben_time', 'Ella_time']]
    results_df['Ben_win'] = np.where((results_df['Ben_solved'] & results_df['Ella_solved'] & (results_df['Ben_time'] < results_df['Ella_time'])) | (results_df['Ben_solved'] & ~results_df['Ella_solved']), True, False)
    results_df['Ella_win'] = np.where((results_df['Ben_solved'] & results_df['Ella_solved'] & (results_df['Ella_time'] < results_df['Ben_time'])) | (results_df['Ella_solved'] & ~results_df['Ben_solved']), True, False)
    
    results_df = results_df.sort_values(by='print_date')
    results_df['Ben_cum_wins'] = results_df['Ben_win'].cumsum()
    results_df['Ella_cum_wins'] = results_df['Ella_win'].cumsum()

    # Calculate stats
    stats_df = pd.DataFrame()
    for token in tokens:
        stats_df = pd.concat([stats_df, player_mini_stats(token["name"], results_df)])

    # Output (save to csv or print to console?)
    print('\n'+results_df.to_string(index=False))
    print('\n'+stats_df.to_string(index=False)+'\n')


    




'''

Read tokens

using first token, get list of dates + ids

For each mini id, get specific data for each player (in 'calcs' -> percentFilled, secondsSpentSolving, solved)

Save info to data structure / dataframe

Output dataframe with calculations to a csv

'''