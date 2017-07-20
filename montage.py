from decoder import Decoder
from render import Render
from encoder import Encoder

import sys
import queue, threading

class Montage:
    STOP = None
    VERTEX_FALLBACK = 'fallback'
    BUFFER_SIZE = 8
    CODEC = 'mpeg4'

    def __init__(self, input_prev, input_next, shader, mix_start_time, output):
        self.shader = shader
        self.mix_start_time = mix_start_time
        self.decoder_prev = Decoder(input_prev)
        self.decoder_next = Decoder(input_next)

        self.size = self.decoder_prev.size
        self.rate = self.decoder_prev.rate
        self.bit_rate = self.decoder_prev.bit_rate

        self.encoder = Encoder(output, self.size, self.CODEC, self.bit_rate, self.rate)

        self.decode_queue_prev = queue.Queue(self.BUFFER_SIZE)
        self.decode_queue_next = queue.Queue(self.BUFFER_SIZE)
        self.encode_queue = queue.Queue(self.BUFFER_SIZE)

    def load_shader(self, vertex, fragment):
        if vertex is None:
            vertex = VERTEX_FALLBACK
        return Render(self.size, open('shaders/' + vertex + '.vertex').read(), open('shaders/' + fragment + '.fragment').read())

    @staticmethod
    def decode(cls, decoder, decode_queue):
        for frame in decoder.decode_all():
            decode_queue.put(frame)
        decode_queue.put(cls.STOP)

    def render(self):
        renderer = self.load_shader(self.VERTEX_FALLBACK, self.shader)
        while True:
            prev_frame = self.decode_queue_prev.get()
            if prev_frame is self.STOP:
                break
            time = prev_frame.time * 1000
            if time < self.mix_start_time:
                self.encode_queue.put(prev_frame.to_image())
            else:
                fraction = (time - self.mix_start_time) / (self.decoder_prev.duration - self.mix_start_time)
                picture = prev_frame.to_image().tobytes()
                picture = renderer.render(True, picture, fraction - 1)
                next_frame = self.decode_queue_next.get()
                picture = next_frame.to_image().tobytes()
                picture = renderer.render(False, picture, fraction)
                self.encode_queue.put(picture)
        while True:
            next_frame = self.decode_queue_next.get()
            if next_frame is self.STOP:
                break
            self.encode_queue.put(next_frame.to_image())
        self.encode_queue.put(self.STOP)

    def encode(self):
        while True:
            picture = self.encode_queue.get()
            if picture is self.STOP:
                break
            self.encoder.encode(picture)
        self.encoder.save()

    def mix(self):
        decode_thread_prev = threading.Thread(target=self.decode, args=(self, self.decoder_prev, self.decode_queue_prev))
        decode_thread_prev.start()
        decode_thread_next = threading.Thread(target=self.decode, args=(self, self.decoder_next, self.decode_queue_next))
        decode_thread_next.start()

        render_thread = threading.Thread(target=self.render)
        render_thread.start()

        encode_thread = threading.Thread(target=self.encode)
        encode_thread.start()

        decode_thread_prev.join()
        decode_thread_next.join()
        render_thread.join()
        encode_thread.join()

if __name__ == '__main__':
    video_prev = sys.argv[1]
    video_next = sys.argv[2]
    shader = sys.argv[3]              # file in shaders/ directory without extendsion. now only `fade` and `slide` is supported.
    mix_start_time = int(sys.argv[4]) # time in milliseconds
    output = sys.argv[5]

    # python montage.py video1.mp4 video2.mp4 fade/slide 1000 output.mp4
    montage = Montage(video_prev, video_next, shader, mix_start_time, output)
    montage.mix()
