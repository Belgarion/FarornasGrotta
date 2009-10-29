from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL import GL
from OpenGL import GLU
import pygame
import sys
try:
	import numpy as Numeric
except:
	import Numeric

def nearestPowerOfTwo(v):
	v -= 1
	v |= v >> 1
	v |= v >> 2
	v |= v >> 4
	v |= v >> 8
	v |= v >> 16
	v += 1
	return v

def loadRaw(filename):
	f = open(filename, "r")
	lines = f.readlines()
	f.close()

	vertices = []
	for line in lines:
		pos = line.rsplit(" ")
		if len(pos) < 3:
			continue
		vertices.append( (float(pos[0]), float(pos[1]), float(pos[2])) )
	
	return vertices

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
			a = pos[1].rsplit("/")
			b = pos[2].rsplit("/")
			c = pos[3].rsplit("/")

			facesv.append( (int(a[0])-1, int(b[0])-1, int(c[0])-1) )
			if a[1] != '':
				facest.append( (int(a[1])-1, int(b[1])-1, int(c[1])-1) )
			else:
				facest.append( (0, 0, 0) )
			if a[2] != '':
				facesn.append( (int(a[2])-1, int(b[2])-1, int(c[2])-1) )
			else:
				facesn.append( (0, 0, 0) )

	vertices = Numeric.zeros((len(facesv)*3, 3), 'f')
	vnormals = Numeric.zeros((len(facesn)*3, 3), 'f')
	#texCoords = Numeric.zeros((len(facest*3), 2), 'f')
	vertexCount = len(facesv)*3
	
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

	return (vertices, vnormals, (facesv, facest, facesn))

def loadTexture(filename):
	""" Loads a texture from file, returns (textureId, textureWidthRatio, textureHeightRatio) """
	image = pygame.image.load(filename)

	width = image.get_width()
	height = image.get_height()

	textureWidthRatio = 1.0
	textureHeightRatio = 1.0

	if not Global.NPOTSupported:
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

	if Global.NPOTSupported:
		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, pygame.image.tostring(image, "RGBA", 1))
	else:
		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
		glTexSubImage2D(GL_TEXTURE_2D, 0 , 0, 0, image.get_width(), image.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, pygame.image.tostring(image, "RGBA", 1))

	return (textureId, textureWidthRatio, textureHeightRatio)


# This is our constructor that allows us to initialize our data upon creating an instance
class CVector3:

	def __init__(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z

	def __add__(self, v):
       		return CVector3(self.x + v[0], self.y + v[1], self.z + v[2])

	def __sub__(self, v):
		return CVector3(self.x - v[0], self.y - v[1], self.z - v[2])

	def __mul__(self, num):
		return CVector3(self.x * num, self.y * num, self.z * num)

	def __div__(self, num):
		return CVector3(self.x / num, self.y / num, self.z / num)

# Visually Octrees
class CDebug:

	def __init__(self):
		self.m_vLines = []

	# This adds a line to out list of debug lines
	def AddDebugLine(self, vPoint1, vPoint2):
		# Add the 2 points that make up the line into our line list.
		m_vLines.push_back(vPoint1)
		m_vLines.push_back(vPoint2)

	# This adds a rectangle with a given center, width, height and depth to our list
	def AddDebugRectangle(self, vCenter, width, height, depth):
		# So we can work with the code better, we divide the dimensions in half.
		# That way we can create the cube from the center outwards.
		width /= 2.0
		height /= 2.0
		depth /= 2.0

		# Below we create all the 8 points so it will be easier to input the lines
		# of the cube.  With the dimensions we calculate the points.
		vTopLeftFront = CVector3( vCenter.x - width, vCenter.y + height, vCenter.z + depth)
		vTopLeftBack = CVector3( vCenter.x - width, vCenter.y + height, vCenter.z - depth)
		vTopRightBack = CVector3( vCenter.x + width, vCenter.y + height, vCenter.z - depth)
		vTopRightFront = CVector3( vCenter.x + width, vCenter.y + height, vCenter.z + depth)

		vBottom_LeftFront = CVector3( vCenter.x - width, vCenter.y - height, vCenter.z + depth)
		vBottom_LeftBack = CVector3( vCenter.x - width, vCenter.y - height, vCenter.z - depth)
		vBottomRightBack = CVector3( vCenter.x + width, vCenter.y - height, vCenter.z - depth)
		vBottomRightFront = CVector3( vCenter.x + width, vCenter.y - height, vCenter.z + depth)


		## TOP LINES
		self.m_vLines.append(vTopLeftFront)
		self.m_vLines.append(vTopRightFront)

		self.m_vLines.append(vTopLeftBack)
		self.m_vLines.append(vTopRightBack)

		self.m_vLines.append(vTopLeftFront)
		self.m_vLines.append(vTopLeftBack)

		self.m_vLines.append(vTopRightFront)
		self.m_vLines.append(vTopRightBack)


		## BOTTOM LINES
		self.m_vLines.append(vBottom_LeftFront)
		self.m_vLines.append(vBottomRightFront)

		self.m_vLines.append(vBottom_LeftBack)
		self.m_vLines.append(vBottomRightBack)

		self.m_vLines.append(vBottom_LeftFront)
		self.m_vLines.append(vBottom_LeftBack)

		self.m_vLines.append(vBottomRightFront)
		self.m_vLines.append(vBottomRightBack)


		## SIDE LINES
		self.m_vLines.append(vTopLeftFront)
		self.m_vLines.append(vBottom_LeftFront)

		self.m_vLines.append(vTopLeftBack)
		self.m_vLines.append(vBottom_LeftBack)

		self.m_vLines.append(vTopRightBack)
		self.m_vLines.append(vBottomRightBack)

		self.m_vLines.append(vTopRightFront)
		self.m_vLines.append(vBottomRightFront)


	# This renders all of the lines
	def RenderDebugLines(self):

		# Turn OFF lighting so the debug lines are bright yellow
		glDisable(GL_LIGHTING)

		# Start rendering lines
		glBegin(GL_LINES)

		# Turn the lines yellow
		#glColor3ub(255, 255, 0)

		# Go through the whole list of lines stored in the vector m_vLines.
		for i in xrange(len(self.m_vLines)):
			# Pass in the current point to be rendered as part of a line
			glVertex3f(self.m_vLines[i].x, self.m_vLines[i].y, self.m_vLines[i].z)

		# Stop rendering lines
		glEnd()

		# If we have lighting turned on, turn the lights back on
		if( Global.g_bLighting ):
			glEnable(GL_LIGHTING)

	# Destroy the list by set them to 0 again
	def Clear(self):
		self.m_vLines = CVector3()

class Global:
	quit = 0
	Input = None
	menu = None
	Level = [[]]
	numberOfVertices = 0
	vertices = []
	wireframe = False
	VBOSupported = False
	NPOTSupported = False
	mainMenuOpen = True
	mainMenuRow = 0
	drawAxes = False
	debugLines = False

	g_Debug = CDebug()

	# Turn lighting on initially
	g_bLighting = 1
