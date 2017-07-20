import av

class Decoder:
    def __init__(self, filename):
        self.container = av.open(filename)

        streams = self.container.streams
        self.video = streams.video[0]

    def decode_all(self):
        for packet in self.container.demux(self.video):
            for frame in packet.decode():
                yield frame

    @property
    def size(self):
        return self.video.width, self.video.height

    @property
    def frames(self):
        return self.video.frames

    @property
    def duration(self):
        return self.container.duration / 1000

    @property
    def rate(self):
        return 1 / self.video.rate

    @property
    def bit_rate(self):
        return self.video.bit_rate
