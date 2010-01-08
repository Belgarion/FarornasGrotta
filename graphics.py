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
from player import Player

import random

from water import Water

def nearestPowerOfTwo(v):
	v -= 1
	v |= v >> 1
	v |= v >> 2
	v |= v >> 4
	v |= v >> 8
	v |= v >> 16
	v += 1
	return v
class CVert:
	def __init__(self, x = 0.0, y = 0.0, z = 0.0):
		self.x = 0
		self.y = 0
		self.z = 0
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

		xMax = xMin = iLevel[0].x
		zMax = zMin = iLevel[0].z
		for i in iLevel:
			if i.x < xMin: xMin = i.x
			elif i.x > xMax: xMax = i.x

			if i.z < zMin: zMin = i.z
			elif i.z > zMax: zMax = i.z

		sizeX = xMax - xMin
		sizeY = zMax - zMin

		self.m_nVertexCount = len(iLevel)
		
		self.m_pVertices = Numeric.zeros ((self.m_nVertexCount, 3), 'f')	# // Vertex Data
		self.normals = Numeric.zeros ((self.m_nVertexCount, 3), 'f')
		self.m_pTexCoords = Numeric.zeros ((self.m_nVertexCount, 2), 'f')	# // Texture Coordinates

		nIndex = 0
		for i in iLevel:
			self.m_pVertices[nIndex, 0] = i.x 
			self.m_pVertices[nIndex, 1] = i.y * flHeightScale + self.position_y
			self.m_pVertices[nIndex, 2] = i.z
			self.m_pTexCoords[nTIndex, 0] = (i.x-xMin) / sizeX * textureWidthRatio
			self.m_pTexCoords[nTIndex, 1] = (i.z-zMin) / sizeY * textureHeightRatio
			nIndex += 1

		self.m_pVertices_as_string = self.m_pVertices.tostring ()
		self.m_pTexCoords_as_string = self.m_pTexCoords.tostring ()

	def BuildVBOs (self):
		""" Generate And Bind The Vertex Buffer """
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
class Graphics:
	def __init__(self):
		global g_fVBOObjects

		g_fVBOObjects = []
		self.g_nFrames = 0

		self.g_Octree = COctree()
	def addSurface(self, Mesh, Map, Texture):
		g_pMesh = CMesh (Mesh)
		vertices, vnormals, f, self.vertexCount = loadObj("terrain.obj")

		g_pMesh.textureId, textureWidthRatio, textureHeightRatio = loadTexture(Texture)

		xMax = xMin = vertices[0][0]
		zMax = zMin = vertices[0][2]
		for i in vertices:
			if i[0] < xMin: xMin = i[0]
			elif i[0] > xMax: xMax = i[0]

			if i[2] < zMin: zMin = i[2]
			elif i[2] > zMax: zMax = i[2]

		sizeX = xMax - xMin
		sizeY = zMax - zMin

		texCoords = Numeric.zeros ((self.vertexCount, 2), 'f')

		nIndex = 0
		for i in vertices:
			Global.vertices.append( CVector3(i[0], i[1], i[2]) )
			Global.numberOfVertices += 1
			Global.g_NumberOfVerts += 1
			texCoords[nIndex, 0] = (i[0]-xMin) / sizeX * textureWidthRatio
			texCoords[nIndex, 1] = (i[2]-zMin) / sizeY * textureHeightRatio
			nIndex += 1


		self.verticesId = glGenBuffersARB(1)
		self.vnormalsId = glGenBuffersARB(1)
		self.texCoordsId = glGenBuffersARB(1)
		glBindBufferARB(GL_ARRAY_BUFFER_ARB, self.verticesId)
		glBufferDataARB(GL_ARRAY_BUFFER_ARB, vertices, GL_STATIC_DRAW_ARB)
		glBindBufferARB(GL_ARRAY_BUFFER_ARB, self.vnormalsId)
		glBufferDataARB(GL_ARRAY_BUFFER_ARB, vnormals, GL_STATIC_DRAW_ARB)
		glBindBufferARB(GL_ARRAY_BUFFER_ARB, self.texCoordsId)
		glBufferDataARB(GL_ARRAY_BUFFER_ARB, texCoords, GL_STATIC_DRAW_ARB)
		glBindBufferARB(GL_ARRAY_BUFFER_ARB, 0)

		g_pMesh.verticesId = self.verticesId
		g_pMesh.vnormalsId = self.vnormalsId
		g_pMesh.texCoordsId = self.texCoordsId
		g_pMesh.vertexCount = self.vertexCount

		g_fVBOObjects.append(g_pMesh)
	def initGL(self):
		Global.VBOSupported = self.IsExtensionSupported("GL_ARB_vertex_buffer_object")
		if not glInitVertexBufferObjectARB():
			sys.stderr.write("ERROR: Vertex buffer objects is not supported\n")
			Global.quit = 1
			return

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
		###########

		glEnable(GL_NORMALIZE)

		self.skydome = Skydome()
		
		if not Global.disableWater:
			self.water = Water()

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
			print "Failed to import", extension_module_name
			print "OpenGL rendering context supports '%s'" % (TargetExtension),
			return False

		return True
	def printFPS(self):
		while True:
			pygame.display.set_caption("FarornasGrotta - %d FPS" % (self.g_nFrames))
			#print self.g_nFrames
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

		if Global.reDraw:
			Global.g_EndNodeCount = 0
			Global.g_Debug.Clear()
			self.g_Octree.DestroyOctree()
			self.g_Octree.GetSceneDimensions(Global.vertices, Global.g_NumberOfVerts)
			self.g_Octree.CreateNode(Global.vertices, Global.g_NumberOfVerts, self.g_Octree.GetCenter(), self.g_Octree.GetWidth())
			Global.reDraw = False


		glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT ) 
		glLoadIdentity()

		if Global.drawAxes:
			self.drawAxes()

		glClearColor(0.4, 0.4, 0.4, 0.0)

		if Global.wireframe:
			glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
		else:
			glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)


		glLoadIdentity()

		glRotatef(Global.Input.xrot, 1.0, 0.0, 0.0)
		glRotatef(Global.Input.yrot, 0.0, 1.0, 0.0)

		# SkyDome
		self.skydome.draw()

		if Global.spectator:
			glTranslated(-Global.Input.xpos, -Global.Input.ypos,-Global.Input.zpos)
		else:
			glTranslated(
					-Global.player.position[0]-0.2*math.sin(math.radians(Global.player.orientation[1])),
					-Global.player.position[1]-2.2,
					-Global.player.position[2]+0.2*math.cos(math.radians(Global.player.orientation[1]-180))
					)

		self.g_nFrames += 1

		if Global.drawAxes:
			self.drawAxes()

		# Water
		if not Global.disableWater:
			self.water.draw()

		glColor3f(1.0, 1.0, 1.0)

		#glClearColor(0.0, 0.0, 0.6, 0.5)
		glFogi(GL_FOG_MODE, GL_LINEAR)
		glFogfv(GL_FOG_COLOR, (0.4, 0.4, 0.4, 0.0))
		glFogf(GL_FOG_DENSITY, 0.1)
		glHint(GL_FOG_HINT, GL_DONT_CARE)
		glFogf(GL_FOG_START, 1.0)
		glFogf(GL_FOG_END, 110.0)
		#glEnable(GL_FOG)

		# // Enable Pointers
		glEnableClientState( GL_VERTEX_ARRAY )						# // Enable Vertex Arrays
		glEnableClientState( GL_TEXTURE_COORD_ARRAY )				# // Enable Texture Coord Arrays
		glEnableClientState(GL_NORMAL_ARRAY)
	

		glPushMatrix()
		glColor3f(1.0, 1.0, 1.0)
		#glScalef(10.0, 10.0, 10.0)

		for i in xrange(len(g_fVBOObjects)):
			#glEnable(GL_BLEND)
			#glBlendFunc(GL_ONE, GL_ONE)
			glBindTexture(GL_TEXTURE_2D, g_fVBOObjects[i].textureId)
			glEnable(GL_TEXTURE_2D)


			glBindBufferARB( GL_ARRAY_BUFFER_ARB, g_fVBOObjects[i].verticesId )
			glVertexPointer(3, GL_FLOAT, 0, None)
			glBindBufferARB(GL_ARRAY_BUFFER_ARB, g_fVBOObjects[i].texCoordsId)
			glTexCoordPointer(2, GL_FLOAT, 0, None)
			glBindBufferARB(GL_ARRAY_BUFFER_ARB, g_fVBOObjects[i].vnormalsId)
			glNormalPointer(GL_FLOAT, 0, None)

			glDrawArrays(GL_TRIANGLES, 0, g_fVBOObjects[i].vertexCount)
			glBindBufferARB(GL_ARRAY_BUFFER_ARB, 0)

			glDisable(GL_TEXTURE_2D)
			#glDisable(GL_BLEND)

		glPopMatrix()


		# // Disable Pointers
		glDisableClientState( GL_VERTEX_ARRAY )					# // Disable Vertex Arrays
		glDisableClientState( GL_TEXTURE_COORD_ARRAY )			# // Disable Texture Coord Arrays
		glDisableClientState(GL_NORMAL_ARRAY)

		glDisable(GL_FOG)

		if Global.debugLines:
			Global.g_Debug.RenderDebugLines()

		if Global.g_MaxSubdivisions:
			# Here we draw the octree, starting with the root node and recursing down each node.
			# When we get to each of the end nodes we will draw the vertices assigned to them.
			self.g_Octree.DrawOctree(self.g_Octree)
			
			if Global.g_bDebugLines:
				# Render the cube'd nodes to visualize the octree (in wire frame mode)
				Global.g_Debug.RenderDebugLines()

		for obj in objects:
			obj.draw()

		glFlush()

		pygame.display.flip()

		err = glGetError()
		if err:
			print "OpenGL Error:",err,"(",gluErrorString(err),")"
