import math, sys, struct
import glfw
import OpenGL.GL as gl
import numpy
import glm
import ctypes

cs = """
    #version 430 core

    uniform uint vertexcount;

    struct DrawCommand {
        uint count;
        uint instanceCount;
        uint firstIndex;
        uint baseVertex;
        uint baseInstance;
    };

    layout(local_size_x = 1) in;

    layout(std140, binding = 0) uniform barrierData {
        vec3 direction;
        vec3 barrier;
    };

    layout(std140, binding = 1) buffer modelMatrix {
        mat4 model[];
    };

    layout(std430, binding = 2) buffer drawIndirectBuffer {
        DrawCommand commands[];
    };


    void main(){
        const uint index = gl_WorkGroupID.x; // this shader may only be dispatched in the x dimension

        bool draw = dot((model[index] * vec4(0.5, 0.5, 0.5, 1.0)).xyz - barrier, direction) > 0.0;

        commands[index] = DrawCommand(
            vertexcount,
            draw ? 1 : 0,
            0,
            0,
            index
        );        
    }
    """

vs = """
    #version 430 core
    
    layout(location = 0) in vec3 vertexPosition_modelspace;
    layout(location = 2) in mat4 model;

    layout(std140, binding = 3) uniform matricies {
        mat4 projection;
        mat4 view;
    };

    uniform vec3 staticcolor;

    out vec3 fragmentColor;
    
    void main(){
        mat4 fullMatrix = projection * view * model;
        gl_Position = fullMatrix * vec4(vertexPosition_modelspace, 1.0);
        fragmentColor = staticcolor;
    }
    """

fs = """
    #version 430 core
    in vec3 fragmentColor;

    out vec3 color;

    void main(){
        color = fragmentColor;
    }
    """

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
        0, 2, 4
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


def compile_compute_shader(cs):
    compute_shader_id = gl.glCreateShader(gl.GL_COMPUTE_SHADER)

    gl.glShaderSource(compute_shader_id, cs)
    gl.glCompileShader(compute_shader_id)
    if not gl.glGetShaderiv(compute_shader_id, gl.GL_COMPILE_STATUS):
        print("compute shader compile error:\n\t", "\n\t".join(gl.glGetShaderInfoLog(compute_shader_id).decode().split("\n")), sep="")

    program_id = gl.glCreateProgram()
    gl.glAttachShader(program_id, compute_shader_id)

    gl.glLinkProgram(program_id)
    if not gl.glGetProgramiv(program_id, gl.GL_LINK_STATUS):
        print("shader link error:\n\t", "\n\t".join(gl.glGetProgramInfoLog(program_id).decode().split("\n")), sep="")
        sys.exit()

    gl.glDetachShader(program_id, compute_shader_id)
    gl.glDeleteShader(compute_shader_id)

    return program_id


def load_shaders(vs, fs):
    vertex_shader_id = gl.glCreateShader(gl.GL_VERTEX_SHADER)
    fragment_shader_id = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)

    gl.glShaderSource(vertex_shader_id, vs)
    gl.glCompileShader(vertex_shader_id)
    if not gl.glGetShaderiv(vertex_shader_id, gl.GL_COMPILE_STATUS):
        print("vertex shader compile error:\n\t", "\n\t".join(gl.glGetShaderInfoLog(vertex_shader_id).decode().split("\n")), sep="")

    gl.glShaderSource(fragment_shader_id, fs)
    gl.glCompileShader(fragment_shader_id)
    if not gl.glGetShaderiv(fragment_shader_id, gl.GL_COMPILE_STATUS):
        print("fragment shader compile error:\n\t", "\n\t".join(gl.glGetShaderInfoLog(fragment_shader_id).decode().split("\n")), sep="")

    program_id = gl.glCreateProgram()
    gl.glAttachShader(program_id, vertex_shader_id)
    gl.glAttachShader(program_id, fragment_shader_id)

    gl.glLinkProgram(program_id)
    if not gl.glGetProgramiv(program_id, gl.GL_LINK_STATUS):
        print("shader link error:\n\t", "\n\t".join(gl.glGetProgramInfoLog(program_id).decode().split("\n")), sep="")
        sys.exit()

    gl.glDetachShader(program_id, vertex_shader_id)
    gl.glDetachShader(program_id, fragment_shader_id)

    gl.glDeleteShader(vertex_shader_id)
    gl.glDeleteShader(fragment_shader_id)

    return program_id


class Display:
    def __init__(self, octree):
        self.octree = octree
        self.window_dims = [1280, 960]
        
        self.fulcrum = glm.vec3(2**(octree.level-1))  # orbit center of camera
        self.direction = glm.vec3(0)
        self.position = glm.vec3(0)
        self.dist = 2**(octree.level+1)
        self.barrier = 0
        
        self.h_angle = math.pi/4
        self.v_angle = 0 # -1*math.pi/8
        self.initial_fov = 60.0

        self.fill_color = glm.vec3(0.9)

        self.speed = 1.0
        self.mouse_speed = 0.5

        self.projectionmatrix = glm.perspective(glm.radians(60.0), 3/2, 0.1, 10000.0)
    
        if not glfw.init():
            print(glfw.get_error())
            return

        self.last_time = glfw.get_time()
        self.last_mouse_x, self.last_mouse_y = None, None

        glfw.window_hint(glfw.SAMPLES, 4)

        self.window = glfw.create_window(self.window_dims[0], self.window_dims[1], "Octrees!", None, None)
        if not self.window:
            glfw.terminate()
            return

        glfw.make_context_current(self.window)
        glfw.set_scroll_callback(self.window, self.scroll)
        gl.glClearColor(0.0, 0.6, 1.0, 0.0)

        self.compute_id = compile_compute_shader(cs)
        self.program_id = load_shaders(vs, fs)
        gl.glUseProgram(self.program_id)
        
        self.color_id = gl.glGetUniformLocation(self.program_id, "staticcolor")
        self.vertex_count_id = gl.glGetUniformLocation(self.compute_id, "vertexcount")

        self.vertex_array_id = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.vertex_array_id)

        # create & load indexed vertex buffer
        self.vertex_buffer = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vertex_buffer)
        indexed_vertex_data = numpy.array(indexed_vertecies, numpy.float32)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, len(indexed_vertex_data)*4, indexed_vertex_data, gl.GL_STATIC_DRAW)

        # create & store cube index buffer
        self.cube_index_buffer = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.cube_index_buffer)
        cube_index_data = numpy.array(cube_indicies, numpy.uint16)
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, len(cube_index_data)*2, cube_index_data, gl.GL_STATIC_DRAW)

        # create & store frame index buffer
        self.frame_index_buffer = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.frame_index_buffer)
        frame_index_data = numpy.array(frame_indicies, numpy.uint16)
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, len(frame_index_data)*2, frame_index_data, gl.GL_STATIC_DRAW)

    
        # create & partially load transformation matricies 
        self.uniform_matricies = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_UNIFORM_BUFFER, self.uniform_matricies)
        gl.glBufferData(gl.GL_UNIFORM_BUFFER, 2 * glm.sizeof(glm.mat4), None, gl.GL_STATIC_DRAW)
        gl.glBufferSubData(gl.GL_UNIFORM_BUFFER, 0, glm.sizeof(glm.mat4), glm.value_ptr(self.projectionmatrix))
        
        # create & reserve space for barrier data
        self.barrier_vectors = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_UNIFORM_BUFFER, self.barrier_vectors)
        gl.glBufferData(gl.GL_UNIFORM_BUFFER, 2 * glm.sizeof(glm.vec4), None, gl.GL_STATIC_DRAW)

        # create indirect & matrix buffers
        self.matrix_buffer, self.indirect_buffer = gl.glGenBuffers(2)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, 0)
        gl.glBindBuffer(gl.GL_UNIFORM_BUFFER, 0)

        gl.glEnable(gl.GL_POLYGON_OFFSET_FILL)
        gl.glPolygonOffset(1, 0)
        gl.glLineWidth(1)
        gl.glEnable(gl.GL_LINE_SMOOTH)
        gl.glEnable(gl.GL_BLEND)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glDepthFunc(gl.GL_LEQUAL)
        gl.glEnable(gl.GL_CULL_FACE)


    def poll_octree_data(self):
        matricies = []
        for line in self.octree:
            if line["void"]:
                matricies.append(glm.translate(glm.mat4(1), glm.vec3(line["coords"])) * glm.scale(glm.mat4(1), glm.vec3(2**line["level"])))
        
        self.cube_count = len(matricies)
        matrix_array = glm.array(matricies)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.matrix_buffer)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, matrix_array.nbytes, matrix_array.ptr, gl.GL_STATIC_DRAW)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

        gl.glBindBuffer(gl.GL_DRAW_INDIRECT_BUFFER, self.indirect_buffer)
        gl.glBufferStorage(gl.GL_DRAW_INDIRECT_BUFFER, 32 * len(matricies), None, gl.GL_MAP_READ_BIT | gl.GL_MAP_WRITE_BIT)
        gl.glBindBuffer(gl.GL_DRAW_INDIRECT_BUFFER, 0)


    def draw(self):
        # Update UBO with new view matrix
        gl.glBindBuffer(gl.GL_UNIFORM_BUFFER, self.uniform_matricies)
        gl.glBufferSubData(gl.GL_UNIFORM_BUFFER, glm.sizeof(glm.mat4), glm.sizeof(glm.mat4), glm.value_ptr(self.probeKeyBoard()))

        # Update UBO with barrier data
        gl.glBindBuffer(gl.GL_UNIFORM_BUFFER, self.barrier_vectors)
        gl.glBufferSubData(gl.GL_UNIFORM_BUFFER, 0, glm.sizeof(glm.vec3), glm.value_ptr(self.direction))
        gl.glBufferSubData(gl.GL_UNIFORM_BUFFER, glm.sizeof(glm.vec4), glm.sizeof(glm.vec3), glm.value_ptr(self.barrier*self.direction + self.position))
        gl.glBindBuffer(gl.GL_UNIFORM_BUFFER, 0)

        # # Compute Commands
        gl.glUseProgram(self.compute_id)

        gl.glUniform1ui(self.vertex_count_id, len(cube_indicies))
        gl.glBindBufferBase(gl.GL_UNIFORM_BUFFER, 0, self.barrier_vectors)
        gl.glBindBufferBase(gl.GL_SHADER_STORAGE_BUFFER, 1, self.matrix_buffer)
        gl.glBindBufferBase(gl.GL_SHADER_STORAGE_BUFFER, 2, self.indirect_buffer)

        gl.glDispatchCompute(self.cube_count, 1, 1)
        gl.glMemoryBarrier(gl.GL_COMMAND_BARRIER_BIT | gl.GL_SHADER_STORAGE_BARRIER_BIT)

        gl.glUseProgram(self.program_id)
                
        # Bind VBO with verticies
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vertex_buffer)
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

        # Bind VBO with matricies and set attrib pointers
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.matrix_buffer)
    
        for i in range(4):
            gl.glEnableVertexAttribArray(2 + i)
            gl.glVertexAttribPointer(2 + i, 4, gl.GL_FLOAT, gl.GL_FALSE, glm.sizeof(glm.mat4), ctypes.c_void_p(glm.sizeof(glm.vec4) * i))
            gl.glVertexAttribDivisor(2 + i, 1)

        gl.glBindBufferBase(gl.GL_UNIFORM_BUFFER, 3, self.uniform_matricies)
        gl.glBindBuffer(gl.GL_DRAW_INDIRECT_BUFFER, self.indirect_buffer)

        # print(self.cube_count)
        # for i in range(self.cube_count):
        #     print(gl.glGetBufferSubData(gl.GL_DRAW_INDIRECT_BUFFER, 20 * i, 20))
        
        # sys.exit()
    
        # for i in [0, 2, 3, 4, 5]:
        #     print(gl.glGetVertexAttribfv(i, gl.GL_VERTEX_ATTRIB_RELATIVE_OFFSET))
    
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.cube_index_buffer)
        gl.glUniform3fv(self.color_id, 1, glm.value_ptr(self.fill_color))
        gl.glMultiDrawElementsIndirect(gl.GL_TRIANGLES, gl.GL_UNSIGNED_SHORT, None, self.cube_count, 20)
        
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.frame_index_buffer)
        gl.glUniform3fv(self.color_id, 1, glm.value_ptr(glm.vec3(1, 0, 0)))
        gl.glMultiDrawElementsIndirect(gl.GL_LINES, gl.GL_UNSIGNED_SHORT, None, self.cube_count, 20)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, 0)
        gl.glBindBuffer(gl.GL_DRAW_INDIRECT_BUFFER, 0)


    def main(self):
        self.poll_octree_data()
        while not glfw.get_key(self.window, glfw.KEY_ESCAPE) == glfw.PRESS:
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

            self.draw()
            glfw.swap_buffers(self.window)
            glfw.poll_events() 

        glfw.terminate()


    def scroll(self, window, xoffset, yoffset):
        if glfw.get_key(self.window, glfw.KEY_LEFT_ALT) == glfw.PRESS:
            self.barrier = (self.barrier + yoffset) if self.barrier >= 0 else 0
        else:
            self.dist = (self.dist + yoffset) if self.dist >= 0 else 0


    def on_key(self, window, key, scancode, action, mods):...


    def probeKeyBoard(self):  
        """returns updated view matrix"""
        self.current_time = glfw.get_time()
        self.delta_time = self.current_time - self.last_time
        self.last_time = self.current_time

        print("\r                                                 \r", round(self.delta_time, 5), "\t|", 1/self.delta_time, sep="", end="")

        if glfw.get_key(self.window, glfw.KEY_W) == glfw.PRESS:
            self.v_angle -= (self.delta_time * self.speed) if (self.v_angle > math.pi/-2) else 0

        if glfw.get_key(self.window, glfw.KEY_S) == glfw.PRESS:
            self.v_angle += (self.delta_time * self.speed) if (self.v_angle < math.pi/2) else 0

        if glfw.get_key(self.window, glfw.KEY_D) == glfw.PRESS:
            self.h_angle += self.delta_time * self.speed

        if glfw.get_key(self.window, glfw.KEY_A) == glfw.PRESS:
            self.h_angle -= self.delta_time * self.speed

        if glfw.get_mouse_button(self.window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS:
            mouse_x, mouse_y = glfw.get_cursor_pos(self.window)
            if self.last_mouse_x and self.last_mouse_y:
                self.h_angle += (self.last_mouse_x - mouse_x) / self.window_dims[0] * 4
                self.v_angle += (self.last_mouse_y - mouse_y) / self.window_dims[1] * 4
            self.last_mouse_x, self.last_mouse_y = mouse_x, mouse_y
        elif self.last_mouse_x or self.last_mouse_y:
            self.last_mouse_x, self.last_mouse_y = None, None

        self.direction = glm.vec3(
                            math.cos(self.v_angle) * math.sin(self.h_angle),
                            math.sin(self.v_angle),
                            math.cos(self.v_angle) * math.cos(self.h_angle))

        right = glm.vec3(
                        math.sin(self.h_angle - math.pi/2),
                        0,
                        math.cos(self.h_angle - math.pi/2))

        up = glm.cross(right, self.direction)

        self.position = self.fulcrum - self.dist * self.direction
        return glm.lookAt(self.position, self.fulcrum, up)
