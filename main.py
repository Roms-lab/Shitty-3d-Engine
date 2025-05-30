import glfw
from OpenGL.GL import *
import numpy as np
import ctypes
import time

print("Script started.")

# Helper function for perspective projection
def perspective(fovy, aspect, znear, zfar):
    f = 1.0 / np.tan(fovy / 2)
    proj = np.zeros((4, 4), dtype=np.float32)
    proj[0, 0] = f / aspect
    proj[1, 1] = f
    proj[2, 2] = (zfar + znear) / (znear - zfar)
    proj[2, 3] = (2 * zfar * znear) / (znear - zfar)
    proj[3, 2] = -1.0
    return proj

# Helper function for lookAt view matrix
def look_at(eye, center, up):
    f = center - eye
    f = f / np.linalg.norm(f)
    u = up / np.linalg.norm(up)
    s = np.cross(f, u)
    s = s / np.linalg.norm(s)
    u = np.cross(s, f)
    m = np.identity(4, dtype=np.float32)
    m[0, :3] = s
    m[1, :3] = u
    m[2, :3] = -f
    m[0, 3] = -np.dot(s, eye)
    m[1, 3] = -np.dot(u, eye)
    m[2, 3] = np.dot(f, eye)
    return m

def rotation_matrix_y(angle):
    c, s = np.cos(angle), np.sin(angle)
    return np.array([
        [c, 0, s, 0],
        [0, 1, 0, 0],
        [-s, 0, c, 0],
        [0, 0, 0, 1]
    ], dtype=np.float32)

# Initialize GLFW
def init_window(width, height, title):
    print("Initializing GLFW...")
    if not glfw.init():
        raise Exception("GLFW can't be initialized")
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    window = glfw.create_window(width, height, title, None, None)
    if not window:
        glfw.terminate()
        raise Exception("GLFW window can't be created")
    glfw.make_context_current(window)
    print("Window created and context set.")
    return window

def create_shader(shader_type, source):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)
    if not glGetShaderiv(shader, GL_COMPILE_STATUS):
        error = glGetShaderInfoLog(shader).decode()
        raise Exception(f'Shader compile error: {error}')
    return shader

def create_program(vertex_src, fragment_src):
    vertex_shader = create_shader(GL_VERTEX_SHADER, vertex_src)
    fragment_shader = create_shader(GL_FRAGMENT_SHADER, fragment_src)
    program = glCreateProgram()
    glAttachShader(program, vertex_shader)
    glAttachShader(program, fragment_shader)
    glLinkProgram(program)
    if not glGetProgramiv(program, GL_LINK_STATUS):
        error = glGetProgramInfoLog(program).decode()
        raise Exception(f'Program link error: {error}')
    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)
    return program

def main():
    window = init_window(800, 600, "3D Engine - Prism")
    print("Starting main loop...")

    # Prism base triangle vertices (counter-clockwise)
    # Base 1 (z = -0.5): A, B, C
    # Base 2 (z = +0.5): D, E, F (corresponding to A, B, C)
    vertices = np.array([
        # x,    y,    z,     r, g, b
        -0.5, -0.5, -0.5,   1, 0, 0,  # 0: A (red)
         0.5, -0.5, -0.5,   0, 1, 0,  # 1: B (green)
         0.0,  0.5, -0.5,   0, 0, 1,  # 2: C (blue)
        -0.5, -0.5,  0.5,   1, 1, 0,  # 3: D (yellow)
         0.5, -0.5,  0.5,   0, 1, 1,  # 4: E (cyan)
         0.0,  0.5,  0.5,   1, 0, 1,  # 5: F (magenta)
    ], dtype=np.float32)

    indices = np.array([
        # Base 1 (A, B, C)
        0, 1, 2,
        # Base 2 (D, F, E) (note winding for correct normal)
        3, 5, 4,
        # Side 1 (A, B, E, D)
        0, 1, 4,
        0, 4, 3,
        # Side 2 (B, C, F, E)
        1, 2, 5,
        1, 5, 4,
        # Side 3 (C, A, D, F)
        2, 0, 3,
        2, 3, 5
    ], dtype=np.uint32)

    vertex_src = """
    #version 330 core
    layout(location = 0) in vec3 aPos;
    layout(location = 1) in vec3 aColor;
    uniform mat4 mvp;
    out vec3 vColor;
    void main() {
        gl_Position = mvp * vec4(aPos, 1.0);
        vColor = aColor;
    }
    """
    fragment_src = """
    #version 330 core
    in vec3 vColor;
    out vec4 FragColor;
    void main() {
        FragColor = vec4(vColor, 1.0);
    }
    """

    program = create_program(vertex_src, fragment_src)

    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)
    EBO = glGenBuffers(1)
    glBindVertexArray(VAO)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
    # Position
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * vertices.itemsize, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    # Color
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * vertices.itemsize, ctypes.c_void_p(3 * vertices.itemsize))
    glEnableVertexAttribArray(1)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

    aspect = 800 / 600
    proj = perspective(np.radians(45), aspect, 0.1, 100.0)
    eye = np.array([2.0, 2.0, 3.0], dtype=np.float32)
    center = np.array([0.0, 0.0, 0.0], dtype=np.float32)
    up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
    view = look_at(eye, center, up)

    mvp_loc = glGetUniformLocation(program, "mvp")

    while not glfw.window_should_close(window):
        glfw.poll_events()
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)  # Solid rendering
        glUseProgram(program)
        angle = time.time() % (2 * np.pi)
        model = rotation_matrix_y(angle)
        mvp = proj @ view @ model
        glUniformMatrix4fv(mvp_loc, 1, GL_FALSE, mvp)
        glBindVertexArray(VAO)
        glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, None)
        glBindVertexArray(0)
        glfw.swap_buffers(window)

    glDeleteVertexArrays(1, [VAO])
    glDeleteBuffers(1, [VBO])
    glDeleteBuffers(1, [EBO])
    glfw.terminate()
    print("Terminated cleanly.")

if __name__ == "__main__":
    main() 