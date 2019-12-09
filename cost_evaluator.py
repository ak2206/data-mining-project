import math
import sys
from typing import NamedTuple, List

import fastkml

import hazards

class Coordinates(NamedTuple):
	lon: float
	lat: float
	speed: float

# Type aliases
Path = List[Coordinates]

# Meters in a single degree latitude at NY's longitude.
LAT_RATIO = 111200

# Meters in a single degree longitude at NY's latitude.
LONG_RATIO = 81210

def get_kml_object(filename: str) -> fastkml.kml.KML:
	kml_obj = fastkml.kml.KML()
	
	with open(filename) as file:
		kml_obj.from_string(file.read().encode("utf-8"))
	
	return kml_obj

def get_kml_document(kml_obj: fastkml.kml.KML) -> None:
	return None

def calc_dist(c1: Coordinates, c2: Coordinates) -> float:
	# Get distances for each dimension in a common unit, meters.
	lat_dist = (c1.lat - c2.lat) * LAT_RATIO
	long_dist = (c1.lon - c2.lon) * LONG_RATIO
	return math.sqrt(lat_dist**2 + long_dist**2)

def annotate_hazards(kml_obj: fastkml.kml.KML, path: Path) -> None:
	hazards.add_hazard_style(kml_obj)
	
	hazard_list = hazards.get_hazards(path)
	
	for hazard in hazard_list:
		kml_obj
	


if __name__ == "__main__":
	if len(sys.argv) < 2:
		raise Exception("No KML file name provided.")
	
	kml_object = get_kml_object(sys.argv[1])
	kml_document = next(kml_object.features())
	
	geometry_obj = next(kml_document.features()).geometry
	coords_path = [
		Coordinates(*co_tuple)
		for co_tuple in geometry_obj.coords
	]
	
