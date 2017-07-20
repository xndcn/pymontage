import ModernGL
import struct

class Render:
    def __init__(self, size, vertex, fragment):
        self.size = size
        self.context = ModernGL.create_standalone_context(self.size)

        renderbuffer = self.context.renderbuffer(self.size, 3)
        self.framebuffer = self.context.framebuffer(renderbuffer)
        self.framebuffer.use()

        program = self.context.program([self.context.vertex_shader(vertex), self.context.fragment_shader(fragment)])
        self.fraction = program.uniforms['fraction']
        vbo = self.context.buffer(struct.pack('8f', -1, -1, 1, -1, -1, 1, 1, 1))
        self.vao = self.context.simple_vertex_array(program, vbo, ['vertex'])

        self.texture = self.context.texture(self.size, 3)
        self.texture.use()

        self.context.enable(ModernGL.BLEND)

    def render(self, clear, picture, fraction):
        if clear:
            self.context.clear(0, 0, 0)
        self.texture.write(picture)
        self.fraction.value = fraction
        self.vao.render(ModernGL.TRIANGLE_STRIP)

        return self.framebuffer.read()

