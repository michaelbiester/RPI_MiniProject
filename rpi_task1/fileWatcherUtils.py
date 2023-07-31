# runFileWatcherUtils.py
# 11.02.2023

"""
function to monitor a directory for changes
"""

import asyncio
import os
from collections import deque

def findFiles(fileDir): 
    """
        fileDir: directory to watch 
        
        returns:
            1) if files have been found:
            
            list of list; list is sorted
            1st list element is a 2-element list corresponding to
            the newest file as determined by the modification date
            
            each 2-element list has two elements
            1st element: object as returned from os.scandir()
            2nd element: modification date as float
            
            2) if no files have been found:
            
            None   
    """
    filesFound = [[entry, os.path.getmtime(entry)] for entry in os.scandir(fileDir) if entry.is_file() ]   
    # sort by modTime (newest file first)
    filesFound.sort(key=lambda x: x[1], reverse=True)
    return filesFound if len(filesFound) > 0 else None

async def watcher(fileDir, check_interval_s):
    """
        fileDir : directory which shall be watched / monitored for changes
        check_interval_s : time in seconds between successive checks
    """
    newest_file = newest_date = None
    files_in_dir = findFiles(fileDir)
    if files_in_dir is not None:
        newest_file, newest_date = files_in_dir[0]
    
    while True:
        await asyncio.sleep(check_interval_s)
        
        current_files_in_dir = findFiles(fileDir)
        if current_files_in_dir is not None:
            cur_newest_file, cur_newest_date = current_files_in_dir[0]
            if (newest_date is not None) and (cur_newest_date > newest_date):
                newest_file = cur_newest_file
                newest_date = cur_newest_date
                #                
                # todo: send a notification to an application
                # -> communicates, that file system has changed
                # it is still the application's responsibility to decide how to
                # apply this information (eg.: request an updated file)
                print(f"new file detected: {newest_file} with date {newest_date}")
    
async def watcher_deq(recentModDate_deq: deque, check_interval_s):
    """
        recentModDatedeq : deque with most recent modification dates
                           initially the deque must be initalised with Nones
    """
    previous_date = recentModDate[0]

    while True:
        await asyncio.sleep(check_interval_s)
        most_recent_date = recentModDate_deq[0]
        
        if most_recent_date_deq is not None:
            if previous_date is None:
                print(f"new file detected with date {most_recent_date}")
            if (previous_date is not None) and (most_recent_date > previous_date):
                print(f"new file detected with date {most_recent_date}")
            # update anyway
            previous_date = most_recent_date
