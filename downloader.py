#!/usr/bin/env python3

"""
Description: Download stats for mini crossword and wordle from nyt website
"""

# Imports
import json
import requests

# Constants

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
        print('Error retrieving data: '+response.status_code)
        return
    # Return calculated results
    return response.json()['calcs']

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

    print(get_mini_ids('2024-07-20', '2024-07-22'))
    print('------------')

    url = 'https://www.nytimes.com/svc/crosswords/v3/36569100/puzzles.json?publish_type=mini&date_start=2024-07-16&date_end=2024-07-22'
    
    # Read tokens from file
    with open('tokens.json', 'r') as file:
        tokens = json.load(file)
    for token in tokens:
    #     print(f"Name: {token['name']}, Token: {token['token']}")
    # token = tokens[0]['token']
    # print(token)
    
        # Query NYT
        # Define the URL and headers
        headers = {
            'Cookie': f'nyt-s={token["token"]};',
            'Accept': 'text/plain',
        }
        # Send the GET request with headers
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data['status'] != 'OK':
                print('status not OK')
                print(data)
            else:
                print(f'({token["name"]}) data read successfully')
                data = data['results']
                for line in data:
                    print(line)
        else:
            print(f"Error: {response.status_code}")
            print(response.text)

    # Manipulate using Pandas

    # Output (save to csv or print to console?)




'''

Read tokens

using first token, get list of dates + ids

For each mini id, get specific data for each player (in 'calcs' -> percentFilled, secondsSpentSolving, solved)

Save info to data structure / dataframe

Output dataframe with calculations to a csv

'''