import random

class RemoteRadioHead(object):
    def __init__(self, env, name):
        self.name = name
        self.env = env
        self.action = env.process(self.run())

    def run(self):
        while True:
            yield self.env.timeout(random.randint(1, 5))
            print('sent a message at %s from %s' % (self.env.now, self.name))
