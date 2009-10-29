import pygame
from Global import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL import GL
from OpenGL import GLU
try:
	import numpy as Numeric
except:
	import Numeric
from OpenGL.GL.ARB.vertex_buffer_object import *
import time
from octree import *
import sys
import math
from skydome import Skydome
vertices = []

g_Octree = COctree()

import random

def load_level(name):
	f = open(name, "r")
	lines = f.readlines()
	f.close()
	level = []
	#x = 0
	#y = 0

	for line in lines:
		pos = line.rsplit(" ")
		if len(pos) < 2:
			continue
		level.append( (float(pos[0]), float(pos[1]), float(pos[2])) )
		Global.vertices.append( (float(pos[0]), float(pos[1]), float(pos[2])) )
		Global.numberOfVertices += 1
		#line2 = []
		#for i in line.rsplit(" "):
		#	line2.append(float(i.replace("\n", "")))
		#	y+=1
		#	Global.vertices.append( (float(x), float(i.replace("\n","")), float(y)) )
		#	Global.numberOfVertices += 1
		#level.append(line2)
		#x+=1
		#y = 0

	return level

class CVert:
	def __init__(self, x = 0.0, y = 0.0, z = 0.0):
		self.x = 0
		self.y = 0
		self.z = 0

CVec = CVert

class CTexCoord:
	""" Texture Coordinate Class """
	def __init__ (self, u = 0.0, v = 0.0):
		self.u = u # // U Component
		self.v = v

class CMesh:
	""" Mesh Data """
	MESH_HEIGHTSCALE = 1.0

	def __init__ (self,position_y):
		self.position_y = position_y
		self.m_nVertexCount = 0								# // Vertex Count

		self.m_pVertices = None # Numeric.array ( (), 'f') 		# // Vertex Data array
		self.m_pVertices_as_string = None						# raw memory string for VertexPointer ()

		self.m_pTexCoords = None # Numeric.array ( (), 'f') 	# // Texture Coordinates array
		self.m_pTexCoords_as_string = None						# raw memory string for TexPointer ()

		self.m_nTextureId = None								# // Texture ID

		# // Vertex Buffer Object Names
		self.m_nVBOVertices = None								# // Vertex VBO Name
		self.m_nVBOTexCoords = None							# // Texture Coordinate VBO Name

	def LoadHeightmap(self, flHeightScale, iLevel, textureWidthRatio, textureHeightRatio):
		""" Heightmap Loader """

		xMax = xMin = iLevel[0][0]
		zMax = zMin = iLevel[0][2]
		for i in iLevel:
			if i[0] < xMin: xMin = i[0]
			elif i[0] > xMax: xMax = i[0]

			if i[2] < zMin: zMin = i[2]
			elif i[2] > zMax: zMax = i[2]

		sizeX = xMax - xMin
		sizeY = zMax - zMin

		self.m_nVertexCount = len(iLevel)
		self.m_pVertices = Numeric.zeros ((self.m_nVertexCount, 3), 'f')	# // Vertex Data
		self.normals = Numeric.zeros ((self.m_nVertexCount, 3), 'f')
		self.m_pTexCoords = Numeric.zeros ((self.m_nVertexCount, 2), 'f')	# // Texture Coordinates

		nIndex = 0
		for i in iLevel:
			self.m_pVertices[nIndex, 0] = i[0] 
			self.m_pVertices[nIndex, 1] = i[1] * flHeightScale + self.position_y
			self.m_pVertices[nIndex, 2] = i[2]
			self.m_pTexCoords[nIndex, 0] = (i[0]-xMin) / sizeX * textureWidthRatio
			self.m_pTexCoords[nIndex, 1] = (i[2]-zMin) / sizeY * textureHeightRatio
			self.normals[nIndex, 0] = random.random()
			self.normals[nIndex, 1] = random.random()
			self.normals[nIndex, 2] = random.random()
			nIndex += 1

		self.m_pVertices_as_string = self.m_pVertices.tostring ()
		self.m_pTexCoords_as_string = self.m_pTexCoords.tostring ()

	def BuildVBOs (self):
		""" // Generate And Bind The Vertex Buffer """
		if (Global.VBOSupported):
			self.m_nVBOVertices = int(glGenBuffersARB( 1))						# // Get A Valid Name
			glBindBufferARB( GL_ARRAY_BUFFER_ARB, self.m_nVBOVertices )	# // Bind The Buffer
			# // Load The Data
			glBufferDataARB( GL_ARRAY_BUFFER_ARB, self.m_pVertices, GL_STATIC_DRAW_ARB )

			# // Generate And Bind The Texture Coordinate Buffer
			self.m_nVBOTexCoords = int(glGenBuffersARB( 1))						# // Get A Valid Name
			glBindBufferARB( GL_ARRAY_BUFFER_ARB, self.m_nVBOTexCoords )		# // Bind The Buffer
			# // Load The Data
			glBufferDataARB( GL_ARRAY_BUFFER_ARB, self.m_pTexCoords, GL_STATIC_DRAW_ARB )

			self.normalsId = glGenBuffersARB(1)
			glBindBufferARB(GL_ARRAY_BUFFER_ARB, self.normalsId)
			glBufferDataARB(GL_ARRAY_BUFFER_ARB, self.normals, GL_STATIC_DRAW_ARB)

			# // Our Copy Of The Data Is No Longer Necessary, It Is Safe In The Graphics Card
			self.m_pVertices = None
			self.m_pTexCoords = None
			self.normals = None
		return

class Player:
	def __init__(self):
		vertices, vnormals, f, self.vertexCount, self.isQuad = loadObj("player.obj")

		self.verticesId = glGenBuffersARB(1)
		self.normalsId = glGenBuffersARB(1)
		glBindBufferARB(GL_ARRAY_BUFFER_ARB, self.verticesId)
		glBufferDataARB(GL_ARRAY_BUFFER_ARB, vertices, GL_STATIC_DRAW_ARB)
		glBindBufferARB(GL_ARRAY_BUFFER_ARB, self.normalsId)
		glBufferDataARB(GL_ARRAY_BUFFER_ARB, vnormals, GL_STATIC_DRAW_ARB)
		glBindBufferARB(GL_ARRAY_BUFFER_ARB, 0)

		self.x = 100
		self.y = 100

	
	def draw(self):

		glPushMatrix()


		#glDisable(GL_COLOR_MATERIAL)

		#glDisable(GL_LIGHTING)
		light = glIsEnabled(GL_LIGHTING)
		if not light:
			glEnable(GL_LIGHTING)

		glColor3f(1.0, 1.0, 0.0)
		
		glTranslatef(self.x, self.y, 0.0)
		glScalef(10, 10, 10)
		#glRotatef(180.0, 0.0, 1.0, 0.0)

		glEnableClientState(GL_VERTEX_ARRAY)
		glEnableClientState(GL_NORMAL_ARRAY)

		glBindBufferARB(GL_ARRAY_BUFFER_ARB, self.verticesId)
		glVertexPointer(3, GL_FLOAT, 0, None)
		glBindBufferARB(GL_ARRAY_BUFFER_ARB, self.normalsId)
		glNormalPointer(GL_FLOAT, 0, None)
		if not self.isQuad:
			glDrawArrays(GL_TRIANGLES, 0, self.vertexCount)
		else:
			glDrawArrays(GL_QUADS, 0, self.vertexCount)
		glBindBufferARB(GL_ARRAY_BUFFER_ARB, 0)

		glDisableClientState(GL_VERTEX_ARRAY)
		glDisableClientState(GL_NORMAL_ARRAY)

		if not light:
			glDisable(GL_LIGHTING)

		glPopMatrix()

class Graphics:
	def __init__(self):
		global g_fVBOObjects

		g_fVBOObjects = []

		self.g_nFrames = 0

	def addSurface(self, Mesh, Map, Texture):
		global g_fVBOObjects
		g_pMesh = CMesh (Mesh)
		#Level = load_level(Map)
		Level = loadRaw(Map)

		g_pMesh.nTextureId, textureWidthRatio, textureHeightRatio = loadTexture(Texture)

		g_pMesh.LoadHeightmap (CMesh.MESH_HEIGHTSCALE, Level, textureWidthRatio, textureHeightRatio)

		if (Global.VBOSupported):
			# // Get Pointers To The GL Functions
			# In python, calling Init for the extension functions will
			# fill in the function pointers (really function objects)
			# so that we call the Extension.

			if (not glInitVertexBufferObjectARB()):
				print "Help!  No GL_ARB_vertex_buffer_object"
				sys.exit(1)
				return False
			# Now we can call to gl*Buffer* ()
			# glGenBuffersARB
			# glBindBufferARB
			# glBufferDataARB
			# glDeleteBuffersARB
			g_pMesh.BuildVBOs()


		g_fVBOObjects.append(g_pMesh)

	def initGL(self):
		Global.VBOSupported = self.IsExtensionSupported("GL_ARB_vertex_buffer_object")
		#if self.IsExtensionSupported("GL_ARB_texture_non_power_of_two") or self.IsExtensionSupported("GL_NV_texture_rectangle") or self.IsExtensionSupported("GL_EXT_texture_rectangle") or self.IsExtensionSupported("GL_ARB_texture_rectangle"):
		if self.IsExtensionSupported("GL_ARB_texture_non_power_of_two"):
			Global.NPOTSupported = True

		glClearColor( 0.0, 0.0, 0.0, 0.0)
		glClearDepth(1.0)
		glDepthFunc(GL_LEQUAL)
		glEnable(GL_DEPTH_TEST)
		glShadeModel(GL_SMOOTH)
		glHint (GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
		glViewport (0, 0, 640, 480)
		glMatrixMode(GL_PROJECTION)

		#glOrtho(0.0, 1.0, 0.0, 1.0, -1.0, 1.0)

		glLoadIdentity()
		gluPerspective( 60.0, 640.0/480.0, 0.1, 5000.0)
		glMatrixMode(GL_MODELVIEW)

		#Lighting
		diffuseMaterial = (0.5, 0.5, 0.0, 1.0)
		mat_specular = (1.0, 1.0, 1.0, 1.0)
		light_position = (150.0, 0.0, 75.0, 1.0)

		glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, diffuseMaterial)
		glMaterialfv(GL_FRONT, GL_DIFFUSE, diffuseMaterial)
		glLightfv(GL_LIGHT1, GL_POSITION, light_position)

		glEnable(GL_LIGHTING)
		glDisable(GL_LIGHT0)
		glEnable(GL_LIGHT1)

		#glColorMaterial(GL_FRONT_AND_BACK, GL_DIFFUSE)
		#glEnable(GL_COLOR_MATERIAL)
		############
		#glEnable(GL_RESCALE_NORMAL)
		glEnable(GL_NORMALIZE)

		self.skydome = Skydome()

		g_Octree.GetSceneDimensions(Global.vertices, Global.numberOfVertices)
		g_Octree.CreateNode(Global.vertices, Global.numberOfVertices, g_Octree.GetCenter(), g_Octree.GetWidth())
		#g_Octree.CreateNode(Global.vertices, Global.numberOfVertices, g_Octree.GetCenter(), 100)

		#Global.g_Debug.AddDebugRectangle(CVector3(-50,50,-50) , 100,100,100)
		#Global.g_Debug.RenderDebugLines()
		self.player = Player()


	def IsExtensionSupported (self, TargetExtension):
		""" Accesses the rendering context to see if it supports an extension.
			Note, that this test only tells you if the OpenGL library supports
			the extension. The PyOpenGL system might not actually support the extension.
		"""
		Extensions = glGetString (GL_EXTENSIONS)
		if (not TargetExtension in Extensions):
			gl_supports_extension = False
			print "OpenGL does not support '%s'" % (TargetExtension)
			return False

		gl_supports_extension = True

		# Now determine if Python supports the extension
		# Exentsion names are in the form GL_<group>_<extension_name>
		# e.g.  GL_EXT_fog_coord
		# Python divides extension into modules
		# g_fVBOSupported = IsExtensionSupported ("GL_ARB_vertex_buffer_object")
		# from OpenGL.GL.EXT.fog_coord import *
		if (TargetExtension [:3] != "GL_"):
			# Doesn't appear to following extension naming convention.
			# Don't have a means to find a module for this exentsion type.
			return False

		# extension name after GL_
		afterGL = TargetExtension [3:]
		try:
			group_name_end = afterGL.index ("_")
		except:
			# Doesn't appear to following extension naming convention.
			# Don't have a means to find a module for this exentsion type.
			return False

		group_name = afterGL [:group_name_end]
		extension_name = afterGL [len (group_name) + 1:]
		extension_module_name = "OpenGL.GL.ARB.%s" % (extension_name)

		import traceback
		try:
			__import__ (extension_module_name)
			print "PyOpenGL supports '%s'" % (TargetExtension)
		except:
			traceback.print_exc()
			print 'Failed to import', extension_module_name
			print "OpenGL rendering context supports '%s'" % (TargetExtension),
			return False

		return True

	def printFPS(self):
		while True:
			pygame.display.set_caption("FarornasGrotta - %d FPS" % (self.g_nFrames))
			self.g_nFrames = 0
			if sys.platform == "win32": break
			time.sleep(1.0)

	def drawAxes(self):
		""" Draws x, y and z axes """
		light = glIsEnabled(GL_LIGHTING)
		if light:
			glDisable(GL_LIGHTING)

		glColor3f(1.0, 0.0, 0.0)
		glBegin(GL_LINES)
		glVertex3f(-1000.0, 0.0, 0.0)
		glVertex3f( 1000.0, 0.0, 0.0)
		glEnd()

		glColor3f(0.0, 1.0, 0.0)
		glBegin(GL_LINES)
		glVertex3f(0.0, -1000.0, 0.0)
		glVertex3f(0.0,  1000.0, 0.0)
		glEnd()

		glColor3f(0.0, 0.0, 1.0)
		glBegin(GL_LINES)
		glVertex3f(0.0, 0.0, -1000.0)
		glVertex3f(0.0, 0.0, 1000.0)
		glEnd()

		if light:
			glEnable(GL_LIGHTING)


	def draw(self, objects):
		global g_fVBOObjects

		glClearColor(0.4, 0.4, 0.4, 0.0)

		glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

		if Global.wireframe:
			glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
		else:
			glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)


		#light_position = (150.0, 0.0, 75.0, 1.0)
		#glLightfv(GL_LIGHT0, GL_POSITION, light_position)


		glLoadIdentity()
		glRotatef(Global.Input.xrot, 1.0, 0.0, 0.0)
		glRotatef(Global.Input.yrot, 0.0, 1.0, 0.0)
		glTranslated(-Global.Input.xpos, -Global.Input.ypos,-Global.Input.zpos)
		#print -Global.Input.xpos, -Global.Input.ypos, -Global.Input.zpos

		self.g_nFrames += 1

		if Global.drawAxes:
			self.drawAxes()

		glColor3f(1.0, 1.0, 1.0)

		#glClearColor(0.0, 0.0, 0.6, 0.5)
		glFogi(GL_FOG_MODE, GL_LINEAR)
		glFogfv(GL_FOG_COLOR, (0.4, 0.4, 0.4, 0.0))
		glFogf(GL_FOG_DENSITY, 0.1)
		glHint(GL_FOG_HINT, GL_DONT_CARE)
		glFogf(GL_FOG_START, 1.0)
		glFogf(GL_FOG_END, 110.0)
		#glEnable(GL_FOG)

		# SkyDome
		self.skydome.draw()

		# // Enable Pointers
		glEnableClientState( GL_VERTEX_ARRAY )						# // Enable Vertex Arrays
		#glEnableClientState( GL_TEXTURE_COORD_ARRAY )				# // Enable Texture Coord Arrays
	

		glPushMatrix()
		glColor3f(1.0, 1.0, 1.0)
		#glScalef(10.0, 10.0, 10.0)

		for i in xrange(len(g_fVBOObjects)):
			#glEnable(GL_BLEND)
			#glBlendFunc(GL_ONE, GL_ONE)
			glBindTexture(GL_TEXTURE_2D, g_fVBOObjects[i].nTextureId)
			#glEnable(GL_TEXTURE_2D)


			glBindBufferARB( GL_ARRAY_BUFFER_ARB, g_fVBOObjects[i].m_nVBOVertices )
			glVertexPointer(3, GL_FLOAT, 0, None)
			#glBindBufferARB(GL_ARRAY_BUFFER_ARB, g_fVBOObjects[i].m_nVBOTexCoords)
			#glTexCoordPointer(2, GL_FLOAT, 0, None)
			glBindBufferARB(GL_ARRAY_BUFFER_ARB, g_fVBOObjects[i].normalsId)
			glNormalPointer(GL_FLOAT, 0, None)

			glDrawArrays( GL_TRIANGLES, 0, g_fVBOObjects[i].m_nVertexCount )
			glBindBufferARB(GL_ARRAY_BUFFER_ARB, 0)

			#glDisable(GL_TEXTURE_2D)
			#glDisable(GL_BLEND)

		glPopMatrix()


		# // Disable Pointers
		glDisableClientState( GL_VERTEX_ARRAY )					# // Disable Vertex Arrays
		#glDisableClientState( GL_TEXTURE_COORD_ARRAY )			# // Disable Texture Coord Arrays

		glDisable(GL_FOG)

		self.player.draw()

		g_Octree.DrawOctree(g_Octree)
		if Global.debugLines:
			Global.g_Debug.RenderDebugLines()


		s = 100.0
		x = objects[0].position[0]
		y = objects[0].position[1]
		z = objects[0].position[2]
		verts = [
				x+s,y+s,z-s, x-s,y+s,z-s, x-s,y+s,z+s, x+s,y+s,z+s, #top
				x+s,y-s,z+s, x-s,y-s,z+s, x-s,y-s,z-s, x+s,y-s,z-s, #bottom
				x+s,y+s,z+s, x-s,y+s,z+s, x-s,y-s,z+s, x+s,y-s,z+s, #front
				x+s,y-s,z-s, x-s,y-s,z-s, x-s,y+s,z-s, x+s,y+s,z-s, #back
				x-s,y+s,z+s, x-s,y+s,z-s, x-s,y-s,z-s, x-s,y-s,z+s, #left
				x+s,y+s,z-s, x+s,y+s,z+s, x+s,y-s,z+s, x+s,y-s,z-s  #right
				]
		colors = [
				0.0,1.0,0.0, 0.0,1.0,0.0, 0.0,1.0,0.0, 0.0,1.0,0.0, #top
				1.0,0.5,0.0, 1.0,0.5,0.0, 1.0,0.5,0.0, 1.0,0.5,0.0, #bottom
				1.0,0.0,0.0, 1.0,0.0,0.0, 1.0,0.0,0.0, 1.0,0.0,0.0, #front
				1.0,1.0,0.0, 1.0,1.0,0.0, 1.0,1.0,0.0, 1.0,1.0,0.0, #back
				0.0,0.0,1.0, 0.0,0.0,1.0, 0.0,0.0,1.0, 0.0,0.0,1.0, #left
				1.0,0.0,1.0, 1.0,0.0,1.0, 1.0,0.0,1.0, 1.0,0.0,1.0  #right
				]
		normals = [
				0.0,1.0,0.0, 0.0,1.0,0.0, 0.0,1.0,0.0, 0.0,1.0,0.0, 	#top
				0.0,-1.0,0.0, 0.0,-1.0,0.0, 0.0,-1.0,0.0, 0.0,-1.0,0.0, #bottom
				0.0,0.0,1.0, 0.0,0.0,1.0, 0.0,0.0,1.0, 0.0,0.0,1.0,		#front
				0.0,0.0,-1.0, 0.0,0.0,-1.0, 0.0,0.0,-1.0, 0.0,0.0,-1.0,	#back
				-1.0,0.0,0.0, -1.0,0.0,0.0, -1.0,0.0,0.0, -1.0,0.0,0.0, #left
				1.0,0.0,0.0, 1.0,0.0,0.0, 1.0,0.0,0.0, 1.0,0.0,0.0, 	#right
				]

		glEnableClientState(GL_VERTEX_ARRAY)
		glEnableClientState(GL_COLOR_ARRAY)
		glEnableClientState(GL_NORMAL_ARRAY)
		glVertexPointer(3, GL_FLOAT, 0, verts)
		glColorPointer(3, GL_FLOAT, 0, colors)
		glNormalPointer(GL_FLOAT, 0, normals)
		glDrawArrays(GL_QUADS, 0, 24)
		glDisableClientState(GL_VERTEX_ARRAY)
		glDisableClientState(GL_COLOR_ARRAY)
		glDisableClientState(GL_NORMAL_ARRAY)

		i = 0
		while i < len(normals):
			glBegin(GL_LINES)
			glVertex3f(normals[i], normals[i+1], normals[i+2])
			glVertex3f(normals[i]*200, normals[i+1]*200, normals[i+2]*200)
			glEnd()
			i += 3
		
		glFlush()

		pygame.display.flip()

		err = glGetError()
		if err:
			print "OpenGL Error:",err,"(",gluErrorString(err),")"
