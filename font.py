from OpenGL.GL import *
import sys
try:
	import ImageFont
except:
	print "ERROR: Python Imaging Library is not installed"
	sys.exit()
from graphics import nearestPowerOfTwo

class Font:
	def __init__(self):
		self.font_height = 24

		try:
			self.ft = ImageFont.truetype("Rufscript010.ttf", self.font_height)
		except:
			print "WARNING: Unable to load font"
			self.ft = ImageFont.load_default()

		self.list_base = glGenLists(128)
		self.textures = [None] * 128

		for i in xrange(128):
			self.make_dlist(i)

		ft = None
		return

	def make_dlist(self, ch):
		if ch == 0:
			ch = ord(" ")

		glyph = self.ft.getmask(chr(ch))
		glyph_width, glyph_height = glyph.size

		width = nearestPowerOfTwo(glyph_width + 1)
		height = nearestPowerOfTwo(glyph_height + 1)

		data = ""
		for j in xrange(height):
			for i in xrange(width):
				if i >= glyph_width or j >= glyph_height:
					value = chr(0)
					data += value
					data += value
				else:
					value = chr(glyph.getpixel((i, j)))
					data += value
					data += value

		id = glGenTextures(1)
		self.textures[ch] = id

		glBindTexture(GL_TEXTURE_2D, id)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_LUMINANCE_ALPHA, GL_UNSIGNED_BYTE, data)

		data = None

		glNewList(self.list_base + ch, GL_COMPILE)

		if (ch == ord(" ")):
			glyph_advance = glyph_width
			glTranslatef(glyph_advance, 0, 0)
			glEndList()
		else:
			glBindTexture(GL_TEXTURE_2D, id)

			glPushMatrix()

			x = float(glyph_width) / float(width)
			y = float(glyph_height) / float(height)

			glBegin(GL_QUADS)
			glTexCoord2f(0, 0), glVertex2f(0, glyph_height)
			glTexCoord2f(0, y), glVertex2f(0, 0)
			glTexCoord2f(x, y), glVertex2f(glyph_width, 0)
			glTexCoord2f(x, 0), glVertex2f(glyph_width, glyph_height)
			glEnd()

			glPopMatrix()

			glTranslatef(glyph_width + 0.75, 0, 0)

			glEndList()

		return

	def glPrint(self, x, y, string):
		h = float(self.font_height) / 0.63

		if string == None or string == "":
			return

		lines = string.split("\n")

		glEnable(GL_TEXTURE_2D)
		glDisable(GL_DEPTH_TEST)
		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

		glListBase(self.list_base)

		for i in xrange(len(lines)):
			line = lines[i]

			glPushMatrix()
			glTranslatef(x, y - h*i, 0)

			glCallLists(line)

			glPopMatrix()

		glEnable(GL_DEPTH_TEST)
		glDisable(GL_BLEND)
		glDisable(GL_TEXTURE_2D)
		return

