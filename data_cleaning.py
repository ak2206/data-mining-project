import pandas as pd
import numpy as np
from fastkml import kml
from io import StringIO
import sys
import os
import re
from shutil import copyfile


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
    rit_coords = [-1*(77+(40/60)+(30/360)), 43 + 5/60 + 6/360]
    home_coords = [-1*(77+26/60+17/360), 43+8/60+17/360]
    with open(file_name, 'rt', encoding="utf-8") as myfile:
        doc = myfile.read()
        k = kml.KML()
        k.from_string(doc)
        kml_doc = next(k.features())
        data = next(kml_doc.features()).geometry.coords
        df = pd.DataFrame(data)
        # df is now a Pandas data frame of all the coordinate entries in the kml file
        reached_rit = False
        reached_home = False

        first_point = df.iloc[0]  # the first row
        last_point = df.iloc[-1]  # the last row
        points = [first_point, last_point]

        for point in points:
            if distance_between_points(rit_coords, point) < 0.1:
                reached_rit = True
            else:
                if distance_between_points(home_coords, point) < 0.078:
                    reached_home = True

        if reached_rit and reached_home:
            print(file_name + " has an endpoint at RIT and Home")
            return 1
        else:
            if reached_rit:
                print(file_name + " does not have an endpoint at Home")
            else:
                if reached_home:
                    print(file_name + " does not have an endpoint at RIT")
                else:
                    print(file_name + " does not have an endpoint at Home nor RIT")
        return 0


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
