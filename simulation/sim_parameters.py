class SimulationParams(object):
    SPLIT_ALGORITHM = "kargers"
    SIMULATION_TIME = 1000
    STEP_TIME = 0
    PACKET_GENERATION_FINISH = float('inf')
    PACKET_GENERATION_DELAY = 0
    BBU_DEBUG = False
    VIRTUAL_SWITCH_RATE = 90000
    VIRTUAL_SWITCH_QLIMIT = 10000
    EXTERNAL_TRANSMISSION_COFACTOR = 0.000001
    INTERNAL_TRANSMISSION_COFACTOR = 0.000001
    EXTERNAL_TRANSMISSION_COST = 5
    INTERNAL_TRANSMISSION_COST = 1
    CLUSTER_SIZE = 0
