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
	kml_obj = fastkml.kml.KML()
	
	with open(filename) as file:
		kml_obj.from_string(file.read().encode("utf-8"))
	
	return kml_obj

def get_kml_document(kml_obj: fastkml.kml.KML) -> fastkml.Document:
	return next(kml_obj.features())

def get_kml_coordinates(kml_obj: fastkml.kml.KML) -> Path:
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
	# Get distances for each dimension in a common unit, meters.
	lat_dist = (c1.lat - c2.lat) * LAT_RATIO
	long_dist = (c1.lon - c2.lon) * LONG_RATIO
	return math.sqrt(lat_dist**2 + long_dist**2)

def annotate_hazards(kml_obj: fastkml.kml.KML) -> None:
	import hazards
	
	kml_document = get_kml_document(kml_obj)
	hazards.add_hazard_style(kml_obj)
	
	hazard_list = hazards.get_hazards(get_kml_coordinates(kml_obj))
	
	for hazard in hazard_list:
		kml_document.append(hazards.build_hazard_placemark(hazard))

def calc_total_dist(path: Path) -> float:
	return sum(
		calc_dist(*cs)
		for cs in iter_n(path, 2)
	)

def avg(iterable: Iterable[Num]) -> float:
	sum_nums = 0
	nums = 0
	
	for num in iterable:
		sum_nums += num
		nums += 1
	
	return sum_nums / nums

def calc_average_speed(path: Path) -> float:
	return KNOTS_TO_MPS_RATIO * avg(
		coords.speed
		for coords in path
	)

def total_cost(path: Path) -> float:
	distance = calc_total_dist(path)
	avg_speed = calc_average_speed(path)
	
	SPEED_DISTANCE_COST_RATIO = 7865.099
	
	# Roughly, total distance is twice as important as speed.
	return (
		(distance * 1) +
		(-avg_speed * SPEED_DISTANCE_COST_RATIO)
	)

def get_best_kml_file(directory_name: str) -> fastkml.kml.KML:
	return min(
		os.listdir(directory_name),
		key=lambda filename: total_cost(get_kml_coordinates(get_kml_object(os.path.join(directory_name, filename)))),
	)


if __name__ == "__main__":
	"""
	if len(sys.argv) < 2:
		raise Exception("No KML file name provided.")
	
	kml_object = get_kml_object(sys.argv[1])
	kml_document = next(kml_object.features())
	
	geometry_obj = next(kml_document.features()).geometry
	coords_path = [
		Coordinates(*co_tuple)
		for co_tuple in geometry_obj.coords
	]
	
	
	
	print(f"Total distance: {calc_total_dist(coords_path)}")
	print(f"Average speed: {calc_average_speed(coords_path)}")
	
	pass
	"""
	print(get_best_kml_file("GOOD_KML_FILES_TO_WORK"))
