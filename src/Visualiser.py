import math, sys
import glfw
import OpenGL.GL as gl
import numpy
import glm
from queue import Queue

vs = """
#version 400 core
layout(location = 0) in vec3 vertexPosition_modelspace;

uniform vec3 staticcolor;
uniform mat4 fullmatrix;

out vec3 fragmentColor;
  
void main(){
  gl_Position = fullmatrix * vec4(vertexPosition_modelspace, 1);
  fragmentColor = staticcolor;
}
"""

fs = """
#version 400 core
in vec3 fragmentColor;

out vec3 color;

void main(){
  color = fragmentColor;
}
"""

cube_verticies = [ 
        1.0, 1.0, 1.0,
        1.0, 0.0, 0.0,
        1.0, 1.0, 0.0,
        0.0, 0.0, 1.0,
        1.0, 0.0, 1.0,
        1.0, 1.0, 1.0,
        0.0, 1.0, 0.0,
        0.0, 1.0, 1.0,
        1.0, 1.0, 1.0,
        0.0, 0.0, 1.0,
        1.0, 1.0, 1.0,
        0.0, 1.0, 1.0,
        1.0, 1.0, 1.0,
        1.0, 0.0, 1.0,
        1.0, 0.0, 0.0,
        0.0, 1.0, 0.0,
        1.0, 1.0, 1.0,
        1.0, 1.0, 0.0,
        1.0, 0.0, 0.0,
        0.0, 1.0, 0.0,
        1.0, 1.0, 0.0,
        0.0, 0.0, 0.0,
        0.0, 0.0, 1.0,
        0.0, 1.0, 1.0,
        0.0, 1.0, 1.0,
        0.0, 1.0, 0.0,
        0.0, 0.0, 0.0,
        0.0, 0.0, 0.0,
        1.0, 0.0, 1.0,
        0.0, 0.0, 1.0,
        0.0, 0.0, 0.0,
        1.0, 0.0, 0.0,
        1.0, 0.0, 1.0,
        0.0, 0.0, 0.0,
        0.0, 1.0, 0.0,
        1.0, 0.0, 0.0
        ]

frame_verticies = [
        0.0, 0.0, 0.0,
        0.0, 0.0, 1.0,
        0.0, 0.0, 1.0, 
        0.0, 1.0, 1.0,
        0.0, 0.0, 1.0, 
        1.0, 0.0, 1.0, 
        1.0, 1.0, 0.0,
        1.0, 1.0, 1.0,
        0.0, 0.0, 0.0, 
        0.0, 1.0, 0.0,
        0.0, 1.0, 0.0, 
        0.0, 1.0, 1.0, 
        0.0, 1.0, 0.0,
        1.0, 1.0, 0.0,
        1.0, 0.0, 1.0, 
        1.0, 1.0, 1.0,
        0.0, 0.0, 0.0, 
        1.0, 0.0, 0.0,
        1.0, 0.0, 0.0, 
        1.0, 1.0, 0.0, 
        1.0, 0.0, 0.0, 
        1.0, 0.0, 1.0,
        0.0, 1.0, 1.0, 
        1.0, 1.0, 1.0,
        ]

indexed_vertecies = [
        0.0, 0.0, 0.0,
        0.0, 0.0, 1.0,
        0.0, 1.0, 0.0,
        0.0, 1.0, 1.0,
        1.0, 0.0, 0.0,
        1.0, 0.0, 1.0,
        1.0, 1.0, 0.0,
        1.0, 1.0, 1.0
        ]

cube_indicies = [
        7, 4, 6,
        1, 5, 7, 
        2, 3, 7, 
        1, 7, 3, 
        7, 5, 4,
        2, 7, 6,
        4, 2, 6,
        0, 1, 3,
        3, 2, 0,
        0, 5, 1,
        0, 4, 5,
        0, 2, 1
        ]

frame_indicies = [
        0, 1,
        1, 3,
        1, 5,
        6, 7,
        0, 2,
        2, 3, 
        2, 6, 
        5, 7, 
        0, 4,
        4, 5, 
        4, 6,
        3, 7
        ]

def load_shaders(vs, fs):
    vertex_shader_id = gl.glCreateShader(gl.GL_VERTEX_SHADER)
    fragment_shader_id = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)

    result = gl.GL_FALSE
    info_log_length = 0

    gl.glShaderSource(vertex_shader_id, vs)
    gl.glCompileShader(vertex_shader_id)

    gl.glGetShaderiv(vertex_shader_id, gl.GL_COMPILE_STATUS, result)
    gl.glGetShaderiv(vertex_shader_id, gl.GL_INFO_LOG_LENGTH, info_log_length)
    if info_log_length > 0:
        vertex_shader_error_message  = []
        gl.glGetShaderInfoLog(vertex_shader_id, info_log_length, None, vertex_shader_error_message)
        print(vertex_shader_error_message)

    gl.glShaderSource(fragment_shader_id, fs)
    gl.glCompileShader(fragment_shader_id)

    gl.glGetShaderiv(fragment_shader_id, gl.GL_COMPILE_STATUS, result)
    gl.glGetShaderiv(fragment_shader_id, gl.GL_INFO_LOG_LENGTH, info_log_length)
    if info_log_length > 0:
        fragment_shader_error_message  = []
        gl.glGetShaderInfoLog(fragment_shader_id, info_log_length, None, fragment_shader_error_message)
        print(fragment_shader_error_message)

    program_id = gl.glCreateProgram()
    gl.glAttachShader(program_id, vertex_shader_id)
    gl.glAttachShader(program_id, fragment_shader_id)

    gl.glLinkProgram(program_id)
    print(gl.glGetProgramInfoLog(program_id))

    gl.glGetProgramiv(program_id, gl.GL_LINK_STATUS, result)
    gl.glGetProgramiv(program_id, gl.GL_INFO_LOG_LENGTH, info_log_length)
    if info_log_length > 0:
        program_error_message  = []
        gl.glGetProgramInfoLog(program_id, info_log_length, None, program_error_message)
        print(program_error_message)

    gl.glDetachShader(program_id, vertex_shader_id)
    gl.glDetachShader(program_id, fragment_shader_id)

    gl.glDeleteShader(vertex_shader_id)
    gl.glDeleteShader(fragment_shader_id)

    return program_id

class Display:
    def __init__(self, octree):
        self.octree = octree
        self.octree_data = []
        self.window_dims = [1280, 960]
        
        self.fulcrum = glm.vec3(2**(octree.level-1))  # orbit center of camera
        self.direction = glm.vec3(0)
        self.position = glm.vec3(0)
        self.dist = 8
        self.barrier = 7
        
        self.h_angle = math.pi/4
        self.v_angle = 0 # -1*math.pi/8
        self.initial_fov = 60.0

        self.fill_color = glm.vec3(0.9)

        self.speed = 1.0
        self.mouse_speed = 0.5

        self.projectionmatrix = glm.perspective(glm.radians(60.0), 1280/960, 0.1, 100.0)
    
        if not glfw.init():
            print(glfw.get_error())
            return
        
        self.last_time = glfw.get_time()

        glfw.window_hint(glfw.SAMPLES, 4)

        self.window = glfw.create_window(self.window_dims[0], self.window_dims[1], "Octrees!", None, None)
        if not self.window:
            glfw.terminate()
            return

        glfw.make_context_current(self.window)
        gl.glClearColor(0.0, 0.6, 1.0, 0.0)

        self.program_id = load_shaders(vs, fs)
        gl.glUseProgram(self.program_id)
        
        self.color_id = gl.glGetUniformLocation(self.program_id, "staticcolor")
        self.fullmatrix_id = gl.glGetUniformLocation(self.program_id, "fullmatrix")

        self.vertex_array_id = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.vertex_array_id)

        # self.vertex_buffer = gl.glGenBuffers(1)
        # gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vertex_buffer)
        # indexed_vertex_data = numpy.array(indexed_vertecies, numpy.float32)
        # gl.glBufferData(gl.GL_ARRAY_BUFFER, len(indexed_vertex_data)*4, indexed_vertex_data, gl.GL_STATIC_DRAW)

        # self.cube_index_buffer = gl.glGenBuffers(1)
        # gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.cube_index_buffer)
        # cube_index_data = numpy.array(cube_indicies, numpy.uint16)
        # gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, len(cube_index_data)*2, cube_index_data, gl.GL_STATIC_DRAW)

        # self.frame_index_buffer = gl.glGenBuffers(1)
        # gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.frame_index_buffer)
        # frame_index_data = numpy.array(frame_indicies, numpy.uint16)
        # gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, len(frame_index_data)*2, frame_index_data, gl.GL_STATIC_DRAW)

        # gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, 0)

        self.cube_vertex_buffer = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.cube_vertex_buffer)
        cube_vertex_data = numpy.array(cube_verticies, numpy.float32)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, len(cube_vertex_data)*4, cube_vertex_data, gl.GL_STATIC_DRAW)

        self.frame_vertex_buffer = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.frame_vertex_buffer)
        frame_vertex_data = numpy.array(frame_verticies, numpy.float32)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, len(frame_vertex_data)*4, frame_vertex_data, gl.GL_STATIC_DRAW)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)


        gl.glEnable(gl.GL_POLYGON_OFFSET_FILL)
        gl.glPolygonOffset(1, -1)
        gl.glLineWidth(2)
        gl.glEnable(gl.GL_BLEND)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glDepthFunc(gl.GL_LEQUAL)
        gl.glEnable(gl.GL_CULL_FACE)

    def poll_octree_data(self):
        tmp = self.octree.map()
        self.octree_data = []
        for line in tmp:
            if line["void"]:
                color = glm.vec3(0)
            else:
                color = glm.vec3(0, 1, 0)
            self.octree_data.append({"pos":line["coords"], "level":line["level"], "fill":not line["void"], "framecolor":color})

    def draw(self):
        gl.glUseProgram(self.program_id)
        
        viewmatrix = self.probeKeyBoard() # called once each draw call
        
        # gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vertex_buffer)
        # gl.glEnableVertexAttribArray(0)
        # gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

        barrier_vector = self.barrier*self.direction

        for cube in self.octree_data:
            
            modelmatrix = glm.translate(glm.mat4(1), glm.vec3(cube["pos"])) * glm.scale(glm.mat4(1), glm.vec3(2**cube["level"])) 
            fullmatrix = self.projectionmatrix * viewmatrix * modelmatrix
            gl.glUniformMatrix4fv(self.fullmatrix_id, 1, gl.GL_FALSE, glm.value_ptr(fullmatrix)) # called once each cube
                            
            if glm.dot(glm.vec3(cube["pos"]) + glm.vec3(2**(cube["level"]-1)) - (self.position + barrier_vector), barrier_vector) < 0:
                continue
            
            if cube["fill"]:

                gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.cube_vertex_buffer)
                gl.glEnableVertexAttribArray(0)
                gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

                gl.glUniform3fv(self.color_id, 1, glm.value_ptr(self.fill_color))
                gl.glDrawArrays(gl.GL_TRIANGLES, 0, len(cube_verticies))

                gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.frame_vertex_buffer)
                gl.glEnableVertexAttribArray(0)
                gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

                gl.glUniform3fv(self.color_id, 1, glm.value_ptr(glm.vec3(1, 0, 0)))
                gl.glDrawArrays(gl.GL_LINES, 0, len(frame_verticies))

            else:
                gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.frame_vertex_buffer)
                gl.glEnableVertexAttribArray(0)
                gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

                gl.glUniform3fv(self.color_id, 1, glm.value_ptr(glm.vec3(0, 0, 1)))
                gl.glDrawArrays(gl.GL_LINES, 0, len(frame_verticies))

            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

            # if cube["fill"]:
            #     gl.glUniform3fv(self.color_id, 1, glm.value_ptr(self.fill_color))
            #     gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.cube_index_buffer)
            #     gl.glDrawElements(gl.GL_TRIANGLES, len(cube_indicies), gl.GL_UNSIGNED_INT, None)

            # gl.glUniform3fv(self.color_id, 1, glm.value_ptr(cube["framecolor"]))
            # gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.frame_index_buffer)
            # gl.glDrawElements(gl.GL_LINES, len(frame_indicies), gl.GL_UNSIGNED_INT, None)
        
        gl.glDisableVertexAttribArray(0)



    def main(self):
        self.poll_octree_data()
        while not glfw.get_key(self.window, glfw.KEY_ESCAPE) == glfw.PRESS:
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

            self.draw()
            glfw.swap_buffers(self.window)
            glfw.poll_events() 

        glfw.terminate()

    def probeKeyBoard(self):  
        """returns updated view matrix"""
        self.current_time = glfw.get_time()
        self.delta_time = self.current_time - self.last_time
        self.last_time = self.current_time

        if(glfw.get_key(self.window, glfw.KEY_W) == glfw.PRESS):
            self.v_angle -= self.delta_time * self.speed

        if(glfw.get_key(self.window, glfw.KEY_S) == glfw.PRESS):
            self.v_angle += self.delta_time * self.speed

        if(glfw.get_key(self.window, glfw.KEY_D) == glfw.PRESS):
            self.h_angle += self.delta_time * self.speed

        if(glfw.get_key(self.window, glfw.KEY_A) == glfw.PRESS):
            self.h_angle -= self.delta_time * self.speed

        self.h_angle %= math.pi*2
        self.v_angle %= math.pi*2

        self.direction = glm.vec3(math.cos(self.v_angle) * math.sin(self.h_angle),
                            math.sin(self.v_angle),
                            math.cos(self.v_angle) * math.cos(self.h_angle))
        
        self.position = self.fulcrum - self.dist * self.direction


        right = glm.vec3(math.sin(self.h_angle - math.pi/2), 0, math.cos(self.h_angle - math.pi/2))
        up = glm.cross(right, self.direction)
        return glm.lookAt(self.position, self.fulcrum, up)
