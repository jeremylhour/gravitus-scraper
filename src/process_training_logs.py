#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
process_training_logs:
    Functions to process training logs
    
Created on Mon May 30 12:44:59 2022

@author: jeremylhour
"""
import re
import json
from datetime import datetime

# Define the replacement dictionary for normalizing name of exercises
REPL_DICT = {
    '2 Count Paused Deadlift': '2ct Paused Deadlift @ 1 Inch Off Floor',
    '2Ct Paused Bench Press': '2ct Pause Bench Press',
    '2Ct Paused Incline Bench Press': '2ct Paused Incline Bench Press',
    '2Ct Paused Squat': 'Paused Squats',
    '2Inch Deficit Deadlift': '2" Deficit Deadlift',
    '2Inches Deficit Deadlift': '2" Deficit Deadlift',
    '3-0-3 Tempo Squat': '3.0.3 Tempo Squat',
    '3Ct Paused Bench Press':'3ct Paused Bench Press',
    'Barbell Curls': 'Barbell Curl',
    'Barbell Rows': 'Barbell Row',
    'Barbell Rows (Myo Reps)': 'Barbell Row',
    'Beltless Deadlift': 'Beltless Conventional Deadlift',
    'Beltless Ohp': 'Beltless Press',
    'Beltless Overhead Press': 'Beltless Press',
    'Beltless Squat (Myo Reps)': 'Beltless Squat',
    'Bike (Liss)': 'Bike',
    'Block Pull': 'Rack Pull',
    'Close-Grip Bench Press': 'Close-Grip Bench Press',
    'Hbbs': 'High-Bar Squat',
    'High Bar Squat': 'High-Bar Squat',
    'High-Bar Back Squat': 'High-Bar Squat',
    'Liss (Bike)': 'Bike',
    'Planks': 'Plank',
    'Preacher Curls': 'Preacher Curl',
    'Press (No Belt)': 'Beltless Press',
    'Pull Up': 'Pull-Up',
    'Pull Ups': 'Pull-Up',
    'Push Down': 'Pushdown',
    'Romanian Deadlifts': 'Romanian Deadlift',
    'Rows': 'Barbell row',
    'Slingshot Bench': 'Slingshot Bench Press',
    'Squat (No Belt)': 'Beltless Squat',
    'Tractions': 'Pull-Up',
    'Triceps Push Down': 'Pushdown',
    'Triceps Pushdown': 'Pushdown',
    'Triceps Pushdown (Rope)': 'Pushdown',
    'Triceps Pushdown (With The Rope)': 'Pushdown'
}

def break_raw_data(raw_data: str) -> str:
    """
    break_raw_data:
        break the raw log data into workouts
        
    @param raw_data (str):
    """
    return raw_data.split("\n \n")

def format_exercise_name(raw_name: str) -> str:
    """
    format_exercise_name:
    
    @param raw_name (str): raw name from manual logs
    """
    name = raw_name.title()
    for raw, clean in REPL_DICT.items():
        name = name.replace(raw, clean)
    return name

def process_one_workout(workout: str) -> dict:
    """
    process_one_workout:
        process one workout to the format that comes out of the processing
        of Gravitus data
        
    @param workout (str): the raw workout data to be parsed
    """
    # Define regular expressions
    load_re = r"[[0-9]*[,]?]?[0-9]+\s?k?g?\s?" 
    reps_re = r"x\s[0-9]+\s?"
    rpe_re = r"@?[[0-9]*[,\.]?]?[0-9]+?\s?"
    repeated_re = r"x?\s?[0-9]*"
    repeated_re_at_the_end = r"x\s?[0-9]+.*(x\s?[0-9]+$)"
    
    parsedWorkout = {}
    
    # Process the workout
    lines = workout.split("\n")
    if len(lines) < 2:
        return parsedWorkout
    headline = lines[0].split(":")
    parsedWorkout['title'] = headline[1].strip()
    parsedWorkout['date'] = headline[0].strip().replace("/", "-")
    
    parsedWorkout['work'] = {}
    for line in lines[1:]:
        exercise = format_exercise_name(line.split(":")[0].strip())
        parsedWorkout['work'][exercise] = []
        
        for item in re.findall(load_re+reps_re+rpe_re+repeated_re, line):
            # Main expression
            rest_of_the_item = re.findall(load_re+reps_re+rpe_re, item)[0]
            parsed_item = rest_of_the_item.replace('kg', '').replace(',', '.').replace(' ', '').replace('@', ' @')
            
            # repeated if any
            repeated = re.findall(repeated_re_at_the_end, item)
        
            if repeated:
                n_ = int(re.findall(r"[0-9]",repeated[0])[0])
            else:
                n_ = 1
                
            for i in range(int(n_)):
                parsedWorkout['work'][exercise].append(parsed_item)
    return parsedWorkout

def process_log_data(raw_data: str) -> list:
    """
    process_log_data:
        process the whole log data file
    
    @param raw_data (str):
    """
    # Step 1: break each workout
    workouts = break_raw_data(raw_data)
    
    # Step 2: process each workout
    parsedWorkouts = []
    for workout in workouts:
        parsedWorkout = process_one_workout(workout)
        if len(parsedWorkout) > 0:
            parsedWorkouts.append(
                parsedWorkout
                )
    return parsedWorkouts
          

if __name__ == "__main__":
    print("\nThis script parses the manual data workouts.\n")
    now = datetime.now()
    print(f"Launched on {now.strftime('%d, %b %Y, %H:%M:%S')} \n")
    
    parsedWorkouts = []
    
    for year in ["2122", "2223"]:
        print(f"Parsing manual workouts data for year {year}")
        with open(f"data/manual_data/training_log_{year}.txt", "r") as f:
            raw_data = ' '.join([line for line in f.readlines()])    
        parsedWorkouts += process_log_data(raw_data)
    
    with open("data/manual_data/parsed_training_log.json", "w") as f:
        json.dump(parsedWorkouts, f)