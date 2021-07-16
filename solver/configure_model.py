from config import DELIMITER
DEFAULT_MODEL = DELIMITER+"solver"+DELIMITER+"model"+DELIMITER+"cityscape_work_well.pt"
DEFAULT_MODEL_KNOWNLEDGE = ['bicycle','car','truck', 'bus', 'motorcycle', 'traffic light','vehicles']
SPECIFIC_MODEL = {
    "bicycle":DELIMITER+"solver"+DELIMITER+"model"+DELIMITER+"bicycle_shufflenet_v2_x0_5.pt",
    "bus":DELIMITER+"solver"+DELIMITER+"model"+DELIMITER+"bus_shufflenet_v2_x0_5.pt",
    "car":DELIMITER+"solver"+DELIMITER+"model"+DELIMITER+"car_shufflenet_v2_x0_5.pt",
    "crosswalk":DELIMITER+"solver"+DELIMITER+"model"+DELIMITER+"crosswalk_shufflenet_v2_x0_5.pt",
    "a fire hydrant":DELIMITER+"solver"+DELIMITER+"model"+DELIMITER+"fire_hydrant_shufflenet_v2_x0_5.pt"
}