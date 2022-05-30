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


def break_raw_data(raw_data):
    """
    break_raw_data:
        break the raw log data into workouts
        
    @param raw_data (str):
    """
    return raw_data.split("\n \n")

def process_one_workout(workout):
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
        exercise = line.split(":")[0].strip()
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

def process_log_data(raw_data):
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
    
    with open("data/manual_data/training_log_2122.txt", "r") as f:
        raw_data = ' '.join([line for line in f.readlines()])
        
    parsedWorkouts = process_log_data(raw_data)
    
    with open("data/manual_data/parsed_training_log.json", "w") as fp:
        json.dump(parsedWorkouts, fp)