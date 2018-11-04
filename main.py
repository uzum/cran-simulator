import simpy

from config import *
from entities.remote_radio_head import RemoteRadioHead

env = simpy.Environment()
for i in range(RRH_NUMBER):
    rrh = RemoteRadioHead(env, 'rrh#' + str(i))

env.run(until=100)
