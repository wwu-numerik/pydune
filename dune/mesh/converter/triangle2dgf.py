#!/usr/bin/python
"""
triangle2dgf.py (c) 2009 felix.albrecht@uni-muenster.de
Licence: WTFPLv2, see LICENSE.txt
"""

import sys
import math
import os
import time

## global defines

# about the correctness of the triangle files
triangle_nodefile_incorrect = 0
triangle_polyfile_incorrect = 0
triangle_elefile_incorrect = 0

# about the filenames

## done with global defines


## function definitions

# read vertices from a .node file generated by triangle
def read_vertices(filename) :
	print('reading vertices from %s...' % (filename), end=' ')
	global triangle_nodefile_incorrect
	list_of_vertices = []
	file = open(filename, 'r')
	number_of_vertices = 0
	number_of_vertices_set = 0
	vertex_number = 0
	for line in file.readlines():
		words = line.split()
		if words[0] != '#':
			if number_of_vertices_set == 0:
				if len(words) == 4:
					number_of_vertices = int(words[0])
					number_of_vertices_set += 1
			else:
				if vertex_number < number_of_vertices:
					if int(words[0]) == vertex_number:
						x = float(words[1])
						y = float(words[2])
						vertex = [x, y]
						list_of_vertices.append(vertex)
					else:
						if number_of_vertices != vertex_number:
							triangle_nodefile_incorrect += 1
					vertex_number += 1
	print('\t\tfound %i vertices' % (number_of_vertices))
	return list_of_vertices

# read faces from a .poly file, returns [ [ vertex_one, vertex_two, boundary_id ], ... ]
def read_faces(filename):
	print('reading faces from %s...' % (filename), end=' ')
	global triangle_polyfile_incorrect
	list_of_faces_with_ids = []
	file = open(filename, 'r')
	number_of_faces = 0
	number_of_faces_set = 0
	face_number = 0
	for line in file.readlines():
		words = line.split()
		if words[0] != '#':
			if number_of_faces_set == 0:
				if len( words ) == 2:
					number_of_faces = int(words[0])
					number_of_faces_set += 1
			else:
				if face_number < number_of_faces:
					if int(words[0]) == face_number:
						vertex_one = int(words[1])
						vertex_two = int(words[2])
						boundary_id = int(words[3])
						list_of_faces_with_ids.append([vertex_one, vertex_two,
														boundary_id])
					else:
						if number_of_faces != face_number:
							triangle_polyfile_incorrect += 1
					face_number += 1
	print('\t\tfound %i faces' % (number_of_faces))
	return list_of_faces_with_ids

# read simplices from a .ele file, returns [ [ vertex_one, vertex_two, vertex_three ], ... ]
def read_simplices(filename, faces):
	print('reading simplices from %s...' % (filename), end=' ')
	global triangle_elefile_incorrect
	list_of_simplices = []
	file = open(filename, 'r')
	number_of_simplices = 0
	number_of_simplices_set = 0
	simplex_number = 0
	for line in file.readlines():
		words = line.split()
		if words[0] != '#':
			if number_of_simplices_set == 0:
				if len(words) == 3:
					number_of_simplices = int(words[0])
					number_of_simplices_set += 1
			else:
				if simplex_number < number_of_simplices:
					if int(words[0]) == simplex_number:
						simplex = []
						for i in range(1, 4):
							simplex.append(int(words[i]))
						list_of_simplices.append(simplex)
					else:
						if simplex_number != number_of_simplices:
							triangle_elefile_incorrect += 1
					simplex_number += 1
	print('\t\tfound %i simplices' % (simplex_number))
	return list_of_simplices


# write the dgf header into the dgf file
def write_dgf_header(file):
	file.write('DGF\t\t\t\t\t\t%s %s, generated by triangle2dgf.py on %s \n' %
				('%', file.name, time.strftime('%Y/%m/%d %H:%M:%S')))
	#file.write( '% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n' )
	#file.write( '%s %s\n' %( '%', file.name ) )
	#file.write( '%s written by triangle2dgf.py on %s\n' %( '%', time.strftime('%Y/%m/%d %H:%M:%S') ) )
	#file.write( '% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n' )


# write vertices to dgf file
def write_vertices(vertices,file):
	print('writing vertices to %s...' % (file.name), end=' ')
	file.write('VERTEX\t\t\t\t\t% the vertices of the grid\n')
	if triangle_nodefile_incorrect == 0:
		vertex_number = 0
		for vertex in vertices:
			file.write('%f\t%f\t%s vertex %i\n' %
						( vertex[0], vertex[1], '%', vertex_number))
			vertex_number += 1
		file.write('#\n')
		print('\t\t%i vertices written' % (vertex_number))
	else :
		print('error: write_vertices() not implemented for nonconforming .node file')
		sys.exit()

# write simplices to dgf file
def write_simplices(simplices, file) :
	print('writing simplices to %s...' % (file.name), end=' ')
	file.write('SIMPLEX\t\t\t\t\t% the simplices of the grid\n')
	if triangle_elefile_incorrect == 0:
		simplex_number = 0
		for simplex in simplices:
			file.write('%i\t%i\t%i\t\t\t\t%s simplex %i, consisting of vertices %i, %i and %i\n' %( simplex[ 0 ], simplex[ 1 ], simplex[ 2 ], '%', simplex_number, simplex[ 0 ], simplex[ 1 ], simplex[ 2 ] ) )
			simplex_number += 1
		file.write( '#\n' )
		print('\t\t%i simplices written' %( simplex_number ))
	else :
		print('error: write_simplices() not implemented for nonconforming .ele file')
		sys.exit()

# write boundary segments to dgf file
def write_boundary_segments( faces_with_ids, file ) :
	print('writing boundary segments to %s...' %( file.name ), end=' ')
	file.write( 'BOUNDARYSEGMENTS\t\t% the boundary segments of the grid\n' )
	if triangle_polyfile_incorrect == 0 :
		boundary_segment_number = 0
		for face_with_id in faces_with_ids :
			vertex_one = face_with_id[ 0 ]
			vertex_two = face_with_id[ 1 ]
			id = face_with_id[ 2 ]
			file.write( '%i\t%i\t%i\t\t\t\t%s boundary ID %i between vertices %i and %i\n' %( id, vertex_one, vertex_two, '%', id, vertex_one, vertex_two ) )
			boundary_segment_number += 1
		file.write( '#\n' )
		file.write( 'BOUNDARYDOMAIN\n' )
		file.write( 'default 1\n' )
		file.write( '#\n')
		print('\t%i boundary segments written' %( boundary_segment_number ))
	else :
		print('error: write_boundary_segments() not implemented for nonconforming .poly file')
		sys.exit()

## done with function definitions


def main():
	filename_prefix = sys.argv[ 1 ]
	dgf_filename = '%s.dgf' %( filename_prefix )
	nodefile_filename = filename_prefix + '.node'
	polyfile_filename = filename_prefix + '.poly'
	elefile_filename = filename_prefix + '.ele'

	dgf_file = open( dgf_filename, 'w' )

	vertices = read_vertices( nodefile_filename )
	if triangle_nodefile_incorrect != 0 :
		print('error: the triangle nodefile is incorrect')
		sys.exit()

	faces_with_boundary_ids = read_faces( polyfile_filename )
	if triangle_polyfile_incorrect != 0 :
		print('error: the triangle polyfile is incorrect')
		sys.exit()
		
	simplices = read_simplices( elefile_filename, faces_with_boundary_ids )
	if triangle_nodefile_incorrect != 0 :
		print('error: the triangle nodefile is incorrect')
		sys.exit()

	write_dgf_header( dgf_file )
	write_vertices( vertices, dgf_file )
	write_simplices( simplices, dgf_file )
	write_boundary_segments( faces_with_boundary_ids, dgf_file )
