import pygame
from Global import Global
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL import GL
from OpenGL import GLU
import numpy as Numeric
from OpenGL.GL.ARB.vertex_buffer_object import *
import time

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

	def LoadHeightmap( self, flHeightScale, flResolution ):
		""" // Heightmap Loader """

		# // Generate Vertex Field
		sizeX = len(Global.level)
		sizeY = len(Global.level[0])
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
		while (nZ < len(Global.level)-4):
			nX = 0
			while (nX < len(Global.level[0])-4):
				for nTri in xrange (6):
					# // Using This Quick Hack, Figure The X,Z Position Of The Point
					flX = float (nX)
					if (nTri == 1) or (nTri == 2) or (nTri == 5):
						flX += flResolution
					flZ = float (nZ)
					if (nTri == 2) or (nTri == 4) or (nTri == 5):
						flZ += flResolution
					x = flX - half_sizeX
					y = Global.level[int(flX)][int(flZ)] * flHeightScale
					z = flZ - half_sizeY
					self.m_pVertices [nIndex, 0] = x
					self.m_pVertices [nIndex, 1] = y + self.position_y
					self.m_pVertices [nIndex, 2] = z
					self.m_pTexCoords [nTIndex, 0] = flX / sizeX
					self.m_pTexCoords [nTIndex, 1] =  flZ / sizeY
					nIndex += 1
					nTIndex += 1
					if nIndex > 1 and nIndex < 6:
						print x, y, z, "x y zzzzz"

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
		global g_fVBOSupported, g_pMesh, g_pMesh2

		g_fVBOSupported = False
		g_pMesh = None
		g_pMesh2 = None

		self.g_nFrames = 0
	def initGL(self):
		global width, height, texture, g_pMesh, g_pMesh2, g_fVBOSupported
		
		
		g_fVBOSupported = self.IsExtensionSupported ("GL_ARB_vertex_buffer_object")

		g_pMesh = CMesh (0)
		g_pMesh2 = CMesh (50)
		if (not g_pMesh.LoadHeightmap (CMesh.MESH_HEIGHTSCALE, CMesh.MESH_RESOLUTION)):
			print "Error Loading Heightmap"
			sys.exit(1)
			return False
		if (not g_pMesh2.LoadHeightmap (CMesh.MESH_HEIGHTSCALE, CMesh.MESH_RESOLUTION)):
			print "Error Loading Heightmap"
			sys.exit(1)
			return False
		
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
			g_pMesh2.BuildVBOs()

		

		image = pygame.image.load("test.bmp")
		
		width = image.get_width()
		height = image.get_height()
		print width
		print height
		texture = glGenTextures(1)
		
		glBindTexture(GL_TEXTURE_2D, texture)
		
		
		GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
		GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, image.get_width(), image.get_height(), 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, pygame.image.tostring(image, "RGBA", 1))
		GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_NEAREST)
		GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_NEAREST)
		GL.glEnable(GL.GL_TEXTURE_2D)


		
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
			print Global.Input.xrot

	def draw(self):
		global g_pMesh, g_pMesh2, g_fVBOSupported
		
		glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT ) 
		glLoadIdentity()
		glRotatef(Global.Input.xrot, 1.0, 0.0, 0.0)
		glRotatef(Global.Input.yrot, 0.0, 1.0, 0.0)
		glTranslated(-Global.Input.xpos, -Global.Input.ypos,-Global.Input.zpos)
		
		self.g_nFrames += 1

		# // Enable Pointers
		glEnableClientState( GL_VERTEX_ARRAY )						# // Enable Vertex Arrays
		glEnableClientState( GL_TEXTURE_COORD_ARRAY )				# // Enable Texture Coord Arrays
		
		# // Set Pointers To Our Data
		if( g_fVBOSupported ):
			glBindBufferARB( GL_ARRAY_BUFFER_ARB, g_pMesh.m_nVBOVertices )
			glVertexPointer( 3, GL_FLOAT, 0, None )				# // Set The Vertex Pointer To The Vertex Buffer
			glBindBufferARB( GL_ARRAY_BUFFER_ARB, g_pMesh.m_nVBOTexCoords )
			glTexCoordPointer( 2, GL_FLOAT, 0, None )				# // Set The TexCoord Pointer To The TexCoord Buffer

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


		glDrawArrays( GL_TRIANGLES, 0, g_pMesh.m_nVertexCount )		# // Draw All Of The Triangles At Once

		
		glDisableClientState( GL_VERTEX_ARRAY )					# // Disable Vertex Arrays
		glDisableClientState( GL_TEXTURE_COORD_ARRAY )			# // Disable Texture Coord Arrays


		glEnableClientState( GL_VERTEX_ARRAY )						# // Enable Vertex Arrays
		glEnableClientState( GL_TEXTURE_COORD_ARRAY )				# // Enable Texture Coord Arrays


		if( g_fVBOSupported ):
			glBindBufferARB( GL_ARRAY_BUFFER_ARB, g_pMesh2.m_nVBOVertices )
			glVertexPointer( 3, GL_FLOAT, 0, None )				# // Set The Vertex Pointer To The Vertex Buffer
			glBindBufferARB( GL_ARRAY_BUFFER_ARB, g_pMesh2.m_nVBOTexCoords )
			glTexCoordPointer( 2, GL_FLOAT, 0, None )				# // Set The TexCoord Pointer To The TexCoord Buffer

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
			print g_pMesh2.m_pVertices_as_string
			glVertexPointer( 3, GL_FLOAT, 0, g_pMesh2.m_pVertices_as_string)  	# // Set The Vertex Pointer To Our Vertex Data
			glTexCoordPointer( 2, GL_FLOAT, 0, g_pMesh2.m_pTexCoords_as_string) 	# // Set The Vertex Pointer To Our TexCoord Data


		glDrawArrays( GL_TRIANGLES, 0, g_pMesh2.m_nVertexCount )		# // Draw All Of The Triangles At Once




		# // Disable Pointers
		glDisableClientState( GL_VERTEX_ARRAY )					# // Disable Vertex Arrays
		glDisableClientState( GL_TEXTURE_COORD_ARRAY )			# // Disable Texture Coord Arrays
		
		"""
		key = 0
		x = 0
		y = 0 # y is actually z here
		errors = 0
		glEnable(GL_TEXTURE_2D)
		glBindTexture(GL_TEXTURE_2D, texture)
		for line in level:
			if(x+1 < len(level)):
				for point in line:
					if y+1 < len(line):
					   
						glBegin(GL_TRIANGLE_STRIP)
						glTexCoord2f(float(x)/width, float(y)/height)
						glVertex3f(x, level[x][y], y)
			 
						glTexCoord2f(float(x)/width, (float(y)+1)/height)
						glVertex3f(x, level[x][y+1], y+1)
						
						glTexCoord2f((float(x)+1)/width, float(y)/height)
						glVertex3f(x+1, level[x+1][y], y)
						
						glTexCoord2f((float(x)+1)/width, (float(y)+1)/height)
						glVertex3f(x+1, level[x+1][y+1], y+1)
						glEnd()
					y += 1
			x += 1
			y = 0
		
		
		
		glPointSize(4.0)
		x=0
		y=0
		for line in level:
			for point in line:
				glBegin(GL_POINTS)
				glVertex3f(x, level[x][y], y)
				glEnd()
				y+=1
			y=0
			x+=1
		"""
		glFlush()

		pygame.display.flip()
