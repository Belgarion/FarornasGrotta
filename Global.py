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


class Global:

	quit = 0
	Input = None
	menu = None
	Level = [[]]
	vertices = []
	reDraw = False

	wireframe = False
	VBOSupported = False
	NPOTSupported = False
	mainMenuOpen = True
	mainMenuRow = 0
	drawAxes = False
	debugLines = False
	spectator = False

	
	g_NumberOfVerts = 0


	# This holds if we want rendered or wire frame mode
	g_bRenderMode = 1


	g_bDebugLines = False
	numberOfVertices = 0
	wireframe = False
	VBOSupported = False
