class UDPPacket(object):
    def __init__(self, time, size, id, src, dst = None):
        self.time = time
        self.size = size
        self.id = id
        self.src = src
        self.dst = dst

    def __repr__(self):
        return "id: {}, src: {}, time: {}, size: {}".format(self.id, self.src, self.time, self.size)
