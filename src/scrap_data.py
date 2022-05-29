#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main functions to scrap Gavitus workout data

Created on Sat Mar 19 15:39:02 2022

@author: jeremylhour
"""
import os
import bs4
import requests
from random import uniform
from time import sleep, time
from datetime import datetime
import yaml
import json
import pandas as pd

from requests_futures.sessions import FuturesSession


# ---------------------------------------------------------
# FUNCTIONS TO COLLECT THE WORKOUT URLs
# ---------------------------------------------------------
def createUrl(user: str, pageNb: int = 0):
    """
    createUrl :
        search for ads related to the given 'watchModel' arg in the cda
        
    @param user (str or int): user name
    @param pageNb (int): id of page
    
    @return: the url to call
    """
    return 'https://gravitus.com/users/'+str(user)+'/?page='+str(pageNb)

def collectWorkouts(user: str, session, out_folder: str = "data"):
    """
    collectWorkouts :
        loops through the pages of a Gravitus user and collect workout url
        
    @param user (str): user name
    @param session (): a requests.session() object
    @param out_folder (str): name of the folder for output
    
    @return: a list of dict {title, url} of length equal to the number of workouts\
        from the user
    """
    print(f'Collecting workouts for user : {user}')
    i = 1
    anotherPage = True
    workoutList = []
    
    while anotherPage:
        sleep(uniform(0, 4)) # random time to send request
        
        pageUrl = createUrl(user, pageNb=i)
        res = session.get(pageUrl)
        print(f'Page {i} -- Request status : {res.status_code}')
        
        soup = bs4.BeautifulSoup(res.text, 'html.parser') # parse the page
        workouts = soup.select('body > div > div.small-header-offset > div > div > div > div.title > a') # get workout title and url
        if not workouts:
            anotherPage = False
            print(f'{i+1} page(s) -- {len(workoutList)} workouts collected.')
        else:
            for item in workouts:
                workoutList.append({
                    'title': item.getText(),
                    'url' : item.get('href')
                    })
        i += 1
        
    # saving URLs to json file
    with open(out_folder+'/'+user+'/workout_url.json', 'w', encoding='utf8') as f:
        json.dump(workoutList, f, ensure_ascii=False)
    return workoutList

# ---------------------------------------------------------
# PARSE WORKOUT AFTER THE RESPONSE
# ---------------------------------------------------------
def workoutUrl(url_part):
    """
    createUrl :
        search for ads related to the given 'watchModel' arg in the cda
        
    @param url_part (str): user name
    
    @return: the url to call
    """
    "/workouts/2741936790/"
    return 'https://gravitus.com'+url_part

def _parseTheWorkout(body, workout):
    """
    _parseTheWorkout:
        parse the workout info at the lower level    
    
    @param body ():
    @param workout (dict): must contain 'url' key
    """
    soup = bs4.BeautifulSoup(body, 'html.parser')
    
    # parse title
    title_field = soup.select('body > div > div.small-header-offset > div > div > div.workout > div.title')
    title = title_field[0].get_text().strip()
    
    # parse description
    description_field = soup.select('body > div > div.small-header-offset > div > div > div.workout > div.description')
    if description_field:
        description = description_field[0].get_text().strip()
    else:
        description = ''
        
    # parse date
    date_field = soup.select('#started-at')
    date = date_field[0].get_text()
        
    # parse exercise names
    exercise_field = soup.select("body > div > div.small-header-offset > div > div > div > div > a")
    exercices = [item.get_text() for item in exercise_field]
    
    # parse sets for each exercise
    set_field = soup.select('body > div > div.small-header-offset > div > div > div > div.sets')
    sets = []
    for item in set_field:
        raw_set = item.get_text().split(",")
        sets.append(
            [i.strip() for i in raw_set]
        )
    
    # create dict
    return {
        'title': title,
        'url': workout.get('url'),
        'date': date,
        'description': description,
        'work': dict(zip(exercices, sets))
        }

# ---------------------------------------------------------
# SCRAP AND PARSE WORKOUT : ASYNC VERSION
# ---------------------------------------------------------
def _parseWorkoutInfoFromText(workout, out_folder):
    """
    _parseWorkoutInfoFromText :
        process the page for the given workout and output a dict with necessary info
        Basically a wrapper around _parseTheWorkout
        
    INFO :
        This is to be used with Async version.
    
    @param workout (dict): dict with keys {title, url, res}, with res the response from a 
        request as concurrent.futures._base.Future object
    @param out_folder (str): where to save the content of the workout in raw form
    """
    res = workout['res'].result()
    # SAVE HERE ALSO
    with open(out_folder+workout['url'][:-1]+'_raw.txt', 'w', encoding='utf8') as f:
        f.write(res.text)
        
    return _parseTheWorkout(
        body=res.text,
        workout=workout
        )

def workoutToDataFrameThreading(workoutList, out_folder):
    """
    workoutToDataFrameThreading:
        create a pd.DataFrame with all that info, but parallel version
    
    @param workoutList (list of dict): ('adTitle', 'adUrl')
    @param out_folder (str): name of the folder for output
    
    @return: a pd.DataFrame() with workout infos, workoutInfos as a list, and the elements
    of workoutList that raised an error
    """
    startTime = time()
    session = FuturesSession(max_workers=12)
    for workout in workoutList:
        workout['res'] = session.get(workoutUrl(workout['url']))
        
    workoutInfos, workoutErrors = [], []
    for workout in workoutList:
        try:
            parsedWorkout = _parseWorkoutInfoFromText(workout, out_folder=out_folder)
            workoutInfos.append(parsedWorkout)
        except:
            workoutErrors.append(workout)
    print(f'All {len(workoutList)} workouts downloaded and parsed in {time()-startTime} seconds.')
    
    # saving URLs of errors to json file
    with open(out_folder+'/not_downloaded_url.json', 'w', encoding='utf8') as f:
        json.dump([workout['url'] for workout in workoutErrors], f, ensure_ascii=False)
    print(f'{len(workoutErrors)} workout(s) not downloaded, but url(s) saved.')
    
    return pd.DataFrame(workoutInfos), workoutInfos, workoutErrors


if __name__ == "__main__":
    print("\nThis is a script to scrap and parse workout data from Gravitus.")
    now = datetime.now()
    print(f"Launched on {now.strftime('%d, %b %Y, %H:%M:%S')} \n")
    
    CONFIG_FILE = 'config/gravitus.yaml'
    with open(CONFIG_FILE, 'r') as stream:
        config = yaml.safe_load(stream)
        
    print(f"The configuration file can be found in {CONFIG_FILE}.")
    
    
    print(80 * "=")
    print("SCRAPING GRAVITUS")
    print(80 * "=")
    
    USER = str(config.get('USER_ID'))
    OUT_FOLDER = config.get('OUT_FOLDER')

    for chemin in [
            OUT_FOLDER,
            OUT_FOLDER+"/"+USER,
            OUT_FOLDER+"/"+USER+"/workouts"
            ]:
        if not os.path.exists(chemin):
            os.makedirs(chemin)
            
    session = requests.session()
    workoutList = collectWorkouts(
        user=USER,
        session=session,
        out_folder=OUT_FOLDER
        )
    
    print(80 * "=")
    print("SCRAPING EACH WORKOUT")
    print(80 * "=")
    
    df, workoutInfos, workoutErrors = workoutToDataFrameThreading(
        workoutList=workoutList,
        out_folder=OUT_FOLDER+"/"+USER
        )
    with open(OUT_FOLDER+"/"+USER+'/parsed_data.json', "w") as fp:
        json.dump(workoutInfos, fp)