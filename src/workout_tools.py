#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
workout_tools:
    Different functions to handle workout data
    (converters, e1rm estimator, etc.)

Created on Sun May 29 14:18:20 2022

@author: jeremylhour
"""
import re
import json
from datetime import datetime
import pandas as pd
from functools import partial

# ---------------------------------------------------------
# LOAD CONSTANTS
# ---------------------------------------------------------
with open('config/rpe_table.json', 'rb') as f:
    RPE_TABLE = json.load(f)

# ---------------------------------------------------------
# PARSING THE RAW DATA
# ---------------------------------------------------------
def lbs_to_kg(x, reverse=False, digits=1):
    """
    convertLBStoKG:
        Convert from lbs to kg, or the reverse
        
    @param x (float):
    @param reverse (bool): If True, convert from kg to lbs
    """
    KG_IN_LBS = 2.2046226218
    
    if reverse:
        return round(x * KG_IN_LBS, digits)
    else:
        return round(x / KG_IN_LBS, digits)
    
def e1RM(load, reps, rpe=None):
    """
    e1RM:
        1-rep max estimator from RPE table
        
    @param load (float):
    @param reps (int or str): 
    @param rpe (int or str):
    """
    # variable check
    if isinstance(reps, str):
        reps = int(reps)
        
    if isinstance(rpe, str):
        rpe = float(rpe)
    
    if isinstance(rpe, float) and (rpe % 1 == 0):
        rpe = int(rpe)       
    
    # check range
    if reps not in range(1, 11):
        reps = 10
    if rpe is None or rpe < 6.5:
        rpe = 6.5
        
    return 100. * load / RPE_TABLE.get(str(reps)).get(str(rpe))
    
def parse_set(x, convert_to_kg = True):
    """
    parse_set:
        parse the set to collect infos
        
    @param x (str): e.g. '308.65x1', '264.55x5 @6'
    @param convert_to_kg (bool): If True, converts to kg
    """
    # Load
    load = re.findall(r"(.*)x", x)
    if load:
        load = float(load[0])
        if convert_to_kg:
            load = lbs_to_kg(load)
    else:
        load = None
    
    # Reps
    reps = re.findall(r"x(.+?)\b", x)
    if reps:
        reps = int(reps[0])
    else:
        reps = None
    
    # RPE
    rpe = re.findall(r"@(.*)$", x)
    if rpe:
        rpe = float(rpe[0])
    else:
        rpe = None
    return load, reps, rpe
    
def get_e1RM_from_sets(sets, convert_to_kg = True):
    """
    get_e1RM_from_sets:
        get the e1RM from sets of a given exercise
    
    @param sets (list of str):
    @param convert_to_kg (bool): If True, converts to kg
    """
    top_set = 0.
    for item in sets:
        top_set = max(top_set, e1RM(*parse_set(item, convert_to_kg)))            
    return top_set

def get_top_set(sets, convert_to_kg = True):
    """
    get_top_set:
        get the top set for a given exercise
    
    @param sets (list of str):
    @param convert_to_kg (bool): If True, converts to kg
    """
    top_set = 0.
    for item in sets:
        load, reps, rpe = parse_set(item, convert_to_kg)
        top_set = max(top_set, load)       
    return top_set

def get_top_single(sets, convert_to_kg = True):
    """
    get_top_single:
        get the top single of an exercise
        
    @param sets (list of str):
    @param convert_to_kg (bool): If True, converts to kg
    """
    top_set = None
    for item in sets:
        load, reps, rpe = parse_set(item, convert_to_kg)
        if reps == 1:
            if top_set is None:
                top_set = load
            else:
                top_set = max(top_set, load)
    return top_set

def get_tonnage(sets, convert_to_kg = True):
    """
    get_tonnage:
        get the tonnage of an exercise
        
    @param sets (list of str):
    """
    tonnage = 0.
    for item in sets:
        load, reps, rpe = parse_set(item, convert_to_kg)
        tonnage += load*reps
    return tonnage

# ---------------------------------------------------------
# GET PERFORMANCE
# ---------------------------------------------------------
def get_historical_performance(exercise, workouts, mode="e1RM", convert_to_kg=True):
    """
    get_historical_performance:
        
    @param exercise (str):
    @param workouts (list):
    @param mode (str):
    @param convert_to_kg (bool): If True, converts to kg
    """
    if mode == "e1RM":
        perf_getter = partial(get_e1RM_from_sets, convert_to_kg=convert_to_kg)
    elif mode == "top-set":
        perf_getter = partial(get_top_set, convert_to_kg=convert_to_kg)
    elif mode == "tonnage":
        perf_getter = partial(get_tonnage, convert_to_kg=convert_to_kg)
    else:
        raise ValueError("'mode' arg must be either tonnage, e1RM or top-set.")
    
    df = {}
    for workout in workouts:
        if exercise in workout['work'].keys():
            try:
                event_date = datetime.fromisoformat(workout['date']).strftime('%Y-%m-%d')
            except:
                event_date = datetime.strptime(workout['date'], "%d-%m-%Y")
            df[event_date] = perf_getter(workout['work'][exercise])
    
    if len(df) > 0:
        df = pd.DataFrame(df.values(), index=df.keys())
        df.columns = [exercise]
        df.index = pd.to_datetime(df.index)
        return df.sort_index()
    else:
        return None

if __name__ == "__main__":
    pass