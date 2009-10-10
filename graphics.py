import pygame
from Global import Global
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL import GL
from OpenGL import GLU
import numpy as Numeric
from OpenGL.GL.ARB.vertex_buffer_object import *
import time

def load_level(name):
	f = open(name, "r")
	lines = f.readlines()
	f.close()
	level = []
	x = 0
	y = 0
	for line in lines:
		line2 = []
		for i in line.rsplit(" "):
			line2.append(float(i.replace("\n", "")))
			y+=1
		level.append(line2)
		x+=1
	return level

class CVert:
	def __init__(self, x = 0.0, y = 0.0, z = 0.0):
		self.x = 0
		self.y = 0
		self.z = 0

CVec = CVert

class CTexCoord:
	""" // Texture Coordinate Class """
	def __init__ (self, u = 0.0, v = 0.0):
		self.u = u # // U Component
		self.v = v

class CMesh:
	""" // Mesh Data """
	MESH_RESOLUTION = 4.0
	MESH_HEIGHTSCALE = 2.0

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

	def LoadHeightmap( self, flHeightScale, flResolution, iLevel):
		""" // Heightmap Loader """

		# // Generate Vertex Field
		sizeX = len(iLevel)
		sizeY = len(iLevel[0])

		print sizeX, sizeY, "titta her"

		self.m_nVertexCount = int ( sizeX * sizeY * 6 / ( flResolution * flResolution ) )
		self.m_pVertices = Numeric.zeros ((self.m_nVertexCount, 3), 'f') 			# // Vertex Data
		self.m_pTexCoords = Numeric.zeros ((self.m_nVertexCount, 2), 'f') 			# // Texture Coordinates

		nZ = 0
		nIndex = 0
		nTIndex = 0
		half_sizeX = float (sizeX) / 1.0
		half_sizeY = float (sizeY) / 1.0
		flResolution_int = int (flResolution)
		while (nZ < len(iLevel)-4):
			nX = 0
			while (nX < len(iLevel[0])-4):
				for nTri in xrange (6):
					# // Using This Quick Hack, Figure The X,Z Position Of The Point
					flX = float (nX)
					if (nTri == 1) or (nTri == 2) or (nTri == 5):
						flX += flResolution
					flZ = float (nZ)
					if (nTri == 2) or (nTri == 4) or (nTri == 5):
						flZ += flResolution
					x = flX - half_sizeX
					y = iLevel[int(flX)][int(flZ)] * flHeightScale
					z = flZ - half_sizeY
					self.m_pVertices [nIndex, 0] = x
					self.m_pVertices [nIndex, 1] = y + self.position_y
					self.m_pVertices [nIndex, 2] = z
					self.m_pTexCoords [nTIndex, 0] = flX / sizeX
					self.m_pTexCoords [nTIndex, 1] =  flZ / sizeY
					nIndex += 1
					nTIndex += 1
					
				nX += flResolution_int
			nZ += flResolution_int

		self.m_pVertices_as_string = self.m_pVertices.tostring () 
		self.m_pTexCoords_as_string = self.m_pTexCoords.tostring () 

		# // Load The Texture Into OpenGL
		#self.m_nTextureID = glGenTextures (1)						# // Get An Open ID
		#glBindTexture( GL_TEXTURE_2D, self.m_nTextureID )			# // Bind The Texture
		#glTexImage2D( GL_TEXTURE_2D, 0, 3, sizeX, sizeY, 0, GL_RGB, GL_UNSIGNED_BYTE, 
		#	self.m_pTextureImage.tostring ("raw", "RGB", 0, -1))
		#glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)
		#glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)

		# // Free The Texture Data
		#self.m_pTextureImage = None
		return True

	def BuildVBOs (self):
		""" // Generate And Bind The Vertex Buffer """
		if (g_fVBOSupported):
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
			self.m_pVertices = None
			self.m_pTexCoords = None
			self.m_pTexCoords = None
		return


class Graphics:
	def __init__(self):
		global g_fVBOSupported, g_fVBOObjects

		g_fVBOSupported = False
		g_fVBOObjects = []

		self.g_nFrames = 0

	def addSurface(self, Mesh, Map, Texture):
		global width, height, g_fVBOSupported, g_fVBOObjects
		g_pMesh = CMesh (Mesh)
		Level = load_level(Map)

		if (not g_pMesh.LoadHeightmap (CMesh.MESH_HEIGHTSCALE, CMesh.MESH_RESOLUTION, Level)):
			print "Error Loading Heightmap"
			sys.exit(1)
			return False

		g_fVBOSupported = self.IsExtensionSupported ("GL_ARB_vertex_buffer_object")
		
		if (g_fVBOSupported):
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

		image = pygame.image.load(Texture)

		width = image.get_width()
		height = image.get_height()
		
		texture = glGenTextures(1)
		
		GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
		GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, image.get_width(), image.get_height(), 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, pygame.image.tostring(image, "RGBA", 1))
		GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_NEAREST)
		GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_NEAREST)
		GL.glEnable(GL.GL_TEXTURE_2D)

		g_pMesh.nTextureId = texture

		# // Set Pointers To Our Data
		if( g_fVBOSupported ):
			# // Enable Pointers
			glEnableClientState( GL_VERTEX_ARRAY )						# // Enable Vertex Arrays
			glEnableClientState( GL_TEXTURE_COORD_ARRAY )				# // Enable Texture Coord Arrays

			g_fVBOObjects.append(g_pMesh)
			print g_pMesh.m_nVBOVertices, g_pMesh.m_nVBOTexCoords

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




	def initGL(self):		
					
		glClearColor( 0.0, 0.0, 0.0, 0.0)
		glClearDepth(1.0)
		glDepthFunc(GL_LEQUAL)
		glEnable(GL_DEPTH_TEST)
		glShadeModel(GL_SMOOTH)
		glHint (GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
		glEnable(GL_TEXTURE_2D)
		glColor4f (1.0, 6.0, 6.0, 1.0)
		glViewport (0, 0, 640, 480)
		glMatrixMode(GL_PROJECTION)
		
		#glOrtho(0.0, 1.0, 0.0, 1.0, -1.0, 1.0)
		
		glLoadIdentity()
		gluPerspective( 60, 640/480, 0.1, 5000.0)
		glMatrixMode(GL_MODELVIEW)

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
			time.sleep(1.0)
			

	def draw(self, objects):
		global g_fVBOSupported, g_fVBOObjects

		glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT ) 
		glLoadIdentity()
		glRotatef(Global.Input.xrot, 1.0, 0.0, 0.0)
		glRotatef(Global.Input.yrot, 0.0, 1.0, 0.0)
		glTranslated(-Global.Input.xpos, -Global.Input.ypos,-Global.Input.zpos)
		
		self.g_nFrames += 1
		

		# // Enable Pointers
		glEnableClientState( GL_VERTEX_ARRAY )						# // Enable Vertex Arrays
		glEnableClientState( GL_TEXTURE_COORD_ARRAY )				# // Enable Texture Coord Arrays


		for i in xrange(len(g_fVBOObjects)):
			GL.glBindTexture(GL.GL_TEXTURE_2D, g_fVBOObjects[i].nTextureId)
			GL.glEnable(GL.GL_TEXTURE_2D)


			glBindBufferARB( GL_ARRAY_BUFFER_ARB, g_fVBOObjects[i].m_nVBOVertices )
			glVertexPointer(3, GL_FLOAT, 0, None)
			glBindBufferARB(GL_ARRAY_BUFFER_ARB, g_fVBOObjects[i].m_nVBOTexCoords)
			glTexCoordPointer(2, GL_FLOAT, 0, None)
			glDrawArrays( GL_TRIANGLES, 0, g_fVBOObjects[i].m_nVertexCount )

		# // Disable Pointers
		glDisableClientState( GL_VERTEX_ARRAY )					# // Disable Vertex Arrays
		glDisableClientState( GL_TEXTURE_COORD_ARRAY )			# // Disable Texture Coord Arrays
		
		
		glBegin(GL_QUADS);


		x = objects[0].position[0]
		y = objects[0].position[1]
		z = objects[0].position[2]

		
		glColor3f(0.0,1.0,0.0)
		glVertex3f( x+100.0, y+100.0,z+-100.0);		# Top Right Of The Quad (Top)
		glVertex3f(x+-100.0, y+100.0,z+-100.0);		# Top Left Of The Quad (Top)
		glVertex3f(x+-100.0, y+100.0, z+100.0);		# Bottom Left Of The Quad (Top)
		glVertex3f( x+100.0, y+100.0, z+100.0);		# Bottom Right Of The Quad (Top)

		glColor3f(1.0,0.5,0.0);			# Set The Color To Orange
		glVertex3f( x+100.0,y+-100.0, z+100.0);		# Top Right Of The Quad (Bottom)
		glVertex3f(x+-100.0,y+-100.0, z+100.0);		# Top Left Of The Quad (Bottom)
		glVertex3f(x+-100.0,y+-100.0,z+-100.0);		# Bottom Left Of The Quad (Bottom)
		glVertex3f( x+100.0,y+-100.0,z+-100.0);		# Bottom Right Of The Quad (Bottom)

		glColor3f(1.0,0.0,0.0);			# Set The Color To Red
		glVertex3f( x+100.0, y+100.0, z+100.0);		# Top Right Of The Quad (Front)
		glVertex3f(x+-100.0, y+100.0, z+100.0);		# Top Left Of The Quad (Front)
		glVertex3f(x+-100.0,y+-100.0, z+100.0);		# Bottom Left Of The Quad (Front)
		glVertex3f( x+100.0,y+-100.0, z+100.0);		# Bottom Right Of The Quad (Front)

		glColor3f(1.0,1.0,0.0);			# Set The Color To Yellow
		glVertex3f( x+100.0,y+-100.0,z+-100.0);		# Bottom Left Of The Quad (Back)
		glVertex3f(x+-100.0,y+-100.0,z+-100.0);		# Bottom Right Of The Quad (Back)
		glVertex3f(x+-100.0, y+100.0,z+-100.0);		# Top Right Of The Quad (Back)
		glVertex3f( x+100.0, y+100.0,z+-100.0);		# Top Left Of The Quad (Back)

		glColor3f(0.0,0.0,1.0);			# Set The Color To Blue
		glVertex3f(x+-100.0, y+100.0, z+100.0);		# Top Right Of The Quad (Left)
		glVertex3f(x+-100.0, y+100.0,z+-100.0);		# Top Left Of The Quad (Left)
		glVertex3f(x+-100.0,y+-100.0,z+-100.0);		# Bottom Left Of The Quad (Left)
		glVertex3f(x+-100.0,y+-100.0, z+100.0);		# Bottom Right Of The Quad (Left)

		glColor3f(1.0,0.0,1.0);			# Set The Color To Violet
		glVertex3f( x+100.0, y+100.0,z+-100.0);		# Top Right Of The Quad (Right)
		glVertex3f( x+100.0, y+100.0, z+100.0);		# Top Left Of The Quad (Right)
		glVertex3f( x+100.0,y+-100.0, z+100.0);		# Bottom Left Of The Quad (Right)
		glVertex3f( x+100.0,y+-100.0,z+-100.0);		# Bottom Right Of The Quad (Right)
		glColor3f(1.0, 1.0, 1.0)
		glEnd();				# Done Drawing The Quad

		glFlush()

		pygame.display.flip()
