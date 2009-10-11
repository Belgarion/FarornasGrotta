#!/usr/bin/python
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL import GL
from OpenGL import GLU
from Global import Global
from debug import * 


# The current amount of end nodes in our tree (The nodes with vertices stored in them)
g_EndNodeCount = 0

# This stores the amount of nodes that are in the frustum
g_TotalNodesDrawn = 0

# The maximum amount of triangles per node.  If a node has equal or less 
# than this, stop subdividing and store the face indices in that node
g_MaxTriangles = 1000

# The maximum amount of subdivisions allow (Levels of subdivision)
g_MaxSubdivisions = 4

# This holds the current amount of subdivisions we are currently at.
# This is used to make sure we don't go over the max amount
g_CurrentSubdivision = 0

# This holds if we want rendered or wire frame mode
g_bRenderMode = 0

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
	
	def __init__(self):
		# This tells us if we want to display the yellow debug lines for our nodes
		self.g_bDisplayNodes = 0

		# These values (0 - 7) store the index ID's for the octree node array (m_pOctreeNodes)
		self.eOctreeNodes = [TOP_LEFT_FRONT, TOP_LEFT_BACK, TOP_RIGHT_BACK, TOP_RIGHT_FRONT, BOTTOM_LEFT_FRONT, BOTTOM_LEFT_BACK, BOTTOM_RIGHT_BACK, BOTTOM_RIGHT_FRONT] = range(8)
	

		# This stores the total fave count that is in the nodes 3D space (how many "true"'s)
		self.totalFaceCount = 0



		# This tells us if we have divided this node into more sub nodes
		self.m_bSubDivided = False

		# This is the size of the cube for this current node
		self.m_Width = 0.0

		# This holds the amount of triangles stored in this node
		self.m_TriangleCount = 0

		# This is the center (X, Y, Z) point in this node
		self.m_vCenter = CVector3(0, 0, 0)

		# This stores the triangles that should be drawn with this node
		self.m_pVertices = CVector3(0, 0, 0)

		# These are the eight nodes branching down from this current node
		self.m_pOctreeNodes = []
		for i in xrange(8):
			self.m_pOctreeNodes.append(CVector3(0, 0, 0))

	def __del__(self):
		pass

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
	def GetNewNodeCenter(self, vCenter, width, nodeID):
		# Initialize the new node center
		vNodeCenter = CVector3(0, 0, 0)

		eOctreeNodes = [TOP_LEFT_FRONT, TOP_LEFT_BACK, TOP_RIGHT_BACK, TOP_RIGHT_FRONT, BOTTOM_LEFT_FRONT, BOTTOM_LEFT_BACK, BOTTOM_RIGHT_BACK, BOTTOM_RIGHT_FRONT] = range(8)

		if nodeID == eOctreeNodes[TOP_LEFT_FRONT]:
			vNodeCenter = CVector3(vCenter.x - width/4, vCenter.y + width/4, vCenter.z + width/4)

		if nodeID == eOctreeNodes[TOP_LEFT_BACK]:
			vNodeCenter = CVector3(vCenter.x - width/4, vCenter.y + width/4, vCenter.z - width/4)

		if nodeID == eOctreeNodes[TOP_RIGHT_BACK]:
			vNodeCenter = CVector3(vCenter.x + width/4, vCenter.y + width/4, vCenter.z - width/4)

		if nodeID == eOctreeNodes[TOP_RIGHT_FRONT]:
			vNodeCenter = CVector3(vCenter.x + width/4, vCenter.y + width/4, vCenter.z + width/4)

		if nodeID == eOctreeNodes[BOTTOM_LEFT_FRONT]:
			vNodeCenter = CVector3(vCenter.x - width/4, vCenter.y - width/4, vCenter.z + width/4)

		if nodeID == eOctreeNodes[BOTTOM_LEFT_BACK]:
			vNodeCenter = CVector3(vCenter.x - width/4, vCenter.y - width/4, vCenter.z - width/4)

		if nodeID == eOctreeNodes[BOTTOM_RIGHT_BACK]:
			vNodeCenter = CVector3(vCenter.x + width/4, vCenter.y - width/4, vCenter.z - width/4)

		if nodeID == eOctreeNodes[BOTTOM_RIGHT_FRONT]:
			vNodeCenter = CVector3(vCenter.x + width/4, vCenter.y - width/4, vCenter.z + width/4)

		return vNodeCenter


	# This sets the initial width, height and depth for the whole scene
	def GetSceneDimensions(self,pVertices, numberOfVerts):
		# Initialize some temporary variables to hold the max dimensions found
		maxWidth = maxHeight = maxDepth = 0.0

		# Return from this function if we passed in bad data
		if(not pVertices or numberOfVerts <= 0):
			return

		# Go through all of the vertices and add them up to eventually find the center
		m_vCenter = CVector3(0, 0, 0)
		for i in xrange(numberOfVerts):
			# Add the current vertex to the center variable (Using operator overloading)
			m_vCenter = m_vCenter + pVertices[i]

		# Divide the total by the number of vertices to get the center point.
		# We could have overloaded the / symbol but I chose not to because we rarely use it.
		m_vCenter.x /= numberOfVerts
		m_vCenter.y /= numberOfVerts
		m_vCenter.z /= numberOfVerts

		# Go through all of the vertices and find the max dimensions
		for i in xrange(numberOfVerts):
			# Get the current dimensions for this vertex.  We use the abs() function
			# to get the absolute value because it might return a negative number.
			currentWidth  = abs(int(pVertices[i][0] - m_vCenter.x))
			currentHeight = abs(int(pVertices[i][1] - m_vCenter.y))
			currentDepth  = abs(int(pVertices[i][2] - m_vCenter.z))

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
		maxWidth = maxHeigh = maxDepth = maxDepth*2

		# Check if the width is the highest value and assign that for the cube dimension
		if maxWidth > maxHeight and maxWidth > maxDepth:
			self.m_Width = maxWidth

		# Check if the height is the heighest value and assign that for the cube dimension
		elif maxHeight > maxWidth and maxHeight > maxDepth:
			self.m_Width = maxHeight

		# Else it must be the depth or it's the same value as some of the other ones
		else:
			self.m_Width = maxDepth


	def CreateNewNode(self, pVertices, pList, numberOfVerts, vCenter, width, triangleCount, nodeID):
		# This function helps us set up the new node that is being created.  We only
		# want to create a new node if it found triangles in it's area.  If there were
		# no triangle found in this node's cube, then we ignore it and don't create a node.

		# Check if the first node found some triangles in it
		if triangleCount:
			# Allocate memory for the triangles found in this node (tri's * 3 for vertices)
			pNodeVertices = []

			# Create an counter to count the current index of the new node vertices

			# Go through all the vertices and assign the vertices to the node's list
			for i in xrange(numberOfVerts):
				# If this current triangle is in the node, assign it's vertices to it
				if pList[i/3]:
					pNodeVertices.append(pVertices[i])

			# Now comes the initialization of the node.  First we allocate memory for
			# our node and then get it's center point.  Depending on the nodeID, 
			# GetNewNodeCenter() knows which center point to pass back (TOP_LEFT_FRONT, etc..)

			# Allocate a new node for this octree
			self.m_pOctreeNodes[nodeID] = COctree

			# Get the new node's center point depending on the nodexIndex (which of the 8 subdivided cubes).
			vNodeCenter = self.GetNewNodeCenter(vCenter, width, nodeID)
			
			# Below, before and after we recurse further down into the tree, we keep track
			# of the level of subdivision that we are in.  This way we can restrict it.

			# Increase the current level of subdivision
			global g_CurrentSubdivision 
			g_CurrentSubdivision += 1

			# Recurse through this node and subdivide it if necessary
			self.m_pOctreeNodes[nodeID].CreateNode(self, pNodeVertices, triangleCount * 3, vNodeCenter, width / 2)

			# Decrease the current level of subdivision
			g_CurrentSubdivision -= 1


	def CreateNode(self, pVertices, numberOfVerts, vCenter, width):
		print "HEJ"
		# This is our main function that creates the octree.  We will recurse through
		# this function until we finish subdividing.  Either this will be because we
		# subdivided too many levels or we divided all of the triangles up.

		# Create a variable to hold the number of triangles
		numberOfTriangles = numberOfVerts / 3

		# Initialize this node's center point.  Now we know the center of this node.
		m_vCenter = vCenter

		# Initialize this nodes cube width.  Now we know the width of this current node.
		m_Width = width

		# Add the current node to our debug rectangle list so we can visualize it.
		# We can now see this node visually as a cube when we render the rectangles.
		# Since it's a cube we pass in the width for width, height and depth.
		print vCenter.x,vCenter.y,vCenter.z, width, width, width
		Global.g_Debug.AddDebugRectangle(vCenter, width, width, width)

		# Check if we have too many triangles in this node and we haven't subdivided
		# above our max subdivisions.  If so, then we need to break this node into
		# 8 more nodes (hence the word OCTree).  Both must be True to divide this node.
		if numberOfTriangles > g_MaxTriangles  and  g_CurrentSubdivision < g_MaxSubdivisions:
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
			pList1 = []	 # TOP_LEFT_FRONT node list
			pList2 = []	 # TOP_LEFT_BACK node list
			pList3 = []	 # TOP_RIGHT_BACK node list
			pList4 = []	 # TOP_RIGHT_FRONT node list
			pList5 = []	 # BOTTOM_LEFT_FRONT node list
			pList6 = []	 # BOTTOM_LEFT_BACK node list
			pList7 = []	 # BOTTOM_RIGHT_BACK node list
			pList8 = []	 # BOTTOM_RIGHT_FRONT node list
		
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
			for i in xrange(numberOfVerts):
				# Create some variables to cut down the thickness of the code (easier to read)
				vPoint = pVertices[i]

				# Check if the point lines within the TOP LEFT FRONT node
				if vPoint[0] <= vCenter.x and vPoint[1] >= vCenter.y and vPoint[2] >= vCenter.z:
					pList1.append(True)
				else:
					pList1.append(False)

				# Check if the point lines within the TOP LEFT BACK node
				if vPoint[0] <= vCenter.x and vPoint[1] >= vCenter.y and vPoint[2] <= vCenter.z:
					pList2.append(True)
				else:
					pList2.append(False)

				# Check if the point lines within the TOP RIGHT BACK node
				if vPoint[0] >= vCenter.x and vPoint[1] >= vCenter.y and vPoint[2] <= vCenter.z:
					pList3.append(True)
				else:
					pList3.append(False)

				# Check if the point lines within the TOP RIGHT FRONT node
				if vPoint[0] >= vCenter.x and vPoint[1] >= vCenter.y and vPoint[2] >= vCenter.z:
					pList4.append(True)
				else:
					pList4.append(False)

				# Check if the point lines within the BOTTOM LEFT FRONT node
				if vPoint[0] <= vCenter.x and vPoint[1] <= vCenter.y and vPoint[2] >= vCenter.z:
					pList5.append(True)
				else:
					pList5.append(False)

				# Check if the point lines within the BOTTOM LEFT BACK node
				if vPoint[0] <= vCenter.x and vPoint[1] <= vCenter.y and vPoint[2] <= vCenter.z:
					pList6.append(True)
				else:
					pList6.append(False)

				# Check if the point lines within the BOTTOM RIGHT BACK node
				if vPoint[0] >= vCenter.x and vPoint[1] <= vCenter.y and vPoint[2] <= vCenter.z:
					pList7.append(True)
				else:
					pList7.append(False)

				# Check if the point lines within the BOTTOM RIGHT FRONT node
				if vPoint[0] >= vCenter.x and vPoint[1] <= vCenter.y and vPoint[2] >= vCenter.z:
					pList8.append(True)
				else:
					pList8.append(False)


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

			eOctreeNodes = [TOP_LEFT_FRONT, TOP_LEFT_BACK, TOP_RIGHT_BACK, TOP_RIGHT_FRONT, BOTTOM_LEFT_FRONT, BOTTOM_LEFT_BACK, BOTTOM_RIGHT_BACK, BOTTOM_RIGHT_FRONT] = range(8)

			self.CreateNewNode(pVertices, pList1, numberOfVerts, vCenter, width, triCount1, eOctreeNodes[TOP_LEFT_FRONT])
			self.CreateNewNode(pVertices, pList2, numberOfVerts, vCenter, width, triCount2, eOctreeNodes[TOP_LEFT_BACK])
			self.CreateNewNode(pVertices, pList3, numberOfVerts, vCenter, width, triCount3, eOctreeNodes[TOP_RIGHT_BACK])
			self.CreateNewNode(pVertices, pList4, numberOfVerts, vCenter, width, triCount4, eOctreeNodes[TOP_RIGHT_FRONT])
			self.CreateNewNode(pVertices, pList5, numberOfVerts, vCenter, width, triCount5, eOctreeNodes[BOTTOM_LEFT_FRONT])
			self.CreateNewNode(pVertices, pList6, numberOfVerts, vCenter, width, triCount6, eOctreeNodes[BOTTOM_LEFT_BACK])
			self.CreateNewNode(pVertices, pList7, numberOfVerts, vCenter, width, triCount7, eOctreeNodes[BOTTOM_RIGHT_BACK])
			self.CreateNewNode(pVertices, pList8, numberOfVerts, vCenter, width, triCount8, eOctreeNodes[BOTTOM_RIGHT_FRONT])
		else:
			# If we get here we must either be subdivided past our max level, or our triangle
			# count went below the minimum amount of triangles so we need to store them.
			
			# Assign the vertices to this node since we reached the end node.
			# This will be the end node that actually gets called to be drawn.
			# We just pass in the vertices and vertex count to be assigned to this node.
			self.AssignVerticesToNode(pVertices, numberOfVerts)

	def AssignVerticesToNode(self, pVertices, numberOfVerts):
		# Since we did not subdivide this node we want to set our flag to false
		m_bSubDivided = False

		# Initialize the triangle count of this end node (total verts / 3 = total triangles)
		m_TriangleCount = numberOfVerts / 3

		# Copy the passed in vertex data over to our node vertice data
		m_pVertices = pVertices

		# Increase the amount of end nodes created (Nodes with vertices stored)
		global g_EndNodeCount
		g_EndNodeCount += 1

	# This goes through each of the nodes and then draws the end nodes vertices.
	# This function should be called by starting with the root node.
	def DrawOctree(self, pNode):
		# We should already have the octree created before we call this function.
		# This only goes through the nodes that are in our frustum, then renders those
		#vertices stored in their end nodes.  Before we draw a node we check to
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
		else:			# Check if this node is subdivided. If so, then we need to recurse and draw it's nodes
			if pNode.IsSubDivided():
				# Recurse to the bottom of these nodes and draw the end node's vertices
				# Like creating the octree, we need to recurse through each of the 8 nodes.
				DrawOctree(pNode.m_pOctreeNodes[eOctreeNodes[TOP_LEFT_FRONT]]);
				DrawOctree(pNode.m_pOctreeNodes[eOctreeNodes[TOP_LEFT_BACK]]);
				DrawOctree(pNode.m_pOctreeNodes[eOctreeNodes[TOP_RIGHT_BACK]]);
				DrawOctree(pNode.m_pOctreeNodes[eOctreeNodes[TOP_RIGHT_FRONT]]);
				DrawOctree(pNode.m_pOctreeNodes[eOctreeNodes[BOTTOM_LEFT_FRONT]]);
				DrawOctree(pNode.m_pOctreeNodes[eOctreeNodes[BOTTOM_LEFT_BACK]]);
				DrawOctree(pNode.m_pOctreeNodes[eOctreeNodes[BOTTOM_RIGHT_BACK]]);
				DrawOctree(pNode.m_pOctreeNodes[eOctreeNodes[BOTTOM_RIGHT_FRONT]]);
			else:
				# Increase the amount of nodes in our viewing frustum (camera's view)
				global g_TotalNodesDrawn				
				g_TotalNodesDrawn += 1

				# Make sure we have valid vertices assigned to this node
				if not pNode.m_pVertices:
					return

				# Render the world data with triangles
				glBegin(GL_TRIANGLES);

				# Turn the polygons green
				glColor3ub(0, 255, 0);

				# Store the vertices in a local pointer to keep code more clean
				pVertices = pNode.m_pVertices;

				# Go through all of the vertices (the number of triangles * 3)
				i = 0
				while i < pNode.GetTriangleCount() * 3:
					# Before we render the vertices we want to calculate the face normal
					# of the current polygon.  That way when lighting is turned on we can
					# see the definition of the terrain more clearly.  In reality you wouldn't do this.
					
					# Here we get a vector from each side of the triangle
					vVector1 = pVertices[i + 1] - pVertices[i]
					vVector2 = pVertices[i + 2] - pVertices[i]

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
				glEnd();



