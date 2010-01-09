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

import random

from water import Water

def loadObj(filename):
	f = open(filename, "r")
	lines = f.readlines()
	f.close()

	v = []
	vn = []
	facesv = []
	facest = []
	facesn = []
	for line in lines:
		pos = line.rsplit(" ")
		if len(pos) < 4:
			continue

		if pos[0] == "v":
			v.append( (float(pos[1]), float(pos[2]), float(pos[3])) )
		elif pos[0] == "vn":
			vn.append( (float(pos[1]), float(pos[2]), float(pos[3])) )
		elif pos[0] == "f":
			quad = False
			a = pos[1].rsplit("/")
			b = pos[2].rsplit("/")
			c = pos[3].rsplit("/")
			d = None
			if len(pos) > 4:
				d = pos[4].rsplit("/")
				quad = True

			facesv.append( (int(a[0])-1, int(b[0])-1, int(c[0])-1) )
			if quad:
				facesv.append( (int(a[0])-1, int(c[0])-1, int(d[0])-1) )

			if a[1] != '':
				facest.append( (int(a[1])-1, int(b[1])-1, int(c[1])-1 ) )
				if quad:
					facest.append( (int(a[1])-1, int(c[1])-1, int(d[1])-1 ) )
			else:
				facest.append( (0, 0, 0) )
				if quad:
					facest.append( (0, 0, 0) )

			if a[2] != '':
				facesn.append( (int(a[2])-1, int(b[2])-1, int(c[2])-1) )
				if quad:
					facesn.append( (int(a[2])-1, int(c[2])-1, int(d[2])-1) )
			else:
				facesn.append( (0, 0, 0) )
				if quad:
					facesn.append( (0, 0, 0) )

	vertices = Numeric.zeros((len(facesv)*3, 3), 'f')
	vnormals = Numeric.zeros((len(facesn)*3, 3), 'f')
	#texCoords = Numeric.zeros((len(facest*3), 2), 'f')
	vertexCount = len(facesv)*3
	quad = False
	
	nIndex = 0
	for i in facesv:
		vertices[nIndex, 0] = v[i[0]][0]
		vertices[nIndex, 1] = v[i[0]][1]
		vertices[nIndex, 2] = v[i[0]][2]
		vertices[nIndex + 1, 0] = v[i[1]][0]
		vertices[nIndex + 1, 1] = v[i[1]][1]
		vertices[nIndex + 1, 2] = v[i[1]][2]
		vertices[nIndex + 2, 0] = v[i[2]][0]
		vertices[nIndex + 2, 1] = v[i[2]][1]
		vertices[nIndex + 2, 2] = v[i[2]][2]
		nIndex += 3

	nIndex = 0
	for i in facesn:
		vnormals[nIndex, 0] = vn[i[0]][0]
		vnormals[nIndex, 1] = vn[i[0]][1]
		vnormals[nIndex, 2] = vn[i[0]][2]
		vnormals[nIndex + 1, 0] = vn[i[1]][0]
		vnormals[nIndex + 1, 1] = vn[i[1]][1]
		vnormals[nIndex + 1, 2] = vn[i[1]][2]
		vnormals[nIndex + 2, 0] = vn[i[2]][0]
		vnormals[nIndex + 2, 1] = vn[i[2]][1]
		vnormals[nIndex + 2, 2] = vn[i[2]][2]
		nIndex += 3

	return (vertices, vnormals, (facesv, facest, facesn), vertexCount)
class CVector3:
	def __init__(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z
	def __add__(self, v):
		return CVector3(self.x + v.x, self.y + v.y, self.z + v.z)
	def __sub__(self, v):
		return CVector3(self.x - v.x, self.y - v.y, self.z - v.z)
	def __mul__(self, num):
		return CVector3(self.x * num, self.y * num, self.z * num)
	def __div__(self, num):
		return CVector3(self.x / num, self.y / num, self.z / num)
def nearestPowerOfTwo(v):
	v -= 1
	v |= v >> 1
	v |= v >> 2
	v |= v >> 4
	v |= v >> 8
	v |= v >> 16
	v += 1
	return v
def createVBO(vertices, vnormals, texCoords = None):
	verticesId = glGenBuffersARB(1)
	normalsId = glGenBuffersARB(1)

	glBindBufferARB(GL_ARRAY_BUFFER_ARB, verticesId)
	glBufferDataARB(GL_ARRAY_BUFFER_ARB, vertices, GL_STATIC_DRAW_ARB)

	glBindBufferARB(GL_ARRAY_BUFFER_ARB, normalsId)
	glBufferDataARB(GL_ARRAY_BUFFER_ARB, vnormals, GL_STATIC_DRAW_ARB)

	if texCoords != None:
		texCoordsId = glGenBuffersARB(1)

		glBindBufferARB(GL_ARRAY_BUFFER_ARB, texCoordsId)
		glBufferDataARB(GL_ARRAY_BUFFER_ARB, texCoords, GL_STATIC_DRAW_ARB)

	glBindBufferARB(GL_ARRAY_BUFFER_ARB, 0)

	if texCoords != None:
		return verticesId, normalsId, texCoordsId
	return verticesId, normalsId
def drawVBO(verticesId, normalsId, vertexCount, texCoordsId = None):
	glEnableClientState(GL_VERTEX_ARRAY)

	if normalsId != None:
		glEnableClientState(GL_NORMAL_ARRAY)

	if texCoordsId != None:
		glEnableClientState(GL_TEXTURE_COORD_ARRAY)

	glBindBufferARB(GL_ARRAY_BUFFER_ARB, verticesId)
	glVertexPointer(3, GL_FLOAT, 0, None)

	if normalsId != None:
		glBindBufferARB(GL_ARRAY_BUFFER_ARB, normalsId)
		glNormalPointer(GL_FLOAT, 0, None)

	if texCoordsId != None:
		glBindBufferARB(GL_ARRAY_BUFFER_ARB, texCoordsId)
		glTexCoordPointer(2, GL_FLOAT, 0, None)

	glDrawArrays(GL_TRIANGLES, 0, vertexCount)
	glBindBufferARB(GL_ARRAY_BUFFER_ARB, 0)

	if texCoordsId != None:
		glDisableClientState(GL_TEXTURE_COORD_ARRAY)

	if normalsId != None:
		glDisableClientState(GL_NORMAL_ARRAY)

	glDisableClientState(GL_VERTEX_ARRAY)
def loadTexture(filename):
	""" Loads a texture from file, returns (textureId, textureWidthRatio, textureHeightRatio) """
	image = pygame.image.load(filename)

	width = image.get_width()
	height = image.get_height()

	textureWidthRatio = 1.0
	textureHeightRatio = 1.0

	NPOTSupported = extensionSupported("GL_ARB_texture_non_power_of_two")

	if not NPOTSupported:
		width = nearestPowerOfTwo(image.get_width())
		height = nearestPowerOfTwo(image.get_height())

		textureWidthRatio = float(image.get_width()) / width
		textureHeightRatio = float(image.get_height()) / height

	if width > glGetIntegerv(GL_MAX_TEXTURE_SIZE):
		sys.stderr.write("ERROR: Texture is bigger than the maximum texture size of your graphics card\n")
		Global.quit = 1
		return

	textureId = glGenTextures(1)

	glBindTexture(GL_TEXTURE_2D, textureId)

	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
	glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
	
	glTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT )
	glTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT )

	if not NPOTSupported:
		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA,
				GL_UNSIGNED_BYTE, pygame.image.tostring(image, "RGBA", 1))
	else:
		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA,
				GL_UNSIGNED_BYTE, None)
		glTexSubImage2D(GL_TEXTURE_2D, 0 , 0, 0,
				image.get_width(), image.get_height(), GL_RGBA,
				GL_UNSIGNED_BYTE, pygame.image.tostring(image, "RGBA", 1))

	return (textureId, textureWidthRatio, textureHeightRatio)	
def extensionSupported(TargetExtension):
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
	
	wireframe = False	
	vertices = []
	reDraw = False
	toggleDrawAxes = False
	spectator = False
	numberOfVertices = 0	

	def __init__(self, octree, main, config):
		global g_fVBOObjects
		g_fVBOObjects = []
		
		self.octree = octree
		self.main = main # TODO: Away with it BLURP!
		self.config = config

		self.g_nFrames = 0
		self.NPOTSupported = extensionSupported("GL_ARB_texture_non_power_of_two")
		
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
			self.vertices.append( CVector3(i[0], i[1], i[2]) )
			self.numberOfVertices += 1
			texCoords[nIndex, 0] = (i[0]-xMin) / sizeX * textureWidthRatio
			texCoords[nIndex, 1] = (i[2]-zMin) / sizeY * textureHeightRatio
			nIndex += 1

		self.verticesId, self.vnormalsId, self.texCoordsId = createVBO(
				vertices, vnormals, texCoords)

		g_pMesh.verticesId = self.verticesId
		g_pMesh.vnormalsId = self.vnormalsId
		g_pMesh.texCoordsId = self.texCoordsId
		g_pMesh.vertexCount = self.vertexCount

		g_fVBOObjects.append(g_pMesh)
	def initGL(self):
		from skydome import Skydome

		if not glInitVertexBufferObjectARB():
			sys.stderr.write("ERROR: Vertex buffer objects is not supported\n")
			Global.quit = 1
			return

		glClearColor( 0.0, 0.0, 0.0, 0.0)
		glClearDepth(1.0)
		glDepthFunc(GL_LEQUAL)
		glEnable(GL_DEPTH_TEST)
		glShadeModel(GL_SMOOTH)
		glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
		glViewport(0, 0, self.config.getint('Resolution', 'Width'),
				self.config.getint('Resolution', 'Height'))
		glMatrixMode(GL_PROJECTION)

		#glOrtho(0.0, 1.0, 0.0, 1.0, -1.0, 1.0)

		glLoadIdentity()
		gluPerspective(60.0, self.config.getfloat('Resolution','Width')
				/ self.config.getfloat('Resolution', 'Height'), 0.1, 5000.0)
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

	def printFPS(self):
		pygame.display.set_caption("FarornasGrotta - %d FPS" % (self.g_nFrames))
		self.g_nFrames = 0
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

		if self.reDraw:
			self.octree.g_EndNodeCount = 0
			self.octree.debug.Clear()
			self.octree.DestroyOctree()
			self.octree.GetSceneDimensions(self.vertices, self.numberOfVertices)
			self.octree.CreateNode(self.vertices, self.numberOfVertices, self.octree.GetCenter(), self.octree.GetWidth())
			self.reDraw = False


		glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )
		glLoadIdentity()

		if self.toggleDrawAxes:
			self.drawAxes()

		glClearColor(0.4, 0.4, 0.4, 0.0)

		if self.wireframe:
			glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
		else:
			glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)


		glLoadIdentity()

		glRotatef(self.main.Input.xrot, 1.0, 0.0, 0.0)
		glRotatef(self.main.Input.yrot, 0.0, 1.0, 0.0)

		# SkyDome
		self.skydome.draw()

		if self.spectator:
			glTranslated(-self.main.Input.xpos, -self.main.Input.ypos,-self.main.Input.zpos)
		else:
			glTranslated(
					-self.main.player.position[0]-0.2*math.sin(math.radians(self.main.player.orientation[1])),
					-self.main.player.position[1]-2.2,
					-self.main.player.position[2]+0.2*math.cos(math.radians(self.main.player.orientation[1]-180))
					)

		self.g_nFrames += 1

		if self.toggleDrawAxes:
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

			
			drawVBO(g_fVBOObjects[i].verticesId, g_fVBOObjects[i].vnormalsId, 
					g_fVBOObjects[i].vertexCount, g_fVBOObjects[i].texCoordsId)

			glDisable(GL_TEXTURE_2D)
			#glDisable(GL_BLEND)

		glPopMatrix()


		# // Disable Pointers
		glDisableClientState( GL_VERTEX_ARRAY )					# // Disable Vertex Arrays
		glDisableClientState( GL_TEXTURE_COORD_ARRAY )			# // Disable Texture Coord Arrays
		glDisableClientState(GL_NORMAL_ARRAY)

		glDisable(GL_FOG)

		if self.octree.debugLines:
			self.octree.debug.RenderDebugLines()
		
		if self.octree.g_MaxSubdivisions:
			# Here we draw the octree, starting with the root node and recursing down each node.
			# When we get to each of the end nodes we will draw the vertices assigned to them.
			self.octree.DrawOctree(self.octree)
			
			if self.octree.debugLines:
				# Render the cube'd nodes to visualize the octree (in wire frame mode)
				self.octree.debug.RenderDebugLines()

		for obj in objects:
			if obj != self.main.player or self.spectator:
				obj.draw()

		glFlush()

		pygame.display.flip()

		err = glGetError()
		if err:
			print "OpenGL Error:",err,"(",gluErrorString(err),")"

