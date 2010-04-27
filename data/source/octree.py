#!/usr/bin/python
# python Octree v.1

# UPDATED:
# Is now more like a true octree (ie: partitions space containing objects)

# Important Points to remember:
# The OctNode positions do not correspond to any object position
# rather they are seperate containers which may contain objects
# or other nodes.

# An OctNode which which holds less objects than MAX_OBJECTS_PER_CUBE
# is a LeafNode; it has no branches, but holds a list of objects contained within
# its boundaries. The list of objects is held in the leafNode's 'data' property

# If more objects are added to an OctNode, taking the object count over MAX_OBJECTS_PER_CUBE
# Then the cube has to subdivide itself, and arrange its objects in the new child nodes.
# The new octNode itself contains no objects, but its children should.

# TODO: Add support for multi-threading for node insertion and/or searching

#### Global Variables ####

# This defines the maximum objects an LeafNode can hold, before it gets subdivided again.
MAX_OBJECTS_PER_CUBE = 7

# This dictionary is used by the findBranch function, to return the correct branch index
DIRLOOKUP = {"3":0, "2":1, "-2":2, "-1":3, "1":4, "0":5, "-4":6, "-3":7}

#### End Globals ####

class Debug:
	def __init__(self):
		self.debugLines = []

	# This adds a rectangle with a given center,
	# width, height and depth to our list
	def addDebugRectangle(self, center, width, height, depth):
		# So we can work with the code better, we divide the dimensions in half.
		# That way we can create the cube from the center outwards.
		width /= 2.0
		height /= 2.0
		depth /= 2.0

		# Below we create all the 8 points so it will be easier to input
		# the lines of the cube.
		# With the dimensions we calculate the points.
		TopLeftFront = (center[0]-width, center[1]+height, center[2]+depth)
		TopLeftBack = (center[0]-width, center[1]+height, center[2]-depth)
		TopRightBack = (center[0]+width, center[1]+height, center[2]-depth)
		TopRightFront = (center[0]+width, center[1]+height, center[2]+depth)
		BottomLeftFront = (center[0]-width, center[1]-height, center[2]+depth)
		BottomLeftBack = (center[0]-width, center[1]-height, center[2]-depth)
		BottomRightBack = (center[0]+width, center[1]-height, center[2]-depth)
		BottomRightFront = (center[0]+width, center[1]-height, center[2]+depth)

		## TOP LINES
		self.debugLines.append(TopLeftFront)
		self.debugLines.append(TopRightFront)
		self.debugLines.append(TopLeftBack)
		self.debugLines.append(TopRightBack)
		#self.debugLines.append(TopLeftFront)
		#self.debugLines.append(TopLeftBack)
		#self.debugLines.append(TopRightFront)
		#self.debugLines.append(TopRightBack)

		## BOTTOM LINES
		self.debugLines.append(BottomLeftFront)
		self.debugLines.append(BottomRightFront)
		self.debugLines.append(BottomLeftBack)
		self.debugLines.append(BottomRightBack)
		#self.debugLines.append(BottomLeftFront)
		#self.debugLines.append(BottomLeftBack)
		#self.debugLines.append(BottomRightFront)
		#self.debugLines.append(BottomRightBack)

		## SIDE LINES
		self.debugLines.append(TopLeftFront)
		self.debugLines.append(BottomLeftFront)
		self.debugLines.append(TopLeftBack)
		self.debugLines.append(BottomLeftBack)
		#self.debugLines.append(TopRightBack)
		#self.debugLines.append(BottomRightBack)
		#self.debugLines.append(TopRightFront)
		#self.debugLines.append(BottomRightFront)


class OctNode:
	# New Octnode Class, can be appended to as well i think
	def __init__(self, position, size, data):
		# OctNode Cubes have a position and size
		# position is related to, but not the same as the objects the node contains.
		self.position = position
		self.size = size

		# All OctNodes will be leaf nodes at first
		# Then subdivided later as more objects get added
		self.isLeafNode = True

		# store our object, typically this will be one, but maybe more
		self.data = data

		# might as well give it some emtpy branches while we are here.
		self.branches = [None, None, None, None, None, None, None, None]

class Octree:
	def __init__(self, worldSize, main):
		# Init the world bounding root cube
		# all world geometry is inside this
		# it will first be created as a leaf node (ie, without branches)
		# this is because it has no objects, which is less than MAX_OBJECTS_PER_CUBE
		# if we insert more objects into it than MAX_OBJECTS_PER_CUBE, then it will subdivide itself.
		self.worldSize = worldSize
		self.main = main
		self.debugLines = 0

		self.debug = Debug()

		# Create the root-octree
		self.root = self.addNode((0.0, 0.0, 0.0), worldSize, [])

		# This will render it
		#self.debug.addDebugRectangle((0.0, 0.0, 0.0), worldSize, worldSize, worldSize)

	def checkCollision(self, root, position):
		pass
		#branch = self.findPosition(root, position)

	def addNode(self, position, size, objects):
		#self.debug.addDebugRectangle(position, size, size, size)

		# This creates the actual OctNode itself.
		return OctNode(position, size, objects)

	def insertNode(self, root, size, parent, objData):
		if root == None:
			# we're inserting a single object, so if we reach an empty node, insert it here
			# Our new node will be a leaf with one object, our object
			# More may be added later, or the node maybe subdivided if too many are added
			# Find the Real Geometric centre point of our new node:
			# Found from the position of the parent node supplied in the arguments
			pos = parent.position

			newSize = parent.size / 2

			# offset is halfway across the size allocated for this node
			offset = size / 2

			# find out which direction we're heading in
			branch = self.findBranch(parent, objData.position)

			newCenter = (0,0,0)
			if branch == 0:
				# left down back
				newCenter = (pos[0] + offset, pos[1] + offset, pos[2] + offset)

			elif branch == 1:
				# left down forwards
				newCenter = (pos[0] + offset, pos[1] + offset, pos[2] - offset)

			elif branch == 2:
				# right down forwards
				newCenter = (pos[0] + offset, pos[1] - offset, pos[2] + offset)

			elif branch == 3:
				# right down back
				newCenter = (pos[0] + offset, pos[1] - offset, pos[2] - offset)

			elif branch == 4:
				# left up back
				newCenter = (pos[0] - offset, pos[1] + offset, pos[2] + offset)

			elif branch == 5:
				# left up forward
				newCenter = (pos[0] - offset, pos[1] + offset, pos[2] - offset)

			elif branch == 6:
				# right up forward
				newCenter = (pos[0] - offset, pos[1] - offset, pos[2] + offset)

			elif branch == 7:
				# right up back
				newCenter = (pos[0] - offset, pos[1] - offset, pos[2] - offset)

			# Now we know the centre point of the new node
			# we already know the size as supplied by the parent node
			# So create a new node at this position in the tree
			#print "Adding Node of size: " + str(size / 2) + " at " + str(newCenter)
			return self.addNode(newCenter, size, [objData])

		#else: are we not at our position, but not at a leaf node either
		elif root.position != objData.position and root.isLeafNode == False:
			# we're in an octNode still, we need to traverse further
			branch = self.findBranch(root, objData.position)

			# Find the new scale we working with
			newSize = root.size / 2

			# Perform the same operation on the appropriate branch recursively
			root.branches[branch] = self.insertNode(root.branches[branch], newSize, root, objData)

		# else, is this node a leaf node with objects already in it?
		elif root.isLeafNode:
			# We've reached a leaf node. This has no branches yet, but does hold
			# some objects, at the moment, this has to be less objects than MAX_OBJECTS_PER_CUBE
			# otherwise this would not be a leafNode (elementary my dear watson).
			# if we add the node to this branch will we be over the limit?
			if len(root.data) < MAX_OBJECTS_PER_CUBE:
				# No? then Add to the Node's list of objects and we're done
				root.data.append(objData)

				# We can draw it too
				#self.debug.addDebugRectangle(objData.position, objData.width, objData.height, objData.depth)



			elif len(root.data) == MAX_OBJECTS_PER_CUBE:
				# Adding this object to this leaf takes us over the limit
				# So we have to subdivide the leaf and redistribute the objects
				# on the new children.
				# Add the new object to pre-existing list
				root.data.append(objData)

				# copy the list
				objList = root.data

				# Clear this node's data
				root.data = None

				# Its not a leaf node anymore
				root.isLeafNode = False

				# Calculate the size of the new children
				newSize = root.size / 2

				# distribute the objects on the new tree
				#print "Subdividing Node sized at: " + str(root.size) + " at " + str(root.position)
				for ob in objList:
					branch = self.findBranch(root, ob.position)
					root.branches[branch] = self.insertNode(root.branches[branch], newSize, root, ob)
		return root

	# Basic collision lookup that finds the leaf node wit a specified position
	# Returns the child objects of the leaf, or None if the leaf is empty
	def findPosition(self, root, position):
		if root == None:
			return None
		elif root.isLeafNode:
			return root.data
		else:
			branch = self.findBranch(root, position)
			return self.findPosition(root.branches[branch], position)

	def deletePosition(self, root, position, obj_to_delete):
		if root == None:
			return None
		elif root.isLeafNode:
			added = []
			for obj in root.data:
				if obj.id != obj_to_delete.id:
					added.append(obj)

			root.data = added
			return root.data
		else:
			branch = self.findBranch(root, position)
			return self.deletePosition(root.branches[branch], position, obj_to_delete)

	# Helper function  returns an index corresponding to a branch
	# pointing in the direction we want to go
	def findBranch(self, root, position):
		vec1 = root.position
		vec2 = position
		result = 0

		# Equation created by adding nodes with known branch directions
		# into the tree, and comparing results. See DIRLOOKUP above for the
		# corresponding return values and branch indices
		for i in range(3):
			if vec1[i] <= vec2[i]:
				result += (-4 / (i + 1) / 2)
			else:
				result += (4 / (i + 1) / 2)
		result = DIRLOOKUP[str(result)]
		return result

