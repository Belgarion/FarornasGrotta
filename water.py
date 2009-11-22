try:
	import numpy as Numeric
except:
	import Numeric
from OpenGL.GL import *
from OpenGL.GL.ARB.vertex_buffer_object import *
from OpenGL.GL.ARB.shader_objects import *
from OpenGL.GL.ARB.vertex_shader import *
import time

class Water:
	def __init__(self):
		meshVertices, self.vertexCount = self.generateMesh()
		self.verticesId = self.bindVBO(meshVertices)
		self.initShader()
		#
	def initShader(self):
		program = glCreateProgramObjectARB()
		vertexShader = glCreateShaderObjectARB(GL_VERTEX_SHADER_ARB)
		fragmentShader = glCreateShaderObjectARB(GL_FRAGMENT_SHADER_ARB)
		vertexSource = ["""
		uniform float time;
		void main() {
			gl_FrontColor = gl_Color;

			vec4 a = gl_Vertex;
			a.y = a.y + 2 * sin(a.x * 0.2 + time);

			gl_Position = gl_ModelViewProjectionMatrix * a;
		}
		"""]

		vertexSource = ["""
		uniform float time;

		varying vec4 diffuse, ambient, ambientGlobal;
		varying vec3 normal, lightDir, halfVector;
		varying float dist;

		void main() {
			vec4 ecPos;
			vec3 aux;

			/*normal = normalize(gl_NormalMatrix * gl_Normal);*/
			vec4 a = gl_Vertex;

			/*vec2 pos, n1, n2;
			pos.x = a.x
			pos.y = a.y
			n1.x = pos.x + 1.0*/

			a.y = a.y + sin(0.2 * a.x + time) * cos(0.2 * a.z + time) * 2;
			gl_Position = gl_ModelViewProjectionMatrix * a;

			ecPos = gl_ModelViewMatrix * gl_Vertex;
			aux = vec3(gl_LightSource[1].position - ecPos);
			lightDir = normalize(aux);
			dist = length(aux);

			halfVector = normalize(gl_LightSource[1].halfVector.xyz);

			diffuse = gl_FrontMaterial.diffuse * gl_LightSource[1].diffuse;
			ambient = gl_FrontMaterial.ambient * gl_LightSource[1].ambient;
			ambientGlobal = gl_LightModel.ambient * gl_FrontMaterial.ambient;

		}
		"""]
		fragmentSource = ["""
		varying vec4 diffuse, ambient, ambientGlobal;
		varying vec3 normal, lightDir, halfVector;
		varying float dist;

		void main() {
			/*vec3 n, halfV, viewV, ldir;
			float NdotL, NdotHV;
			vec4 color = ambientGlobal;
			float att;

			n = normalize(normal);

			NdotL = max(dot(n, normalize(lightDir)), 0.0);

			if (NdotL > 0.0) {
				att = 1.0 / (gl_LightSource[1].constantAttenuation +
								gl_LightSource[1].linearAttenuation * dist +
								gl_LightSource[1].quadraticAttenuation * dist * dist);
				color += att * (diffuse * NdotL + ambient);
				halfV = normalize(halfVector);
				NdotHV = max(dot(n, halfV), 0.0);
				color += att * gl_FrontMaterial.specular * gl_LightSource[1].specular * 
							pow(NdotHV, gl_FrontMaterial.shininess);
			}
			gl_FragColor = gl_Color;*/
			gl_FragColor[0] = gl_FragCoord[0] / 400.0;
			gl_FragColor[1] = gl_FragCoord[1] / 400.0;
			gl_FragColor[2] = 1.0;
		}
		"""]
		glShaderSourceARB(vertexShader, vertexSource)
		glShaderSourceARB(fragmentShader, fragmentSource)
	
		glCompileShaderARB(vertexShader)
		compiled = glGetObjectParameterivARB(vertexShader, GL_COMPILE_STATUS)
		if not compiled:
			print glGetInfoLogARB(vertexShader)

		glCompileShaderARB(fragmentShader)
		compiled = glGetObjectParameterivARB(fragmentShader, GL_COMPILE_STATUS)
		if not compiled:
			print glGetInfoLogARB(fragmentShader)
	
		glAttachObjectARB(program, vertexShader)
		glAttachObjectARB(program, fragmentShader)

		glValidateProgramARB(program)
		glLinkProgramARB(program)

		self.program = program
		#
	def generateMesh(self):
		nIndex = 0
		mesh = Numeric.zeros( (99*99*6, 3), 'f')
		for x in xrange(0,99):
			for z in xrange(0,99):
				mesh[nIndex, 0] = float(x)
				mesh[nIndex, 1] = 1.0
				mesh[nIndex, 2] = float(z)
				nIndex += 1

				mesh[nIndex, 0] = float(x+1)
				mesh[nIndex, 1] = 1.0
				mesh[nIndex, 2] = float(z)
				nIndex += 1

				mesh[nIndex, 0] = float(x+1)
				mesh[nIndex, 1] = 1.0
				mesh[nIndex, 2] = float(z+1)
				nIndex += 1

				##
				mesh[nIndex, 0] = float(x)
				mesh[nIndex, 1] = 1.0
				mesh[nIndex, 2] = float(z)
				nIndex += 1

				mesh[nIndex, 0] = float(x)
				mesh[nIndex, 1] = 1.0
				mesh[nIndex, 2] = float(z+1)
				nIndex += 1

				mesh[nIndex, 0] = float(x+1)
				mesh[nIndex, 1] = 1.0
				mesh[nIndex, 2] = float(z+1)
				nIndex += 1

		return (mesh, nIndex)
		#
	def bindVBO(self, vertices):
		verticesId = glGenBuffersARB(1)

		glBindBufferARB(GL_ARRAY_BUFFER_ARB, verticesId)
		glBufferDataARB(GL_ARRAY_BUFFER_ARB, vertices, GL_STATIC_DRAW_ARB)

		glBindBufferARB(GL_ARRAY_BUFFER_ARB, 0)

		return verticesId
		#
	def draw(self):
		glPushMatrix()

		glTranslatef(-1000.0, -40.0, -1000.0)

		glUseProgramObjectARB(self.program)

		loc = glGetUniformLocation(self.program,'time')
		glUniform1f(loc, time.time() % 360)

		glScalef(20.0, 8.0, 20.0)
		self.drawVBO(self.verticesId, self.vertexCount)

		glUseProgramObjectARB(0)

		glPopMatrix()
		#
	def drawVBO(self, verticesId, vertexCount):
		glEnableClientState(GL_VERTEX_ARRAY)

		glBindBufferARB(GL_ARRAY_BUFFER_ARB, verticesId)
		glVertexPointer(3, GL_FLOAT, 0, None)

		glDrawArrays(GL_TRIANGLES, 0, vertexCount)

		glDisableClientState(GL_VERTEX_ARRAY)
		#
