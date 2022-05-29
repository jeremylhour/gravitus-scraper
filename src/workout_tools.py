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

# ---------------------------------------------------------
# FUNCTIONS
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
        1-rep max estimator
        
    @param load (float):
    @param reps (int): 
    @param rpe (int):
    """
    RPE_TABLE = {
        1: {
            10: 100,
            9.5: 98,
            9: 96,
            8.5: 94,
            8: 92,
            7.5: 91,
            7: 89,
            6.5: 88
            },
        2: {
            10: 96,
            9.5: 94,
            9: 92,
            8.5: 91,
            8: 89,
            7.5: 88,
            7: 86,
            6.5: 85
            },
        3: {
            10: 92,
            9.5: 91,
            9: 89,
            8.5: 88,
            8: 86,
            7.5: 85,
            7: 84,
            6.5: 82
            },
        4: {
            10: 89,
            9.5: 88,
            9: 86,
            8.5: 85,
            8: 84,
            7.5: 82,
            7: 81,
            6.5: 80
            },
        5: {
            10: 86,
            9.5: 85,
            9: 84,
            8.5: 82,
            8: 81,
            7.5: 80,
            7: 79,
            6.5: 77
            },
        6: {
            10: 84,
            9.5: 82,
            9: 81,
            8.5: 80,
            8: 79,
            7.5: 77,
            7: 76,
            6.5: 75
            },
        7: {
            10: 81,
            9.5: 80,
            9: 79,
            8.5: 77,
            8: 76,
            7.5: 75,
            7: 74,
            6.5: 72
            },
        8: {
            10: 79,
            9.5: 77,
            9: 76,
            8.5: 75,
            8: 74,
            7.5: 72,
            7: 71,
            6.5: 69
            },
        9: {
            10: 76,
            9.5: 75,
            9: 74,
            8.5: 72,
            8: 71,
            7.5: 69,
            7: 68,
            6.5: 67
            },
        10: {
            10: 74,
            9.5: 72,
            9: 71,
            8.5: 69,
            8: 68,
            7.5: 67,
            7: 65,
            6.5: 64
            },
        }
    
    if reps not in range(1, 11):
        reps = 10
    if rpe is None or rpe < 6.5:
        rpe = 6.5
    return 100. * load / RPE_TABLE.get(reps).get(rpe)
    
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
    
def get_e1RM_from_sets(sets):
    """
    get_e1RM_from_sets:
        get the e1RM from sets of a given exercise
    
    @param sets (list of str):
    """
    top_set = 0.
    for item in sets:
        top_set = max(top_set, e1RM(*parse_set(item)))            
    return top_set

def get_top_set(sets):
    """
    get_top_set:
        get the top set for a given exercise
    
    @param sets (list of str):
    """
    top_set = 0.
    for item in sets:
        load, reps, rpe = parse_set(item)
        top_set = max(top_set, load)       
    return top_set

def get_top_single(sets):
    """
    get_top_single:
        get the top single of an exercise
        
    @param sets (list of str):
    """
    top_set = None
    for item in sets:
        load, reps, rpe = parse_set(item)
        if reps == 1:
            if top_set is None:
                top_set = load
            else:
                top_set = max(top_set, load)
                
    return top_set

if __name__ == "__main__":
    pass