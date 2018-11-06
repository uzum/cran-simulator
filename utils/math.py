import numpy
import math
import random
random.seed(1337)

def next_poisson(rate):
    return -math.log(1.0 - random.random()) / rate

def next_gaussian(mean, dev):
    return int(numpy.random.normal(mean, dev, 1))
