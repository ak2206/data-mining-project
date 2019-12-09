import collections
import itertools
import math
import sys
from typing import Deque, Iterable, List, Sequence, NamedTuple, Tuple, TypeVar

import fastkml
from fastkml import kml

from cost_evaluator import *


T = TypeVar("T")
def iter_n(sequence: Sequence[T], n: int) -> List[T]:
	"""
	Iterate through the given sequence n at a time, consuming only one each
	iteration.
	
	Examples:
	>>> list(iter_n([1,2,3,4,5,6], 2))
	[[1,2],[2,3],[3,4],[4,5],[5,6]]
	"""
	
	for i in range(len(sequence) + 1):
		yield sequence[i:i+n]
	

def get_stops(path: Path) -> List[Coordinates]:
	"""
	Return a list of coordinates at which the device stopped.
	
	Go through the path, and if a certain number of coordinates in a row have a
	speed less than a certain other value, count it as a stop.
	"""
	
	# The number of coordinates in a row to check for a stop.
	min_stop_length = 5
	
	# The maximum speed to count as 'stopped'.
	max_stop_speed = 0.10
	
	stops = []
	
	in_continuous_stop = False
	for coordinate_group in iter_n(path, min_stop_length):
		# True if every coordinate in the current group is slower than the max
		# 	stop speed.
		is_stop = all(
			coord.speed <= max_stop_speed
			for coord in coordinate_group
		)
		
		if is_stop and not in_continuous_stop:
			# If this is a new, not-continued stop.
			stops.append(coordinate_group[0])
			in_continuous_stop = True
		
		elif not is_stop and in_continuous_stop:
			# If we're getting back up to speed.
			in_continuous_stop = False
		
	return stops

def calc_dist(c1: Coordinates, c2: Coordinates) -> float:
	# Get distances for each dimension in a common unit, meters.
	lat_dist = (c1.lat - c2.lat) * LAT_RATIO
	long_dist = (c1.lon - c2.lon) * LONG_RATIO
	return math.sqrt(lat_dist**2 + long_dist**2)

def calc_angle(c1: Coordinates, c2: Coordinates, c3: Coordinates) -> float:
	"""
	Find the angle between c1-c2 and c2-c3.
	"""
	
	return (
		math.atan2(c3.lat - c2.lat, c3.lon - c2.lon) -
		math.atan2(c1.lat - c2.lat, c1.lon - c2.lon)
	)

def get_left_turns(path: Path) -> List[Coordinates]:
	turn_segment_length = 35 # Meters
	min_left_turn_angle = 1.25*math.pi
	max_left_turn_angle = 1.75*math.pi
	
	left_turns = []
	
	# The indices of the three endpoints of the segments.
	p1 = 0
	p2 = 1
	p3 = 2
	
	try:
		# Keep looping until the segments reach the end of the path.
		while True:
			p1 += 1
			
			while calc_dist(path[p1], path[p2]) < turn_segment_length:
				p2 += 1
			
			if p3 <= p2:
				p3 = p2 + 1
			
			while calc_dist(path[p2], path[p3]) < turn_segment_length:
				p3 += 1
			
			# Get the angle between p1 and p3, with p2 as the vertex.
			angle = calc_angle(path[p1], path[p2], path[p3])
			
			if min_left_turn_angle <= angle <= max_left_turn_angle:
				left_turns.append(path[p1])
			
			
	except IndexError:
		pass
		
	return left_turns

hazard_style_id = "redMarker"
def add_hazard_style(kml_obj: kml.KML) -> None:
	stop_style = fastkml.Style(id=hazard_style_id)
	
	stop_icon_href = "https://cdn0.iconfinder.com/data/icons/small-n-flat/24/678111-map-marker-512.png"
	
	stop_style.append_style(fastkml.IconStyle(
		color="ff0000ff",
		icon_href=stop_icon_href,
	))
	
	kml_doc = next(kml_obj.features())
	
	kml_doc.append_style(stop_style)

def build_hazard_placemark(coords: Coordinates) -> fastkml.Placemark:
	placemark = fastkml.Placemark()
	placemark.styleUrl = f"#{hazard_style_id}"
	
	g = fastkml.geometry.Geometry(
		altitude_mode="relativeToGround",
	)
	
	g.geometry = fastkml.geometry.Point(coords)
	
	placemark.geometry = g
	
	return placemark

def remove_similar_coords(points: Iterable[Coordinates]) -> List[Coordinates]:
	# Minimum distance between hazards before we call them different. In meters.
	min_allowed_distance = 30
	
	points_q: Deque[Coordinates] = collections.deque(points)
	kept = []
	
	while len(points_q) > 0:
		 # Don't pop yet; we want to know when we've come back from the start.
		current_group = [points_q[0]]
		
		points_q.rotate()
		while points_q[0] is not current_group[0]:
			
			if any(
				calc_dist(group_point, points_q[0]) < min_allowed_distance
				for group_point in current_group
				):
				
				# This point is very close to the current group; include it.
				current_group.append(points_q.popleft())
			
			points_q.rotate()
		
		# Remove the original reference point from the queue, and add it as the
		# 	representative point to keep of the group.
		kept.append(points_q.popleft())
	
	return kept


def get_hazards(coords_path: Path) -> List[Coordinates]:
	stops = get_stops(coords_path)
	left_turns = get_left_turns(coords_path)
	
	# There's a *lot* of duplication of points both within and between the
	# 	hazard lists.
	# Let's join the lists together and cut down on that as much as we can.
	hazards = remove_similar_coords(itertools.chain(stops, left_turns))
	
	return hazards

if __name__ == "__main__":
	if len(sys.argv) < 2:
		raise Exception("No KML filename provided.")
	
	kml_object = get_kml_file(sys.argv[1])
	kml_document = next(kml_object.features())
	
	geometry_obj = next(kml_document.features()).geometry
	coords_path = [
		Coordinates(*co_tuple)
		for co_tuple in geometry_obj.coords
	]
	
	add_hazard_style(kml_object)
	
	hazards = get_hazards(coords_path)
	
	for hazard in hazards:
		kml_document.append(build_hazard_placemark(hazard))
	
	
	with open("/home/amy/Downloads/foo.kml", "w+") as file:
		file.write(kml_object.to_string(prettyprint=True))
	
	pass
