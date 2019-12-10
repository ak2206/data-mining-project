#!/usr/bin/python3

from fastkml import kml
import os
from shutil import copyfile

from cost_evaluator import calc_dist, Coordinates, get_kml_coordinates

RIT_COORDS = Coordinates(-77.675, 43.085, 0)
KINSMAN_HOME_COORDS = Coordinates(-77.438, 43.138, 0)


def validate_kml_files():
    """"
    Iterate through all files and check for invalid attributes.
    
    Such attributes are large, discontiguous jumps, and endpoints which aren't
    nearby where they're supposed to be.
    
    Files which don't have these attributes are copied over to the
    GOOD_KML_FILES_TO_WORK directory.
    
    Source files come from the KML_FILES_TO_WORK directory.
    """
    
    directory = "KML_FILES_TO_WORK"
    good_directory = f"GOOD_{directory}"
    if not os.path.isdir(good_directory):
        os.mkdir("GOOD_"+directory)
        print("Successfully created the directory %s " % ("Good"+directory))
        
    for filename in os.listdir(directory):
        if filename.endswith(".kml"):
            file = str(os.path.join(directory, filename))
            if check(file) == 1:
                copyfile(file, "GOOD_"+file)
        else:
            continue


def check(file_name):
    """
    Checks that the file has endpoints at each of the target locations
    and calls the method to check for large jumps between points
    :param file_name: the name of the kml file to be checked
    :return: integer indicating whether the file is good or bad
        (1 or 0 respectively)
    """
    
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
        # print(file_name + " has an endpoint at RIT and Home")
        return check_for_jumps(coordinates)
    
    return 0


def check_for_jumps(coordinates) -> int:
    """
    Checks for jumps of more than 100 meters between any two consecutive
    coordinates in the kml file
    
    :param coordinates: the list of coordinates
    :return: 1 or 0 indicating no jumps and jumps respectively
    """
    
    last_coord = Coordinates(*coordinates[0])
    current_coord = Coordinates(*coordinates[0])
    for coordinate in coordinates:
        current_coord = Coordinates(*coordinate)
        if calc_dist(last_coord, current_coord) > 100:
            return 0
        last_coord = current_coord
    return 1


if __name__ == '__main__':
    validate_kml_files()
