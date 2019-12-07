import pandas as pd
import numpy as np
from fastkml import kml
from io import StringIO
import sys
import os


def main():
    files = ["Going_NoWhereFast.kml", "ZJ42_L2C_trip_home.kml"]
    for file in files:
        check(file)

    directory = "FILES_TO_WORK"
    for filename in os.listdir(directory):
        if filename.endswith(".kml") or filename.endswith(".TXT") or filename.endswith(".txt"):
            print(os.path.join(directory, filename))
        else:
            continue


def check(fileName):
    RITcoords = [-1*(77+(40/60)+(30/360)), 43 + 5/60 + 6/360]
    Homecoords = [-1*(77+26/60+17/360), 43+8/60+17/360]
    with open(fileName, 'rt', encoding="utf-8") as myfile:
        doc = myfile.read()
        newDoc = ""
        for line in doc.split("\n"):
            if not line.strip().startswith("<"):
                newDoc += line + "\n"

        df = pd.read_csv(StringIO(newDoc), header=None)
        reachedRIT = False
        reachedHome = False
        for row in df.values:
            if distance(RITcoords, row) < 0.09:
                reachedRIT = True
                if reachedHome:
                    break
            if distance(Homecoords, row) < 0.09:
                reachedHome = True
                if reachedRIT:
                    break
        if reachedRIT and reachedHome:
            print(fileName + " reaches RIT and Home")
        else:
            if reachedRIT:
                print(fileName + " does not reach Home")
            else:
                if reachedHome:
                    print(fileName + " does not reach RIT")
                else:
                    print(fileName + " does not reach Home nor RIT")


def distance(a, b):
    return np.sqrt(np.square(a[0] - b[0]) + np.square(a[1] - b[1]))


if __name__ == '__main__':
    main()
