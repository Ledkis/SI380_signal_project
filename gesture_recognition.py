# -*- encoding : utf-8 -*-



def init_gesture_data_base(path = "data/gesture_data_base/):
    gesture_data_base = {}    
    for file_name in os.listdir(path):
        file = open(file_name, "r").read()
        for data in file:
            
        
