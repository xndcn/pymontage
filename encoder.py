import av
from PIL import Image

class Encoder:
    def __init__(self, filename, size, codec, bit_rate, rate):
        self.container = av.open(filename, 'w')
        self.size = size
        self.video = self.container.add_stream(codec, rate)
        self.video.width, self.video.height = self.size
        self.video.bit_rate = bit_rate
        self.video.pix_fmt = 'yuv420p'

    def encode(self, picture):
        if isinstance(picture, Image.Image):
            image = picture
        else:
            image = Image.frombytes('RGB', self.size, picture)
        frame = av.VideoFrame.from_image(image)
        packet = self.video.encode(frame)
        if packet is not None:
            self.container.mux(packet)

    def save(self):
        while True:
            packet = self.video.encode()
            if packet is None:
                break
            self.container.mux(packet)
        self.container.close()
