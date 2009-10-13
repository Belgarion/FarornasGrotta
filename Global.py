from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL import GL
from OpenGL import GLU

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
	Level = [[]]
	numberOfVertices = 0
	vertices = []
	wireframe = False
	VBOSupported = False

	g_Debug = CDebug()

	# Turn lighting on initially
	g_bLighting = 1
