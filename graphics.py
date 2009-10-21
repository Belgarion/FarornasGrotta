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

def nearestPowerOfTwo(v):
	v -= 1
	v |= v >> 1
	v |= v >> 2
	v |= v >> 4
	v |= v >> 8
	v |= v >> 16
	v += 1
	return v

def load_level(level):
	WholeMap = []	

	level = open(level, "r")
	for line in level:
		temp = line.split(" ")
		temp[2] = temp[2].replace("\r\n", "")

		Global.vertices.append(CVector3(float(temp[0]),float(temp[1]),float(temp[2])))
		WholeMap.append(CVector3(float(temp[0]),float(temp[1]),float(temp[2])))
		Global.g_NumberOfVerts += 1
	
	level.close()
	return WholeMap

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
		self.m_pTexCoords = Numeric.zeros ((self.m_nVertexCount, 2), 'f')	# // Texture Coordinates

		nIndex = 0
		nTIndex = 0
		for i in iLevel:
			self.m_pVertices[nIndex, 0] = i.x 
			self.m_pVertices[nIndex, 1] = i.y * flHeightScale + self.position_y
			self.m_pVertices[nIndex, 2] = i.z
			self.m_pTexCoords[nTIndex, 0] = (i.x-xMin) / sizeX * textureWidthRatio
			self.m_pTexCoords[nTIndex, 1] = (i.z-zMin) / sizeY * textureHeightRatio
			nIndex += 1
			nTIndex += 1

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

			# // Our Copy Of The Data Is No Longer Necessary, It Is Safe In The Graphics Card
			self.m_pVertices = None
			self.m_pTexCoords = None
		return


class Graphics:
	def __init__(self):
		global g_fVBOObjects

		g_fVBOObjects = []
		self.g_nFrames = 0

		self.g_Octree = COctree()

	def addSurface(self, Mesh, Map, Texture):
		global g_fVBOObjects
		g_pMesh = CMesh (Mesh)
		Level = load_level(Map)

		self.g_Octree.GetSceneDimensions(Level, Global.numberOfVertices)
		self.g_Octree.CreateNode(Level, Global.numberOfVertices, self.g_Octree.GetCenter(), self.g_Octree.GetWidth())

		image = pygame.image.load(Texture)

		width = image.get_width()
		height = image.get_height()

		width = nearestPowerOfTwo(width)
		height = nearestPowerOfTwo(height)

		textureWidthRatio = float(image.get_width()) / width
		textureHeightRatio = float(image.get_height()) / height

		if width > glGetIntegerv(GL_MAX_TEXTURE_SIZE):
			sys.stderr.write("ERROR: Texture is bigger than the maximum texture size of your graphics card\n")
			Global.quit = 1
			return

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

		texture = glGenTextures(1)

		glBindTexture(GL_TEXTURE_2D, texture)

		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
		glTexSubImage2D(GL_TEXTURE_2D, 0 , 0, 0, image.get_width(), image.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, pygame.image.tostring(image, "RGBA", 1))
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
		glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
		glEnable(GL_TEXTURE_2D)

		g_pMesh.nTextureId = texture

		# // Set Pointers To Our Data
		if (Global.VBOSupported):
			# // Enable Pointers
			glEnableClientState( GL_VERTEX_ARRAY )						# // Enable Vertex Arrays
			glEnableClientState( GL_TEXTURE_COORD_ARRAY )				# // Enable Texture Coord Arrays

			g_fVBOObjects.append(g_pMesh)

			glBindBufferARB( GL_ARRAY_BUFFER_ARB, g_pMesh.m_nVBOVertices )
			glVertexPointer( 3, GL_FLOAT, 0, None )				# // Set The Vertex Pointer To The Vertex Buffer
			glBindBufferARB( GL_ARRAY_BUFFER_ARB, g_pMesh.m_nVBOTexCoords )
			glTexCoordPointer( 2, GL_FLOAT, 0, None )				# // Set The TexCoord Pointer To The TexCoord Buffer

			glDisableClientState( GL_VERTEX_ARRAY )					# // Disable Vertex Arrays
			glDisableClientState( GL_TEXTURE_COORD_ARRAY )			# // Disable Texture Coord Arrays

		else:
			# You can use the pythonism glVertexPointerf (), which will convert the numarray into
			# the needed memory for VertexPointer. This has two drawbacks however:
			#	1) This does not work in Python 2.2 with PyOpenGL 2.0.0.44
			#	2) In Python 2.3 with PyOpenGL 2.0.1.07 this is very slow.
			# See the PyOpenGL documentation. Section "PyOpenGL for OpenGL Programmers" for details
			# regarding glXPointer API.
			# Also see OpenGLContext Working with Numeric Python
			# glVertexPointerf ( g_pMesh.m_pVertices ) 	# // Set The Vertex Pointer To Our Vertex Data
			# glTexCoordPointerf ( g_pMesh.m_pTexCoords ) 	# // Set The Vertex Pointer To Our TexCoord Data
			#
			#
			# The faster approach is to make use of an opaque "string" that represents the
			# the data (vertex array and tex coordinates in this case).
			print "aaa"
			print g_pMesh.m_pVertices_as_string
			glVertexPointer( 3, GL_FLOAT, 0, g_pMesh.m_pVertices_as_string)  	# // Set The Vertex Pointer To Our Vertex Data
			glTexCoordPointer( 2, GL_FLOAT, 0, g_pMesh.m_pTexCoords_as_string) 	# // Set The Vertex Pointer To Our TexCoord Data

		glDisable(GL_TEXTURE_2D)




	def initGL(self):
		Global.VBOSupported = self.IsExtensionSupported("GL_ARB_vertex_buffer_object")

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
		gluPerspective( 60, 640/480, 0.1, 5000.0)
		glMatrixMode(GL_MODELVIEW)

		#Lighting
		diffuseMaterial = (0.5, 0.5, 0.0, 1.0)
		mat_specular = (1.0, 1.0, 1.0, 1.0)
		light_position = (150.0, 0.0, 75.0, 1.0)

		glMaterialfv(GL_FRONT, GL_AMBIENT, diffuseMaterial)
		glMaterialfv(GL_FRONT, GL_DIFFUSE, diffuseMaterial)
		glLightfv(GL_LIGHT0, GL_POSITION, light_position)

		glEnable(GL_LIGHTING)
		glEnable(GL_LIGHT0)

		glColorMaterial(GL_FRONT, GL_DIFFUSE)
		glEnable(GL_COLOR_MATERIAL)
		############


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
			self.g_nFrames = 0
			if sys.platform == "win32": break
			time.sleep(1.0)

	def drawAxes(self):
		""" Draws x, y and z axes """
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

		glRotatef(Global.Input.xrot, 1.0, 0.0, 0.0)
		glRotatef(Global.Input.yrot, 0.0, 1.0, 0.0)
		glTranslated(-Global.Input.xpos, -Global.Input.ypos,-Global.Input.zpos)
		
		self.g_nFrames += 1

		glClearColor(0.4, 0.4, 0.4, 0.0)

		if Global.wireframe:
			glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
		else:
			glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)


		light_position = (150.0, 0.0, 75.0, 1.0)
		glLightfv(GL_LIGHT0, GL_POSITION, light_position)


		glColor3f(1.0, 1.0, 1.0)


		# // Enable Pointers
		glEnableClientState( GL_VERTEX_ARRAY )						# // Enable Vertex Arrays
		glEnableClientState( GL_TEXTURE_COORD_ARRAY )				# // Enable Texture Coord Arrays


		for i in xrange(len(g_fVBOObjects)):
			#glEnable(GL_BLEND)
			#glBlendFunc(GL_ONE, GL_ONE)
			glBindTexture(GL_TEXTURE_2D, g_fVBOObjects[i].nTextureId)
			glEnable(GL_TEXTURE_2D)


			glBindBufferARB( GL_ARRAY_BUFFER_ARB, g_fVBOObjects[i].m_nVBOVertices )
			glVertexPointer(3, GL_FLOAT, 0, None)
			glBindBufferARB(GL_ARRAY_BUFFER_ARB, g_fVBOObjects[i].m_nVBOTexCoords)
			glTexCoordPointer(2, GL_FLOAT, 0, None)
			glDrawArrays( GL_TRIANGLES, 0, g_fVBOObjects[i].m_nVertexCount )

			glDisable(GL_TEXTURE_2D)

		# // Disable Pointers
		glDisableClientState( GL_VERTEX_ARRAY )					# // Disable Vertex Arrays
		glDisableClientState( GL_TEXTURE_COORD_ARRAY )			# // Disable Texture Coord Arrays




		if Global.g_MaxSubdivisions:
			# Here we draw the octree, starting with the root node and recursing down each node.
			# When we get to each of the end nodes we will draw the vertices assigned to them.
			self.g_Octree.DrawOctree(self.g_Octree)
			
			if Global.g_bDebugLines:
				# Render the cube'd nodes to visualize the octree (in wire frame mode)
				Global.g_Debug.RenderDebugLines()



#		glBegin(GL_QUADS)

#		x = objects[0].position[0]
#		y = objects[0].position[1]
#		z = objects[0].position[2]


#		glColor3f(0.0,1.0,0.0)
#		glVertex3f( x+100.0, y+100.0,z+-100.0);		# Top Right Of The Quad (Top)
#		glVertex3f(x+-100.0, y+100.0,z+-100.0);		# Top Left Of The Quad (Top)
#		glVertex3f(x+-100.0, y+100.0, z+100.0);		# Bottom Left Of The Quad (Top)
#		glVertex3f( x+100.0, y+100.0, z+100.0);		# Bottom Right Of The Quad (Top)
#
#		glColor3f(1.0,0.5,0.0);			# Set The Color To Orange
#		glVertex3f( x+100.0,y+-100.0, z+100.0);		# Top Right Of The Quad (Bottom)
#		glVertex3f(x+-100.0,y+-100.0, z+100.0);		# Top Left Of The Quad (Bottom)
#		glVertex3f(x+-100.0,y+-100.0,z+-100.0);		# Bottom Left Of The Quad (Bottom)
#		glVertex3f( x+100.0,y+-100.0,z+-100.0);		# Bottom Right Of The Quad (Bottom)
#
#		glColor3f(1.0,0.0,0.0);			# Set The Color To Red
#		glVertex3f( x+100.0, y+100.0, z+100.0);		# Top Right Of The Quad (Front)
#		glVertex3f(x+-100.0, y+100.0, z+100.0);		# Top Left Of The Quad (Front)
#		glVertex3f(x+-100.0,y+-100.0, z+100.0);		# Bottom Left Of The Quad (Front)
#		glVertex3f( x+100.0,y+-100.0, z+100.0);		# Bottom Right Of The Quad (Front)
#
#		glColor3f(1.0,1.0,0.0);			# Set The Color To Yellow
#		glVertex3f( x+100.0,y+-100.0,z+-100.0);		# Bottom Left Of The Quad (Back)
#		glVertex3f(x+-100.0,y+-100.0,z+-100.0);		# Bottom Right Of The Quad (Back)
#		glVertex3f(x+-100.0, y+100.0,z+-100.0);		# Top Right Of The Quad (Back)
#		glVertex3f( x+100.0, y+100.0,z+-100.0);		# Top Left Of The Quad (Back)
#
#		glColor3f(0.0,0.0,1.0);			# Set The Color To Blue
#		glVertex3f(x+-100.0, y+100.0, z+100.0);		# Top Right Of The Quad (Left)
#		glVertex3f(x+-100.0, y+100.0,z+-100.0);		# Top Left Of The Quad (Left)
#		glVertex3f(x+-100.0,y+-100.0,z+-100.0);		# Bottom Left Of The Quad (Left)
#		glVertex3f(x+-100.0,y+-100.0, z+100.0);		# Bottom Right Of The Quad (Left)
#
#		glColor3f(1.0,0.0,1.0);			# Set The Color To Violet
#		glVertex3f( x+100.0, y+100.0,z+-100.0);		# Top Right Of The Quad (Right)
#		glVertex3f( x+100.0, y+100.0, z+100.0);		# Top Left Of The Quad (Right)
#		glVertex3f( x+100.0,y+-100.0, z+100.0);		# Bottom Left Of The Quad (Right)
#		glVertex3f( x+100.0,y+-100.0,z+-100.0);		# Bottom Right Of The Quad (Right)
#		glColor3f(1.0, 1.0, 1.0)
#		glEnd();				# Done Drawing The Quad

		glFlush()

		pygame.display.flip()
