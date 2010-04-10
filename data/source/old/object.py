import graphics
import uuid

class Data:
	def __init__(self):
		self.list = {}
		self.load_level("level1")

	def add_data(self, name):
		try: 
			self.list[name]
		except KeyError:
			vertices, vnormals, f, vertexCount = graphics.loadObj("data/model/"+name+".obj")
			verticesId, normalsId = graphics.createVBO(vertices, vnormals)
			self.list[name] = { "verticesId":verticesId, "vertexCount":vertexCount, "normalsId":normalsId }

	def load_level(self, name):
		f = open("data/level/" + name + ".lvl")

		objects_on_level=[]

		for line in f:
			if not line: continue
			if line[0] is "#": continue
			split = line.split(" ")
			if split[0] == "object":
				objects_on_level.append(split[1].replace("\n",""))
		for object in objects_on_level:
			self.add_data(object)

class Object:
	def __init__(self, type, name, position, orientation, scale, mass=1, \
			velocity=(0,0,0), id = None ):
		if id == None:
			id = str(uuid.uuid4().hex)
		self.id = id
		self.type = type
		self.name = name
		self.position = position
		self.orientation = orientation

		self.mass = mass
		self.velocity = velocity
		self.scale = scale

class ObjectManager:
	def __init__(self):
		self.objects = []
		#self.load_level("level1")

	def add_object(self, object, name, x, y, z, orientationx, orientationy, orientationz, scale): #could be better
		object = [object, name, (x,y,z), (orientationx, orientationy, orientationz), scale]
		self.objects.append(object)

	def load_level(self, name):
		f = open("data/level/" + name + ".lvl")
		objects = []
		for line in f:
			if not line: continue
			if line[0] is "#": continue
			split = line.split(" ")
			if split[0] == "spawn":
				pos = split[3].split(",")
				pos = (float(pos[0]), float(pos[1]), float(pos[2]))
				orientation = split[4].split(",")
				orientation = (float(orientation[0]), float(orientation[1]), float(orientation[2]))

				object = [split[1], split[2], (pos[0], pos[1], pos[2]), \
						(orientation[0], orientation[1], orientation[2]), float(split[5]]
				objects.append(object)


