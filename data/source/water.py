try:
	import numpy as Numeric
except:
	import Numeric
from OpenGL.GL import *
from OpenGL.GL.ARB.vertex_buffer_object import *
from OpenGL.GL.ARB.shader_objects import *
from OpenGL.GL.ARB.vertex_shader import *
import time
import graphics

class Water:
	def __init__(self):
		meshVertices, self.vertexCount, meshNormals = self.generateMesh()
		self.verticesId, self.normalsId = \
				graphics.createVBO("water", meshVertices, meshNormals)
		self.initShader()
		#
	def initShader(self):
		program = glCreateProgramObjectARB()
		vertexShader = glCreateShaderObjectARB(GL_VERTEX_SHADER_ARB)
		fragmentShader = glCreateShaderObjectARB(GL_FRAGMENT_SHADER_ARB)

		vertexSource = ["""
		uniform float time;

		varying vec3 normal, lightDir, eyeVec;

		varying vec3 vNormal;

		vec3 computeNormal(vec3 pos, vec3 tangent, vec3 binormal) {
			mat3 J;
			float yx = 0.4 * cos(0.2 * pos.x + time);
			float yz = -0.4 * sin(0.2 * pos.z + time);

			J[0][0] = 1.0;
			J[0][1] = yx;
			J[0][2] = 0.0;

			J[1][0] = 0.0;
			J[1][1] = 1.0;
			J[1][2] = 0.0;

			J[2][0] = 0.0;
			J[2][1] = yz;
			J[2][2] = 1.0;

			vec3 u = J * tangent;
			vec3 v = J * binormal;

			vec3 n = cross(v, u);
			return normalize(n);
		}

		void main() {
			vec3 ecPos;
			vec3 aux;

			// Compute vertex position
			vec4 a = gl_Vertex;
			a.y = a.y + (sin(0.2 * a.x + time) + cos(0.2 * a.z + time)) * 2.0;
			gl_Position = gl_ModelViewProjectionMatrix * a;
			///

			// Compute normal
			vec3 newNormal;
			vec3 tangent;
			vec3 binormal;

			vec3 c1 = cross(gl_Normal, vec3(0.0, 0.0, 1.0));
			vec3 c2 = cross(gl_Normal, vec3(0.0, 1.0, 0.0));

			if (length(c1) > length(c2)) {
				tangent = c1;
			} else {
				tangent = c2;
			}
			tangent = normalize(tangent);

			binormal = cross(gl_Normal, tangent);
			binormal = normalize(binormal);

			newNormal = computeNormal(a.xyz, tangent.xyz, binormal);
			newNormal = -newNormal;

			vNormal = normalize(gl_NormalMatrix * newNormal);

			normal = gl_NormalMatrix * newNormal.xyz;
			//////////

			ecPos = vec3(gl_ModelViewMatrix * a);
			lightDir = vec3(gl_LightSource[1].position.xyz - ecPos);
			eyeVec = -ecPos;
		}
		"""]


		fragmentSource = ["""
		varying vec3 normal, lightDir, eyeVec;

		void main() {
			vec4 final_color =
				(gl_FrontLightModelProduct.sceneColor
					* gl_FrontMaterial.ambient)
				+ (gl_LightSource[1].ambient * gl_FrontMaterial.ambient);

			vec3 N = normalize(normal);
			vec3 L = normalize(lightDir);

			float lambertTerm = max(dot(N, L), 0.0);

			if (lambertTerm > 0.0) {
				final_color += gl_LightSource[1].diffuse *
								gl_FrontMaterial.diffuse *
								lambertTerm;

				vec3 E = normalize(eyeVec);
				vec3 R = reflect(-L, N);
				float specular = pow(max(dot(R, E), 0.0),
									gl_FrontMaterial.shininess);
				final_color += gl_LightSource[1].specular *
								gl_FrontMaterial.specular *
								specular;
			}
			gl_FragColor = final_color;

			//gl_FragColor = float4( (normal + 1) / 2.0, 1);
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
		normals = Numeric.zeros( (99*99*6, 3), 'f')
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

		n = 0
		for x in xrange(0, 99):
			for z in xrange(0, 99):
				for i in xrange(0,6):
					normals[n, 0] = 0.0
					normals[n, 1] = 1.0
					normals[n, 2] = 0.0
					n += 1

		return (mesh, nIndex, normals)
		#
	def draw(self):
		glPushMatrix()

		glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, (0.6, 0.6, 1.0, 1.0))
		glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, (0.6, 0.6, 1.0, 1.0))
		glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))

		glTranslatef(-1000.0, -40.0, -1000.0)
		glScalef(20.0, 8.0, 20.0)

		glUseProgramObjectARB(self.program)

		loc = glGetUniformLocation(self.program,'time')
		glUniform1f(loc, time.time() % 360)

		graphics.drawVBO(self.verticesId, self.normalsId, self.vertexCount)

		glUseProgramObjectARB(0)

		glPopMatrix()
		#
