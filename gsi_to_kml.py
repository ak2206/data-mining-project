#!/usr/bin/python3

import sys
from typing import List
import fastkml


def extract_gsi_lines(file_contents: str) -> List[str]:
	lines = file_contents.strip().splitlines()
	
	first_data_line_index = 0
	
	while not lines[first_data_line_index].startswith("$"):
		first_data_line_index += 1
	
	return lines[first_data_line_index:]

class GSIEntry:
	latitude: float
	longitude: float
	speed: float
	
	def __init__(self, line):
		data = line.split(",")
		
		if data[0] != "$GPRMC":
			raise Exception("GSIEntry can only parse GPRMC lines.")

		self.latitude = float(data[3]) // 100
		self.latitude += (float(data[3]) % 100) / 60
		if data[4] == "S":
			self.latitude *= -1
		
		self.longitude = float(data[5]) // 100
		self.longitude += (float(data[5]) % 100) / 60
		if data[6] == "W":
			self.longitude *= -1
		
		self.speed = data[7]

def convert_gsi_lines_to_entries(lines: List[str]) -> List[GSIEntry]:
	entries = []
	for line in lines:
		if line.startswith("$GPRMC"):
			try:
				entries.append(GSIEntry(line))
			
			except ValueError:
				continue
	
	return entries


style_id = "yellowPoly"
def convert_gsientries_to_kml(entries: List[GSIEntry]) -> fastkml.KML: #
	
	# Boilerplate for creating a new KML doc.
	kml = fastkml.KML()
	d = fastkml.Document()
	kml.append(d)
	
	s = fastkml.Style(id=style_id)
	d.append_style(s)
	
	s.append_style(fastkml.LineStyle(color="Af00ffff", width=6))
	s.append_style(fastkml.PolyStyle(color="7f00ff00"))
	
	p = fastkml.Placemark()
	d.append(p)
	p.styleUrl = "#" + style_id
	
	g = fastkml.geometry.Geometry(
		extrude=True,
		tessellate=True,
		altitude_mode="relativeToGround",
	)
	
	g.geometry = fastkml.geometry.LineString([
		(entry.longitude, entry.latitude, entry.speed)
		for entry in entries
	])
	
	p.geometry = g
	
	return kml
	

if __name__ == "__main__" and len(sys.argv) > 1:
	file_name = sys.argv[1]
	
	with open(file_name) as file:
		gsi_lines = file.read().strip().splitlines()
		
	first_data_line_index = 0
	
	while not gsi_lines[first_data_line_index].startswith("$"):
		first_data_line_index += 1
	
	gsi_lines = gsi_lines[first_data_line_index:]
	
	gsi_lines = [
		line
		for line in gsi_lines
		if line.startswith("$GPR")
	]
	
	kml = convert_gsientries_to_kml(
		convert_gsi_lines_to_entries(gsi_lines)
	)
	
	with open("foo.kml", "w+") as file:
		file.write(kml.to_string(prettyprint=True))
