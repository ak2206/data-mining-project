#!/usr/bin/python3

import pandas as pd
import numpy as np
from fastkml import kml
from io import StringIO
import sys
import os
import re
from shutil import copyfile

from cost_evaluator import calc_dist, Coordinates, get_kml_coordinates

RIT_COORDS = Coordinates(-77.675, 43.085, 0)
KINSMAN_HOME_COORDS = Coordinates(-77.438, 43.138, 0)

def main():
    directory = "KML_FILES_TO_WORK"
    try:
        os.mkdir("GOOD_"+directory)
    except OSError:
        print("Creation of the directory %s failed" % ("Good"+directory))
    else:
        print("Successfully created the directory %s " % ("Good"+directory))
    for filename in os.listdir(directory):
        if filename.endswith(".kml"):
            file = str(os.path.join(directory, filename))
            if check(file) == 1:
                copyfile(file, "GOOD_"+file)
        else:
            continue


# Checks that the file has endpoints at each of the target locations
def check(file_name):
    
    with open(file_name, 'rt', encoding="utf-8") as myfile:
        doc = myfile.read()
    
    k = kml.KML()
    k.from_string(doc)
    coordinates = get_kml_coordinates(k)
    
    first_point = Coordinates(*coordinates[0])
    last_point = Coordinates(*coordinates[-1])

    reached_rit = False
    reached_home = False

    points = [first_point, last_point]
    
    for point in points:
        if calc_dist(RIT_COORDS, point) <= 1000:
            reached_rit = True
            
        elif calc_dist(KINSMAN_HOME_COORDS, point) < 500:
                reached_home = True

    if reached_rit and reached_home:
        print(file_name + " has an endpoint at RIT and Home")
        return check_for_jumps(coordinates)

    
    elif reached_rit:
        print(file_name + " does not have an endpoint at Home")
        
    elif reached_home:
        print(file_name + " does not have an endpoint at RIT")
    
    else:
        print(file_name + " does not have an endpoint at Home nor RIT")
    
    return 0


def check_for_jumps(coordinates) -> int:
    last_coord = Coordinates(*coordinates[0])
    current_coord = Coordinates(*coordinates[0])
    for coordinate in coordinates:
        current_coord = Coordinates(*coordinate)
        if calc_dist(last_coord, current_coord) > 100:
            return 0
        last_coord = current_coord
    print("------------------")
    return 1


def distance(a, b):
    return np.sqrt(np.square(a[0] - b[0]) + np.square(a[1] - b[1]))


def distance_between_points(a, b):
    LAT_RATIO = 111200
    LONG_RATIO = 81210
    LAT_to_LONG = LAT_RATIO/LONG_RATIO

    lat_dist = (a[0] - b[0]) * LAT_to_LONG
    long_dist = (a[1] - b[1])
    return np.sqrt(long_dist**2 + lat_dist**2)


if __name__ == '__main__':
    main()
