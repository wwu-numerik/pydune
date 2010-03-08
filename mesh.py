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
from gridhelper import *
from euclid import *
import random
from OpenGL.GL import *
from OpenGL.GLUT import *

def skipCommentsAndEmptyLines(fd):
	while fd:
		line = fd.readline()
		#if line.startswith( '#' ) or len(line) < 3:
		if line.startswith( '#' ):
			continue
		else:
			break
	return fd

def isAdjacentFace(fs,fa):
	for e in fs.edge_idx:
		e_ = ( e[1], e[0] )
		if e in fa.edge_idx or e_ in fa.edge_idx:
			return True
	return False

class Mesh():

	def __init__(self,dim):
		self.dim = dim
		self.vertices = PLCPointList(dim)
		self.faces = []
		self.edges = []
		self.draw_outline = True
		self.draw_faces = True
		self.outline_color = ( 1,1,1 )
		self.adj_points = dict()

	def parseSMESH(self, filename,zero_based_idx):
		vert_fn_ = filename + '.vertices'
		face_fn_ = filename + '.faces'
		verts = open(vert_fn_, 'w')
		faces = open(face_fn_, 'w')
		fd = open( filename, 'r' )
		#if not zero_based_idx:
		fd = skipCommentsAndEmptyLines( fd )
		print fd.readline()
		while fd:
			line = fd.readline()
			if line.startswith( '#' ):
				continue
			if len(line.split()) < self.dim + 1:
				break
			verts.write(line)
		print 'vertice writing complete'
		#if zero_based_idx:
		fd = skipCommentsAndEmptyLines( fd )
		print fd.readline()
		while fd:
			line = fd.readline()
			if line.startswith( '#' ):
				continue
			if len(line.split()) < self.dim + 2:
				break
			faces.write(line)
		print 'face writing complete'
		verts.close()
		faces.close()
		self.parseSMESH_vertices(vert_fn_)
		print 'vert parsing complete'
		self.parseSMESH_faces(face_fn_, zero_based_idx)
		print 'face parsing complete'

	def parseSMESH_vertices(self,filename):
		fn = open( filename, 'r' )
		for line in fn.readlines():
			line = line.split()
			#this way I can use vector for either dim
			line.append(None)
			v = vector( line[1], line[2], line[3] )
			self.vertices.appendVert( v )
		print 'read %d vertices'%len(self.vertices)
		fn.close()

	def parseSMESH_faces(self,filename,zero_based_idx):
		fn = open( filename, 'r' )
		for line in fn.readlines():
			line = line.split()
			#this way I can use vector for either dim
			line.append(None)
			if zero_based_idx:
				v0 = int(line[1]) + 1
				v1 = int(line[2]) + 1
				v2 = int(line[3]) + 1
			else:
				v0 = int(line[1])
				v1 = int(line[2])
				v2 = int(line[3])
			s = simplex(self.vertices, v0,v1,v2 )
			if self.adj_points.has_key(v0) :
				self.adj_points[v0] += [ v1, v2 ] 
			else:
				self.adj_points[v0] = [ v1, v2 ]
			self.faces.append( s )
		print 'read %d faces'%len(self.faces)
		fn.close()

	def buildAdjacencyList(self):
		self.adj = dict()
		i_s = 0
		for fs in self.faces:
			self.adj[i_s] = []
			ia = 0
			for fa in self.faces:
				if isAdjacentFace(fs,fa) and not ia == i_s:
					self.adj[i_s].append(ia)
				ia += 1
			i_s += 1
			
	def drawFace(self, f,opacity=1.):
		glBegin(GL_POLYGON)					# Start Drawing The Pyramid
		n = f.n
		glNormal3f(n.x,n.y,n.z)
		for v in f.v:
			glColor4f(1.0,0,0,opacity)
			glVertex3f(v.x, v.y, v.z )
		glEnd()

	def drawOutline(self,f,opacity=1):
		glLineWidth(5)
		glBegin(GL_LINE_STRIP)
		n = f.n
		glNormal3f(n.x,n.y,n.z)
		for v in f.v:
			c = self.outline_color
			glColor4f(c[0],c[1],c[2],opacity)
			glVertex3f(v.x, v.y, v.z )
		glEnd()
				
	def drawAdjacentFaces( self, face_idx ):
		for f_idx in self.adj[face_idx]:
			self.drawOutline( self.faces[f_idx] )
			#self.drawFace( self.faces[f_idx], 0.5 )
		self.drawFace( self.faces[f_idx], 1.0 )
		self.drawOutline( self.faces[f_idx] )

	def draw(self, opacity=1.):
		glCallList(1)

	def laplacianDisplacement(self,N_1_p,p):
		n = len( N_1_p )
		s = Vector3()
		if n > 0:
			for j in N_1_p:
				s += self.vertices.verts[j] - p
			s /= float(n)
		return s

	def scale(self,factor):
		for i,v in self.vertices.verts.iteritems():
			self.vertices.verts[i] *= factor
		self.prepDraw()

	def smooth(self,step):
		n = 0
		avg = 0.0
		for i,v in self.vertices.verts.iteritems():
			if self.adj_points.has_key(i):
				p_old = self.vertices.verts[i]
				p_new = self.vertices.verts[i] + step * self.laplacianDisplacement( self.adj_points[i], self.vertices.verts[i] )
				self.vertices.verts[i] = p_new
				avg = ( abs(p_old)/abs(p_new) + n * avg ) / float( n + 1 )
				n += 1
		self.scale( avg )
		self.prepDraw()

	def noise(self,factor):
		for i,v in self.vertices.verts.iteritems():
			#self.vertices.verts[i] += random.gauss( factor, 1 ) * self.vertices.verts[i]
			self.vertices.verts[i] += random.random( ) * factor * self.vertices.verts[i]
		self.prepDraw()

	def prepDraw(self,opacity=1.):
		for f in self.faces:
			f.reset(self.vertices)
		self.main_dl = glGenLists(2)
		self. bounding_box = BoundingVolume( self )
		glNewList(1,GL_COMPILE)
		i = 0
		if self.draw_faces:
			glBegin(GL_TRIANGLES)					# Start Drawing The Pyramid
			for f in self.faces:
				#glBegin(GL_POLYGON)					# Start Drawing The Pyramid
				n = f.n
				if i % 2 == 0:
					n *= -1
				glNormal3f(n.x,n.y,n.z)
				for v in f.v:
					glColor4f(1.0,0,0,opacity)
					glVertex3f(v.x, v.y, v.z )
				i += 1
			glEnd()

		#if self.draw_outline:
			#for f in self.faces:
				#self.drawOutline(f)
		glEndList()

class BoundingVolume:
	def __init__(s,mesh):
		s.outline_color = ( 1,1,1 )
		vertices = mesh.vertices.verts.values()
		minV = Vector3()
		maxV = Vector3()
		vertices.sort( lambda x, y: cmp(y.x, x.x ) )
		minV.x = vertices[0].x
		maxV.x = vertices[-1].x
		vertices.sort( lambda x, y: cmp(y.y, x.y ) )
		minV.y = vertices[0].y
		maxV.y = vertices[-1].y
		vertices.sort( lambda x, y: cmp(y.z, x.z ) )
		minV.z = vertices[0].z
		maxV.z = vertices[-1].z

		s.points = []
		for i in range(8):
			s.points.append(Vector3())
		for i in range(2):
			for j in range(2):
				s.points[int('%d%d%d'%(0,i,j),2)].x = minV.x
				s.points[int('%d%d%d'%(1,i,j),2)].x = maxV.x
				s.points[int('%d%d%d'%(i,0,j),2)].y = minV.y
				s.points[int('%d%d%d'%(i,1,j),2)].y = maxV.y
				s.points[int('%d%d%d'%(i,j,0),2)].z = minV.z
				s.points[int('%d%d%d'%(i,j,1),2)].z = maxV.z

		s.center = Vector3()
		for p in s.points:
			s.center += p
		s.center /= float(8)
		glNewList(2,GL_COMPILE)
		glLineWidth(5)
		glBegin(GL_LINE_STRIP)
		for v in s.points:
			c = s.outline_color
			glColor3f(c[0],c[1],c[2])
			glVertex3f(v.x, v.y, v.z )
		glEnd()
		glEndList()

	def drawFrame(s):
		glCallList(2)
		
		
	def draw(s):
		s.drawFrame()
		glPushMatrix(  )
		glTranslatef(s.center.x,s.center.y,s.center.z)
		glutSolidSphere( GLdouble(0.25), GLint(10), GLint(10) )
		glPopMatrix(  )
		
		