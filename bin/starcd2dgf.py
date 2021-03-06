#!/usr/bin/python
"""
starcd2dgf.py (c) 2009 felix.albrecht@uni-muenster.de
Licence: WTFPLv2, see LICENSE.txt
"""
from __future__ import print_function
import sys
import math
import os
import time
import numpy as np


## global defines

# about the correctness of the starcd files
starcd_vrtfile_incorrect = 0
starcd_celfile_incorrect = 0

# about the filenames

## done with global defines


## function definitions

# read vertices from a .vrt file generated by starcd
def read_vertices(filename) :
    print('reading vertices from %s...' % (filename))
    global starcd_vrtfile_incorrect
    list_of_vertices = []
    file = open(filename, 'r')
    number_of_vertices = 0
    vertex_number = 0
    for line in file.readlines():
        words = line.split()
        if len(words) == 4:
            number_of_vertices += 1
            vertex_number = int(words[0])
            if number_of_vertices == vertex_number:
                x = float(words[1])
                y = float(words[2])
                z = float(words[3])
                vertex = [x, y, z]
                list_of_vertices.append(vertex)
            else:
                starcd_vrtfile_incorrect += 1
        else:
            # we should only get here for the first two lines of the .vrt-file, i.e. when number_of_vertices still equals 0
            if number_of_vertices != 0:
                starcd_vrtfile_incorrect += 1
    print('\tfound %i vertices' % (vertex_number))
    return list_of_vertices



# read elements/cells from a .cel file generated by starcd
def read_cells(filename) :
    print('reading cells from %s...' % (filename))
    global starcd_celfile_incorrect
    list_of_original_cells = []
    file = open(filename, 'r')
    number_of_cells = 0
    number_of_cubes = 0
    number_of_prisms = 0
    cell_index = 0
    for line in file.readlines():
        words = line.split()
        if len(words) == 9:             # cube (second line)
            if cell_index == int(words[0]):
                number_of_cubes += 1
                cube_vertices = []
                for ii in np.arange(1,9):
                    cube_vertices.append(int(words[ii])-1)
                # change order of the vertices to fulfill the Dune numbering conventions
                cube_vertices[2], cube_vertices[3] = cube_vertices[3], cube_vertices[2]
                cube_vertices[6], cube_vertices[7] = cube_vertices[7], cube_vertices[6]
                list_of_original_cells.append(cube_vertices)
        elif len(words) == 7:           # prism (second line)
            if cell_index == int(words[0]):
                number_of_prisms += 1
                prism_vertices = []
                for ii in np.arange(1,7):
                    prism_vertices.append(int(words[ii])-1)
                list_of_original_cells.append(prism_vertices)
        elif len(words) == 5:           # first line for both cube and prism
            number_of_cells += 1
            cell_index = int(words[0])
        else:
            # we should only get here for the first two lines of the .cel-file, i.e. when number_of_cells still equals 0
            if number_of_cells != 0:
                starcd_celfile_incorrect += 1
    if (number_of_cubes+number_of_prisms) != number_of_cells:
        starcd_celfile_incorrect += 1
    print('\tfound {i} cells: {j} cubes and {k} prisms'.format(i=number_of_cells, j=number_of_cubes, k=number_of_prisms))
    return list_of_original_cells 
        
        
def make_simplices(list_of_vertices, list_of_original_cells) :
    print('creating simplices...')
    list_of_simplices = []
    map_of_faces = dict([])
    normsum = 0
    number_of_errors = 0
    for cell in list_of_original_cells:
        if len(cell) == 8:       # cube
            # creating simplices from a cube entity
            
            # append the center of the cube to the list_of_vertices
            center_cube = (np.asarray(list_of_vertices[cell[5]]) + np.asarray(list_of_vertices[cell[0]]) + np.asarray(list_of_vertices[cell[3]]) - np.asarray(list_of_vertices[cell[1]]))/2
            list_of_vertices.append(center_cube)
            index_center_cube = len(list_of_vertices)-1
            
            # each cube has six rectangular faces
            faces = [ [cell[0], cell[1], cell[3], cell[2]],
                      [cell[0], cell[1], cell[5], cell[4]],
                      [cell[1], cell[3], cell[7], cell[5]],
                      [cell[0], cell[2], cell[6], cell[4]],
                      [cell[4], cell[5], cell[7], cell[6]],
                      [cell[2], cell[3], cell[7], cell[6]] ]
            # for each rectangular face  i3 ---- i2   with the indices [i0, i1, i2, i3] for its 4 vertices
            #                            |        |
            #                            i0 ---- i1
            for face in faces:
                [i0, i1, i2, i3] = face
                face_as_string = "".join((str(x)+' ') for x in sorted(face))
                
                if face_as_string not in map_of_faces:                    
                    # calculate the barycenter of the face
                    center  = (np.asarray(list_of_vertices[i0]) + np.asarray(list_of_vertices[i2]))/2
                    center2 = (np.asarray(list_of_vertices[i1]) + np.asarray(list_of_vertices[i3]))/2
                    norm = np.linalg.norm(center - center2)
                    if norm > 0.01:
                        print('Error! {}'.format(norm))
                        normsum += norm
                        number_of_errors += 1
                    # append the center to the list of vertices
                    list_of_vertices.append(center)
                    # append this face to the map_of_faces
                    map_of_faces[face_as_string] = len(list_of_vertices)-1
                  
                # create the four simplices that belong to this cube and this face
                list_of_simplices.append([i0, i1, map_of_faces[face_as_string], index_center_cube])
                list_of_simplices.append([i1, i2, map_of_faces[face_as_string], index_center_cube])
                list_of_simplices.append([i2, i3, map_of_faces[face_as_string], index_center_cube])
                list_of_simplices.append([i3, i0, map_of_faces[face_as_string], index_center_cube])

        elif len(cell) == 6:       # prism
            # creating simplices from a prism entity
            
            # each prism has three rectangular faces
            faces = [ [cell[0], cell[2], cell[5], cell[3]],
                      [cell[2], cell[1], cell[4], cell[5]],
                      [cell[0], cell[1], cell[4], cell[3]] ]
            face_as_string = []
            ii = 0
            # for each rectangular face  i3 ---- i2   with the indices [i0, i1, i2, i3] for its 4 vertices
            #                            |        |
            #                            i0 ---- i1
            for face in faces:
                [i0, i1, i2, i3] = face
                face_as_string.append( "".join((str(x)+' ') for x in sorted(face)) )
                
                if face_as_string[ii] not in map_of_faces:
                    # calculate the barycenter of the face
                    center  = (np.asarray(list_of_vertices[i0]) + np.asarray(list_of_vertices[i2]))/2
                    # append the center to the list of vertices
                    list_of_vertices.append(center)
                    # append this face to the map_of_faces
                    map_of_faces[face_as_string[ii]] = len(list_of_vertices)-1
                ii += 1 
            
            # create the simplices that belong to this prism
            list_of_simplices.append([cell[0], cell[3], map_of_faces[face_as_string[0]], map_of_faces[face_as_string[2]]])
            list_of_simplices.append([cell[0], cell[2], map_of_faces[face_as_string[0]], map_of_faces[face_as_string[2]]])
            list_of_simplices.append([cell[2], cell[5], map_of_faces[face_as_string[0]], map_of_faces[face_as_string[2]]])
            list_of_simplices.append([cell[5], cell[3], map_of_faces[face_as_string[0]], map_of_faces[face_as_string[2]]])
            
            list_of_simplices.append([cell[1], cell[2], map_of_faces[face_as_string[1]], map_of_faces[face_as_string[2]]])
            list_of_simplices.append([cell[1], cell[4], map_of_faces[face_as_string[1]], map_of_faces[face_as_string[2]]])
            list_of_simplices.append([cell[4], cell[5], map_of_faces[face_as_string[1]], map_of_faces[face_as_string[2]]])
            list_of_simplices.append([cell[2], cell[5], map_of_faces[face_as_string[1]], map_of_faces[face_as_string[2]]])
            
            list_of_simplices.append([cell[3], cell[4], cell[5], map_of_faces[face_as_string[2]]])
            list_of_simplices.append([cell[0], cell[1], cell[2], map_of_faces[face_as_string[2]]])
    if normsum>0:
        print('normsum: {}'.format(normsum))
    print('number of errors: {}'.format(number_of_errors))
    print('\tcreated {} simplices'.format(len(list_of_simplices)))
    return list_of_simplices

# write the dgf header into the dgf file
def write_dgf_header(file):
    file.write('DGF\t\t\t\t\t%s %s, generated by starcd2dgf.py on %s \n' %
                ('%', file.name, time.strftime('%Y/%m/%d %H:%M:%S')))
    file.write( '% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n' )
    file.write( '%s %s\n' %( '%', file.name ) )
    file.write( '%s written by starcd2dgf.py on %s\n' %( '%', time.strftime('%Y/%m/%d %H:%M:%S') ) )
    file.write( '% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n' )


# write vertices to dgf file
def write_vertices(vertices,file):
    print('writing vertices to %s...' % (file.name))
    file.write('VERTEX\t\t\t\t\t\t% the vertices of the grid\n')
    if starcd_vrtfile_incorrect == 0:
        vertex_number = 0
        for vertex in vertices:
            file.write('%f\t%f\t%f\t%s vertex %i\n' % ( vertex[0], vertex[1], vertex[2], '%', vertex_number))
            vertex_number += 1
        file.write('#\n')
        print('\t%i vertices written' % (vertex_number))
    else :
        print('error: write_vertices() not implemented for nonconforming .vrt file')
        sys.exit()

# write simplices to dgf file
def write_simplices(simplices, file) :
    print( 'writing simplices to %s...' % (file.name),)
    file.write('SIMPLEX\t\t\t\t\t\t% the simplices of the grid\n')
    if starcd_celfile_incorrect == 0:
        simplex_number = 0
        for simplex in simplices:
            file.write('%i\t%i\t%i\t%i\t\t\t%s simplex %i, consisting of vertices %i, %i, %i and %i\n' %( simplex[ 0 ], simplex[ 1 ], simplex[ 2 ], simplex[ 3 ], '%', simplex_number, simplex[ 0 ], simplex[ 1 ], simplex[ 2 ], simplex[ 3 ] ) )
            simplex_number += 1
        file.write( '#\n' )
        print('\t%i simplices written' %( simplex_number ))
    else :
        print('error: write_simplices() not implemented for nonconforming .cel file')
        sys.exit()

# done with function definitions


def main():
    filename_prefix = sys.argv[ 1 ]
    dgf_filename = '%s.dgf' %( filename_prefix )
    vrtfile_filename = filename_prefix + '.vrt'
    celfile_filename = filename_prefix + '.cel'

    dgf_file = open( dgf_filename, 'w' )

    vertices = read_vertices( vrtfile_filename )
    if starcd_vrtfile_incorrect != 0 :
        print('error: the starcd vrtfile is incorrect')
        sys.exit()

    original_cells = read_cells ( celfile_filename )
    if starcd_celfile_incorrect != 0 :
        print('error: the starcd celfile is incorrect')
        sys.exit()

    simplices = make_simplices( vertices, original_cells )

    write_dgf_header( dgf_file )
    write_vertices( vertices, dgf_file )
    write_simplices( simplices, dgf_file )
    
# run main()
main()
