#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
gridhelper.py (c) 2009 rene.milk@uni-muenster.de

It is licensed to you under the terms of the WTFPLv2 (see below).

This program is free software. It comes with no warranty,
to the extent permitted by applicable law.


            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
                    Version 2, December 2004

 Copyright (C) 2004 Sam Hocevar
  14 rue de Plaisance, 75014 Paris, France
 Everyone is permitted to copy and distribute verbatim or modified
 copies of this license document, and changing it is allowed as long
 as the name is changed.

            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

  0. You just DO WHAT THE FUCK YOU WANT TO.
"""

import mesh,sys,time

filename = sys.argv[1]

mesh = mesh.Mesh( 3 )
dd = filename.find('phantom') != -1
print dd
mesh.parseSMESH( filename, dd )
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *


# Some api in the chain is translating the keystrokes to this octal string
# so instead of saying: ESCAPE = 27, we use the following.
ESCAPE = '\033'

win_x = 500
win_y = 500
x_arc =0
y_arc =0

#float eye[3] = { 0.0f,0.0f,15.f};
#float up[3] = { 0.0f,1.0f,0.f};
mouse_y = 0
mouse_x = 0
zoom = -20.
count = 0
draw_bounding_box = draw_octree = False
draw_mesh = True
# A general OpenGL initialization function.  Sets all of the initial parameters.
def InitGL(Width, Height):				# We call this right after our OpenGL window is created.
	global mesh
	glClearColor(0.0, 0.0, 0.0, 1.0)	# This Will Clear The Background Color To Black
	glClearDepth(1.0)					# Enables Clearing Of The Depth Buffer
	glDepthFunc(GL_LESS)				# The Type Of Depth Test To Do
	glEnable(GL_DEPTH_TEST)				# Enables Depth Testing
	glShadeModel(GL_SMOOTH)				# Enables Smooth Color Shading
	
	glEnable(GL_NORMALIZE)
	light_position = ( 0., 0., 1., 0. )
	white_light = ( 1., 1., 1., 0.01 )
	d_light = ( 1., 1., 1., 0.1 )
	red_light = ( 1., 0., 0., 0.7 )
	glLightfv(GL_LIGHT0, GL_POSITION, light_position)
	glLightfv(GL_LIGHT1, GL_POSITION, light_position)
	glLightfv(GL_LIGHT0, GL_AMBIENT, white_light)
	#glLightfv(GL_LIGHT1, GL_AMBIENT, ( 1., 1., 1., 0.8 ) )
	glLightfv(GL_LIGHT1, GL_SPECULAR, red_light)
	glLightfv(GL_LIGHT0, GL_DIFFUSE, d_light)

	glEnable(GL_LIGHTING)
	glEnable(GL_LIGHT0)
	#glEnable(GL_LIGHT1)

	glEnable(GL_BLEND)
	glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
	#glBlendFunc(GL_SRC_ALPHA,GL_ONE)
	glColorMaterial ( GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE  )
	#glEnable(GL_COLOR_MATERIAL)
	glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
    
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()					# Reset The Projection Matrix
										# Calculate The Aspect Ratio Of The Window
	gluPerspective(45.0, float(Width)/float(Height), 0.1, 1000000.0)

	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()
	mesh.prepDraw()
	#glEnable(GL_CULL_FACE)

# The function called when our window is resized (which shouldn't happen if you enable fullscreen, below)
def ReSizeGLScene(Width, Height):
	if Height == 0:						# Prevent A Divide By Zero If The Window Is Too Small
		Height = 1

	glViewport(0, 0, Width, Height)		# Reset The Current Viewport And Perspective Transformation
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	gluPerspective(45.0, float(Width)/float(Height), 0.1, 1000000.0)
	glMatrixMode(GL_MODELVIEW)

def DrawGLScene():
	global mesh, zoom, draw_bounding_box, draw_octree, draw_mesh,count
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)	# Clear The Screen And The Depth Buffer
	glLoadIdentity()					# Reset The View

	glTranslatef(0,0.0,zoom)
	glRotatef(x_arc,0,1,0);
	glRotatef(y_arc,1,0,0);

	center = -mesh.bounding_box.center
	glTranslatef(center.x,center.y,center.z)

	#if draw_mesh:
		#mesh.draw(1.0)
	#if draw_bounding_box:
		#mesh.bounding_box.draw()
	#if draw_octree:
		#mesh.quad.draw()
	mesh.drawAdjacentFaces( count )
	count += 1
	if count == len(mesh.faces):
		count = 0
	time.sleep(0.3)
	glutSwapBuffers()


# The function called whenever a key is pressed. Note the use of Python tuples to pass in: (key, x, y)
def keyPressed(*args):
	global mesh, zoom, draw_bounding_box, draw_octree, draw_mesh
	# If escape is pressed, kill everything.
	if args[0] == ESCAPE:
		sys.exit()
	if args[0] == 's':
		mesh.smooth(0.3)
	if args[0] == 'n':
		mesh.noise(0.1)
	if args[0] == '+':
		zoom += 5
	if args[0] == '-':
		zoom -= 5
	if args[0] == 'b':
		draw_bounding_box = not draw_bounding_box
	if args[0] == 'o':
		draw_octree = not draw_octree
	if args[0] == 'm':
		draw_mesh = not draw_mesh
	if args[0] == 'c':
		glEnable(GL_COLOR_MATERIAL)
		
def mouseMotion(x,y):
	global mouse_x,	mouse_y,x_arc,y_arc 
	sensitivity = 0.2
	x_arc -= sensitivity*(mouse_x-x);
	y_arc += sensitivity*(mouse_y-y);
	mouse_x = x;
	mouse_y = y;

def processMouse( wheel, direction,x,y):
	global zoom
	zoom += direction * 5

def main():
	global window
	glutInit(sys.argv)

	glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
	glutInitWindowSize(640, 480)
	glutInitWindowPosition(0, 0)
	window = glutCreateWindow("")
	glutDisplayFunc(DrawGLScene)
	glutIdleFunc(DrawGLScene)
	glutReshapeFunc(ReSizeGLScene)
	glutKeyboardFunc(keyPressed)
	glutMotionFunc(mouseMotion)
	glutMouseWheelFunc(processMouse)

	InitGL(640, 480)
	glutMainLoop()

if __name__ == "__main__":
	main()