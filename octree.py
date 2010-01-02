#!/usr/bin/python
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL import GL
from OpenGL import GLU
from Global import *

import math


# This is our constructor that allows us to initialize our data upon creating an instance
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




# Visually Octrees
class CDebug:

	def __init__(self):
		self.m_vLines = []
			
	# This adds a line to out list of debug lines
	def AddDebugLine(self, vPoint1, vPoint2):
		# Add the 2 points that make up the line into our line list.
		self.m_vLines.push_back(vPoint1)
		self.m_vLines.push_back(vPoint2)

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

		vBottomLeftFront = CVector3( vCenter.x - width, vCenter.y - height, vCenter.z + depth)
		vBottomLeftBack = CVector3( vCenter.x - width, vCenter.y - height, vCenter.z - depth)
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
		self.m_vLines.append(vBottomLeftFront)
		self.m_vLines.append(vBottomRightFront)

		self.m_vLines.append(vBottomLeftBack)
		self.m_vLines.append(vBottomRightBack)

		self.m_vLines.append(vBottomLeftFront)
		self.m_vLines.append(vBottomLeftBack)

		self.m_vLines.append(vBottomRightFront)
		self.m_vLines.append(vBottomRightBack)


		## SIDE LINES
		self.m_vLines.append(vTopLeftFront)
		self.m_vLines.append(vBottomLeftFront)

		self.m_vLines.append(vTopLeftBack)
		self.m_vLines.append(vBottomLeftBack)

		self.m_vLines.append(vTopRightBack)
		self.m_vLines.append(vBottomRightBack)

		self.m_vLines.append(vTopRightFront)
		self.m_vLines.append(vBottomRightFront)


	# This renders all of the lines
	def RenderDebugLines(self):

		# Turn OFF lighting so the debug lines are bright yellow
		light = glIsEnabled(GL_LIGHTING)
		if light:	
			glDisable(GL_LIGHTING)
		# Start rendering lines
		glBegin(GL_LINES)

		# Turn the lines yellow
		glColor3ub(255, 255, 0)

		# Go through the whole list of lines stored in the vector m_vLines.
		for i in xrange(len(self.m_vLines)):
			# Pass in the current point to be rendered as part of a line
			glVertex3f(self.m_vLines[i].x, self.m_vLines[i].y, self.m_vLines[i].z)

		# Stop rendering lines
		glEnd()

		# If we have lighting turned on, turn the lights back on
		if light:
			glEnable(GL_LIGHTING)

	# Destroy the list by set them to 0 again
	def Clear(self):
		self.m_vLines = None
		self.m_vLines = []




# This returns the cross product between 2 vectors
def Cross(vVector1, vVector2):
	vNormal = CVector3(0, 0, 0)

	# Calculate the cross product with the non communitive equation
	vNormal.x = ((vVector1.y * vVector2.z) - (vVector1.z * vVector2.y))
	vNormal.y = ((vVector1.z * vVector2.x) - (vVector1.x * vVector2.z))
	vNormal.z = ((vVector1.x * vVector2.y) - (vVector1.y * vVector2.x))

	# Return the cross product
	return vNormal

# This returns the magnitude of a vector
def Magnitude(vNormal):
	# Here is the equation:  magnitude = sqrt(V.x^2 + V.y^2 + V.z^2) : Where V is the vector
	return sqrt( (vNormal.x * vNormal.x) + (vNormal.y * vNormal.y) + (vNormal.z * vNormal.z) )

# This returns a normalized vector
def Normalize(vVector):
	# Get the magnitude of our normal
	magnitude = Magnitude(vVector)

	# Now that we have the magnitude, we can divide our vector by that magnitude.
	# That will make our vector a total length of 1.  
	vVector = vVector / magnitude
	
	# Finally, return our normalized vector
	return vVector

class COctree:
	debug = CDebug()
	g_NumberOfVerts = 0
	g_TotalNodesDrawn = 0
	g_MaxTriangles = 100
	
	g_EndNodeCount = 0		
	g_CurrentSubdivision = 0
	g_bRenderMode = 1
	g_bLighting = 1
	g_MaxSubdivisions = 0
			
	debugLines = False
	
	def __init__(self):
	
		# This tells us if we want to display the yellow debug lines for our nodes
		self.g_bDisplayNodes = 1
	
		# This stores the total fave count that is in the nodes 3D space (how many "true"'s)
		self.totalFaceCount = 0

		# This tells us if we have divided this node into more sub nodes
		self.m_bSubDivided = False

		# This is the size of the cube for this current node
		self.m_Width = 0.0

		# This holds the amount of triangles stored in this node
		self.m_TriangleCount = 0

		# This is the center (X, Y, Z) point in this node
		self.m_vCenter = CVector3(0.0, 0.0, 0.0)

		# This stores the triangles that should be drawn with this node
		self.m_pVertices = CVector3(0.0, 0.0, 0.0)

		# These are the eight nodes branching down from this current node
		self.m_pOctreeNodes = []
		for i in xrange(8):
			self.m_pOctreeNodes.append(CVector3(0, 0, 0))
		
	# This returns the center of this node
	def GetCenter(self):
		return self.m_vCenter

	# This returns the triangle count stored in this node
	def GetTriangleCount(self):
		return self.m_TriangleCount

	# This returns the widht of this node (since it's a cube the height and depth are the same)
	def GetWidth(self):
		return self.m_Width

	# This returns if this node is subdivided or not
	def IsSubDivided(self):
		return self.m_bSubDivided

	# This returns the center point of the new subdivided node, depending on the ID
	def GetNewNodeCenter(self, 	vCenter,	width, nodeID):
		if nodeID == 0:
			return CVector3(vCenter.x - (width/4.0), vCenter.y + (width/4.0), vCenter.z + (width/4.0))

		elif nodeID == 1:
			return  CVector3(vCenter.x - (width/4.0), vCenter.y + (width/4.0), vCenter.z - (width/4.0))

		elif nodeID == 2:
			return  CVector3(vCenter.x + (width/4.0), vCenter.y + (width/4.0), vCenter.z - (width/4.0))

		elif nodeID == 3:
			return  CVector3(vCenter.x + (width/4.0), vCenter.y + (width/4.0), vCenter.z + (width/4.0))

		elif nodeID == 4:
			return  CVector3(vCenter.x - (width/4.0), vCenter.y - (width/4.0), vCenter.z + (width/4.0))

		elif nodeID == 5:
			return  CVector3(vCenter.x - (width/4.0), vCenter.y - (width/4.0), vCenter.z - (width/4.0))

		elif nodeID == 6:
			return  CVector3(vCenter.x + (width/4.0), vCenter.y - (width/4.0), vCenter.z - (width/4.0))

		elif nodeID == 7:
			return  CVector3(vCenter.x + (width/4.0), vCenter.y - (width/4.0), vCenter.z + (width/4.0))


	# This sets the initial width, height and depth for the whole scene
	def GetSceneDimensions(self, pVertices, g_NumberOfVerts):
		# Initialize some temporary variables to hold the max dimensions found
		maxWidth = maxHeight = maxDepth = 0.0

		# Return from this function if we passed in bad data
		if(not pVertices or g_NumberOfVerts <= 0):
			return

		# Go through all of the vertices and add them up to eventually find the center
		self.m_vCenter = CVector3(0.0, 0.0, 0.0)

		for i in xrange(g_NumberOfVerts):
			# Add the current vertex to the center variable (Using operator overloading)
			self.m_vCenter += pVertices[i]

		# Divide the total by the number of vertices to get the center point.
		# We could have overloaded the / symbol but I chose not to because we rarely use it.
		self.m_vCenter.x /= g_NumberOfVerts
		self.m_vCenter.y /= g_NumberOfVerts
		self.m_vCenter.z /= g_NumberOfVerts

		# Go through all of the vertices and find the max dimensions
		for i in xrange(g_NumberOfVerts):
			# Get the current dimensions for this vertex.  We use the abs() function
			# to get the absolute value because it might return a negative number.
			currentWidth  = abs(int(pVertices[i].x - self.m_vCenter.x))
			currentHeight = abs(int(pVertices[i].y - self.m_vCenter.y))
			currentDepth  = abs(int(pVertices[i].z - self.m_vCenter.z))

			# Check if the current width value is greater than the max width stored.
			if currentWidth > maxWidth:
				maxWidth = currentWidth

			# Check if the current height value is greater than the max height stored.
			if currentHeight > maxHeight:
				maxHeight = currentHeight

			# Check if the current depth value is greater than the max depth stored.
			if currentDepth > maxDepth:
				maxDepth  = currentDepth

		# Set the member variable dimensions to the max ones found.
		# We multiply the max dimensions by 2 because this will give us the
		# full width, height and depth.  Otherwise, we just have half the size
		# because we are calculating from the center of the scene.
		maxWidth *= 2.0
		maxHeight *= 2.0
		maxDepth *= 2.0
		
		# Check if the width is the highest value and assign that for the cube dimension
		if maxWidth > maxHeight and maxWidth > maxDepth:
			self.m_Width = maxWidth

		# Check if the height is the heighest value and assign that for the cube dimension
		elif maxHeight > maxWidth and maxHeight > maxDepth:
			self.m_Width = maxHeight

		# Else it must be the depth or it's the same value as some of the other ones
		else:
			self.m_Width = maxDepth


	def CreateNewNode(self, pVertices, pList, g_NumberOfVerts, vCenter, width, triangleCount, nodeID):
		# This function helps us set up the new node that is being created.  We only
		# want to create a new node if it found triangles in it's area.  If there were
		# no triangle found in this node's cube, then we ignore it and don't create a node.

		# Check if the first node found some triangles in it
		if triangleCount:
			# Allocate memory for the triangles found in this node (tri's * 3 for vertices)
			pNodeVertices = []

			# Go through all the vertices and assign the vertices to the node's list
			for i in xrange(g_NumberOfVerts):
				# If this current triangle is in the node, assign it's vertices to it
				if pList[i/3]:
					pNodeVertices.append(pVertices[i])

			# Now comes the initialization of the node.  First we allocate memory for
			# our node and then get it's center point.  Depending on the nodeID, 
			# GetNewNodeCenter() knows which center point to pass back (TOP_LEFT_FRONT, etc..)

			# Allocate a new node for this octree
			self.m_pOctreeNodes[nodeID] = COctree()

			# Get the new node's center point depending on the nodexIndex (which of the 8 subdivided cubes).
			vNodeCenter = self.GetNewNodeCenter(vCenter, width, nodeID)
			
			# Below, before and after we recurse further down into the tree, we keep track
			# of the level of subdivision that we are in.  This way we can restrict it.

			# Increase the current level of subdivision
			COctree.g_CurrentSubdivision += 1

			# Recurse through this node and subdivide it if necessary
			self.m_pOctreeNodes[nodeID].CreateNode(pNodeVertices, triangleCount * 3, vNodeCenter, width/2.0)

			# Decrease the current level of subdivision
			COctree.g_CurrentSubdivision -= 1


	def CreateNode(self, pVertices, g_NumberOfVerts, vCenter, width):
		# This is our main function that creates the octree.  We will recurse through
		# this function until we finish subdividing.  Either this will be because we
		# subdivided too many levels or we divided all of the triangles up.

		# Create a variable to hold the number of triangles
		numberOfTriangles = g_NumberOfVerts / 3

		# Initialize this node's center point.  Now we know the center of this node.
		self.m_vCenter = vCenter

		# Initialize this nodes cube width.  Now we know the width of this current node.
		self.m_Width = width

		# Add the current node to our debug rectangle list so we can visualize it.
		# We can now see this node visually as a cube when we render the rectangles.
		# Since it's a cube we pass in the width for width, height and depth.
		self.debug.AddDebugRectangle(vCenter, width, width, width)	
		# Check if we have too many triangles in this node and we haven't subdivided
		# above our max subdivisions.  If so, then we need to break this node into
		# 8 more nodes (hence the word OCTree).  Both must be True to divide this node.
		if (numberOfTriangles > self.g_MaxTriangles)  and  (self.g_CurrentSubdivision < self.g_MaxSubdivisions):
			# Since we need to subdivide more we set the divided flag to True.
			# This let's us know that this node does NOT have any vertices assigned to it,
			# but nodes that perhaps have vertices stored in them (Or their nodes, etc....)
			# We will querey this variable when we are drawing the octree.
			m_bSubDivided = True

			# Create a list for each new node to store if a triangle should be stored in it's
			# triangle list.  For each index it will be a True or false to tell us if that triangle
			# is in the cube of that node.  Below we check every point to see where it's
			# position is from the center (I.E. if it's above the center, to the left and 
			# back it's the TOP_LEFT_BACK node).  Depending on the node we set the pList 
			# index to True.  This will tell us later which triangles go to which node.
			# You might catch that this way will produce doubles in some nodes.  Some
			# triangles will intersect more than 1 node right?  We won't split the triangles
			# in this tutorial just to keep it simple, but the next tutorial we will.

			# Create the list of booleans for each triangle index
			pList1 = []
			pList2 = []
			pList3 = []
			pList4 = []
			pList5 = []
			pList6 = []
			pList7 = []
			pList8 = []

			for i in xrange(numberOfTriangles):
				pList1.append(False)	 # TOP_LEFT_FRONT node list
				pList2.append(False)	 # TOP_LEFT_BACK node list
				pList3.append(False)	 # TOP_RIGHT_BACK node list
				pList4.append(False)	 # TOP_RIGHT_FRONT node list
				pList5.append(False)	 # BOTTOM_LEFT_FRONT node list
				pList6.append(False)	 # BOTTOM_LEFT_BACK node list
				pList7.append(False)	 # BOTTOM_RIGHT_BACK node list
				pList8.append(False)	 # BOTTOM_RIGHT_FRONT node list
		
			# Go through all of the vertices and check which node they belong too.  The way
			# we do this is use the center of our current node and check where the point
			# lies in relationship to the center.  For instance, if the point is 
			# above, left and back from the center point it's the TOP_LEFT_BACK node.
			# You'll see we divide by 3 because there are 3 points in a triangle.
			# If the vertex index 0 and 1 are in a node, 0 / 3 and 1 / 3 is 0 so it will
			# just set the 0'th index to TRUE twice, which doesn't hurt anything.  When
			# we get to the 3rd vertex index of pVertices[] it will then be checking the
			# 1st index of the pList*[] array.  We do this because we want a list of the
			# triangles in the node, not the vertices.
			for i in xrange(g_NumberOfVerts):
				# Create some variables to cut down the thickness of the code (easier to read)
				vPoint = pVertices[i]

				# Check if the point lines within the TOP LEFT FRONT node
				if (vPoint.x <= vCenter.x) and (vPoint.y >= vCenter.y) and (vPoint.z >= vCenter.z):
					pList1[i / 3] = True

				# Check if the point lines within the TOP LEFT BACK node
				if (vPoint.x <= vCenter.x) and (vPoint.y >= vCenter.y) and (vPoint.z <= vCenter.z):
					pList2[i / 3] = True

				# Check if the point lines within the TOP RIGHT BACK node
				if (vPoint.x >= vCenter.x) and (vPoint.y >= vCenter.y) and (vPoint.z <= vCenter.z):
					pList3[i / 3] = True

				# Check if the point lines within the TOP RIGHT FRONT node
				if (vPoint.x >= vCenter.x) and (vPoint.y >= vCenter.y) and (vPoint.z >= vCenter.z):
					pList4[i / 3] = True

				# Check if the point lines within the BOTTOM LEFT FRONT node
				if (vPoint.x <= vCenter.x) and (vPoint.y <= vCenter.y) and (vPoint.z >= vCenter.z):
					pList5[i / 3] = True

				# Check if the point lines within the BOTTOM LEFT BACK node
				if (vPoint.x <= vCenter.x) and (vPoint.y <= vCenter.y) and (vPoint.z <= vCenter.z):
					pList6[i / 3] = True

				# Check if the point lines within the BOTTOM RIGHT BACK node
				if (vPoint.x >= vCenter.x) and (vPoint.y <= vCenter.y) and (vPoint.z <= vCenter.z):
					pList7[i / 3] = True

				# Check if the point lines within the BOTTOM RIGHT FRONT node
				if (vPoint.x >= vCenter.x) and (vPoint.y <= vCenter.y) and (vPoint.z >= vCenter.z):
					pList8[i / 3] = True

			# Here we create a variable for each list that holds how many triangles
			# were found for each of the 8 subdivided nodes.
			triCount1 = triCount2 = triCount3 = triCount4 = triCount5 = triCount6 = triCount7 = triCount8 = 0
			
			# Go through each of the lists and increase the triangle count for each node.
			for i in xrange(numberOfTriangles):  
				# Increase the triangle count for each node that has a "True" for the index i.
				
				if pList1[i]:
					triCount1 += 1
				if pList2[i]:
					triCount2 += 1
				if pList3[i]:
					triCount3 += 1
				if pList4[i]:
					triCount4 += 1
				if pList5[i]:
					triCount5 += 1
				if pList6[i]:
					triCount6 += 1
				if pList7[i]:
					triCount7 += 1
				if pList8[i]:
					triCount8 += 1
		
			# Next we do the dirty work.  We need to set up the new nodes with the triangles
			# that are assigned to each node, along with the new center point of the node.
			# Through recursion we subdivide this node into 8 more nodes.

			# Create the subdivided nodes if necessary and then recurse through them.
			# The information passed into CreateNewNode() are essential for creating the
			# new nodes.  We pass the 8 ID's in so it knows how to calculate it's new center.

			self.CreateNewNode(pVertices, pList1, g_NumberOfVerts, vCenter, width, triCount1, 0)
			self.CreateNewNode(pVertices, pList2, g_NumberOfVerts, vCenter, width, triCount2, 1)
			self.CreateNewNode(pVertices, pList3, g_NumberOfVerts, vCenter, width, triCount3, 2)
			self.CreateNewNode(pVertices, pList4, g_NumberOfVerts, vCenter, width, triCount4, 3)
			self.CreateNewNode(pVertices, pList5, g_NumberOfVerts, vCenter, width, triCount5, 4)
			self.CreateNewNode(pVertices, pList6, g_NumberOfVerts, vCenter, width, triCount6, 5)
			self.CreateNewNode(pVertices, pList7, g_NumberOfVerts, vCenter, width, triCount7, 6)
			self.CreateNewNode(pVertices, pList8, g_NumberOfVerts, vCenter, width, triCount8, 7)
		else:
			# If we get here we must either be subdivided past our max level, or our triangle
			# count went below the minimum amount of triangles so we need to store them.
			
			# Assign the vertices to this node since we reached the end node.
			# This will be the end node that actually gets called to be drawn.
			# We just pass in the vertices and vertex count to be assigned to this node.
			self.AssignVerticesToNode(pVertices, g_NumberOfVerts)

	def AssignVerticesToNode(self, pVertices, g_NumberOfVerts):
		# Since we did not subdivide this node we want to set our flag to false
		self.m_bSubDivided = False

		# Initialize the triangle count of this end node (total verts / 3 = total triangles)
		self.m_TriangleCount = g_NumberOfVerts / 3

		# Copy the passed in vertex data over to our node vertice data
		self.m_pVertices = pVertices

		# Increase the amount of end nodes created (Nodes with vertices stored)
		self.g_EndNodeCount += 1

	# This goes through each of the nodes and then draws the end nodes vertices.
	# This function should be called by starting with the root node.
	def DrawOctree(self, pNode):
		# We should already have the octree created before we call this function.
		# This only goes through the nodes that are in our frustum, then renders those
		# vertices stored in their end nodes.  Before we draw a node we check to
		# make sure it is a subdivided node (from m_bSubdivided).  If it is, then
		# we haven't reaches the end and we need to keep recursing through the tree.
		# Once we get to a node that isn't subdivided we draw it's vertices.

		# Make sure a valid node was passed in, otherwise go back to the last node
		if not pNode:
			return

		# Before we do any checks with the current node, let's make sure we even need too.
		# We want to check if this node's cube is even in our frustum first.
		# To do that we pass in our center point of the node and 1/2 it's width to our 
		# CubeInFrustum() function.  This will return "True" if it is inside the frustum 
		# (camera's view), otherwise return false.  
		#elif(g_Frustum.CubeInFrustum(pNode.m_vCenter.x, pNode.m_vCenter.y, pNode.m_vCenter.z, pNode.m_Width / 2) or 1):
		else:			# Check if this node is subdivided. If so, then we need to recurse and draw it's nodes
			if pNode.IsSubDivided():
				# Recurse to the bottom of these nodes and draw the end node's vertices
				# Like creating the octree, we need to recurse through each of the 8 nodes.
				DrawOctree(pNode.m_pOctreeNodes[0])
				DrawOctree(pNode.m_pOctreeNodes[1])
				DrawOctree(pNode.m_pOctreeNodes[2])
				DrawOctree(pNode.m_pOctreeNodes[3])
				DrawOctree(pNode.m_pOctreeNodes[4])
				DrawOctree(pNode.m_pOctreeNodes[5])
				DrawOctree(pNode.m_pOctreeNodes[6])
				DrawOctree(pNode.m_pOctreeNodes[7])
			else:
				# Increase the amount of nodes in our viewing frustum (camera's view)
				self.g_TotalNodesDrawn += 1

				# Make sure we have valid vertices assigned to this node
				if not pNode.m_pVertices:
					return

				# Render the world data with triangles
				glBegin(GL_TRIANGLES)

				# Turn the polygons green
				glColor3ub(0, 255, 0)


				# Go through all of the vertices (the number of triangles * 3)
				i = 0
				while i < pNode.GetTriangleCount() * 3:
					# Before we render the vertices we want to calculate the face normal
					# of the current polygon.  That way when lighting is turned on we can
					# see the definition of the terrain more clearly.  In reality you wouldn't do this.
					
					# Here we get a vector from each side of the triangle
					vVector1 = pVertices[i + 1] - pVertices[i]
					vVector2 = pVertices[i + 2] - pVertices[i]
					
					# Haxx instead of the two upper lines
					vVector1 = (vertices[i+1].x - vertices[i].x, vertices[i+1].y - vertices[i].y, vertices[i+1].z - vertices[i].z)
					vVector2 = (vertices[i+2].x - vertices[i].x, vertices[i+2].y - vertices[i].y, vertices[i+2].z - vertices[i].z)

					# Then we need to get the cross product of those 2 vectors (The normal's direction)
					vNormal = Cross(vVector1, vVector2)

					# Now we normalize the normal so it is a unit vector (length of 1)
					vNormal = Normalize(vNormal)

					# Pass in the normal for this triangle so we can see better depth in the scene
					glNormal3f(vNormal.x, vNormal.y, vNormal.z)

					# Render the first point in the triangle
					glVertex3f(pVertices[i].x, pVertices[i].y, pVertices[i].z)

					# Render the next point in the triangle
					glVertex3f(pVertices[i + 1].x, pVertices[i + 1].y, pVertices[i + 1].z)

					# Render the last point in the triangle to form the current triangle
					glVertex3f(pVertices[i + 2].x, pVertices[i + 2].y, pVertices[i + 2].z)

					i += 3

				# Quit Drawing
				glEnd()

	def DestroyOctree(self):
		# Free the triangle data if it's not NULL
		if self.m_pVertices:
			self.m_pVertices = CVector3(0.0, 0.0, 0.0)

		# Go through all of the nodes and free them if they were allocated
		for i in xrange(8):
			# Make sure this node is valid
			if self.m_pOctreeNodes[i]:
				# Free this array index.  This will call the deconstructor which will
				# free the octree data correctly.  This allows us to forget about it's clean up
				self.m_pOctreeNodes[i] = CVector3(0, 0, 0)
				#self.m_pOctreeNodes[i] = None

		self.m_Width = 0.0
		self.m_bSubDivided = False
		self.m_TriangleCount = 0

