#!/usr/bin/python3

import math
import os
import sys
from typing import Iterable, List, NamedTuple, Sequence, TypeVar, Union

import fastkml

class Coordinates(NamedTuple):
	lon: float
	lat: float
	speed: float

# Type aliases
Num = Union[int, float]
Path = List[Coordinates]

# Meters in a single degree latitude at NY's longitude.
LAT_RATIO = 111200

# Meters in a single degree longitude at NY's latitude.
LONG_RATIO = 81210

# Meters in a single knot.
KNOTS_TO_MPS_RATIO = 0.51444

def get_kml_object(filename: str) -> fastkml.kml.KML:
	"""
	Return the representative KML object for the file at the given filename.
	"""
	
	kml_obj = fastkml.kml.KML()
	
	with open(filename) as file:
		kml_obj.from_string(file.read().encode("utf-8"))
	
	return kml_obj

def write_kml_object(kml_object: fastkml.kml.KML, filename: str) -> None:
	"""
	Write the given KML object into the specified file.
	"""
	
	with open(filename, "w+") as file:
		file.write(kml_object.to_string())

def get_kml_document(kml_obj: fastkml.kml.KML) -> fastkml.Document:
	"""
	Return the Document object of the given KML object.
	"""
	
	return next(kml_obj.features())

def get_kml_coordinates(kml_obj: fastkml.kml.KML) -> Path:
	"""
	Return the main list of coordinates from the given KML object.
	"""
	
	geometry_obj = next(get_kml_document(kml_obj).features()).geometry
	coords_path = [
		Coordinates(*co_tuple)
		for co_tuple in geometry_obj.coords
	]
	
	return coords_path
	

T = TypeVar("T")
def iter_n(sequence: Sequence[T], n: int) -> List[T]:
	"""
	Iterate through the given sequence n at a time, consuming only one each
	iteration.
	
	Examples:
	>>> list(iter_n([1,2,3,4,5,6], 2))
	[[1,2],[2,3],[3,4],[4,5],[5,6]]
	"""
	
	for i in range(len(sequence) - (n-1)):
		yield sequence[i:i+n]

def calc_dist(c1: Coordinates, c2: Coordinates = None) -> float:
	"""
	Return the distance in meters between the two given coordinates (in the 
	New York area).
	"""
	
	# Get distances for each dimension in a common unit, meters.
	lat_dist = (c1.lat - c2.lat) * LAT_RATIO
	long_dist = (c1.lon - c2.lon) * LONG_RATIO
	return math.sqrt(lat_dist**2 + long_dist**2)

def annotate_hazards(kml_obj: fastkml.kml.KML) -> None:
	"""
	Add markers to the KML file for stops and left turns.
	"""
	
	# Import inside the function, because otherwise would lead to a circular
	# 	import.
	import hazards
	
	kml_document = get_kml_document(kml_obj)
	hazards.add_hazard_style(kml_obj)
	
	hazard_list = hazards.get_hazards(get_kml_coordinates(kml_obj))
	
	for hazard in hazard_list:
		kml_document.append(hazards.build_hazard_placemark(hazard))

def calc_total_dist(path: Path) -> float:
	"""
	Return the total distance traveled by the coordinate path, in meters.
	"""
	
	return sum(
		calc_dist(*cs)
		for cs in iter_n(path, 2)
	)

def avg(iterable: Iterable[Num]) -> float:
	"""
	Return the average of the items of the given iterable.
	"""
	
	sum_nums = 0
	nums = 0
	
	for num in iterable:
		sum_nums += num
		nums += 1
	
	return sum_nums / nums

def calc_average_speed(path: Path) -> float:
	"""
	Return the average speed of the given coordinate path, in meters/second.
	"""
	
	return KNOTS_TO_MPS_RATIO * avg(
		coords.speed
		for coords in path
	)

def total_cost(path: Path) -> float:
	"""
	Return the total cost of the given coordinate path.
	
	The two considered factors are the total distance covered by the path, and
	the average speed of the path. The former is twice as important as the
	latter.
	"""
	
	distance = calc_total_dist(path)
	avg_speed = calc_average_speed(path)
	
	# Speed is less important, but gets a huge multiplier, because speed and
	# 	distance are in different units. Speed requires a high ratio to have
	# 	similar amounts of variation.
	SPEED_DISTANCE_COST_RATIO = 7865.099
	
	return (
		(distance * 1) +
		(-avg_speed * SPEED_DISTANCE_COST_RATIO)
	)

def get_best_kml_file(directory_name: str) -> fastkml.kml.KML:
	"""
	Search through the KML files in the given directory and return the one which
	best minimises the cost function.
	"""
	
	return min(
		os.listdir(directory_name),
		key=lambda filename: total_cost(get_kml_coordinates(get_kml_object(os.path.join(directory_name, filename)))),
	)


if __name__ == "__main__":
	# If this file is being run as a script, get and output the best KML file at
	# 	this directory.
	print(get_best_kml_file("GOOD_KML_FILES_TO_WORK"))
