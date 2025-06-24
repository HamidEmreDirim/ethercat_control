# config.py

switch_status = {
    "velocity_motor_1": 1, "velocity_motor_2": 1, "velocity_motor_3": 1, "velocity_motor_4": 1,
    "position_motor_1": 1, "position_motor_2": 1, "position_motor_3": 1, "position_motor_4": 1
}

motor_num = {
    "position_1": 0, "velocity_1": 1,
    "position_2": 2, "velocity_2": 3,
    "position_3": 4, "velocity_3": 5,
    "position_4": 6, "velocity_4": 7
}

state_meanings = {
    0: "Initialization",
    1: "The high voltage",
    2: "Ready",
    3: "Operation",
    4: "Forced to stop",
    5: "Fault",
    6: "STO-In"
}

# shared_data, config_labels, motor_sliders, logs, etc. gibi dict'leri de burada tutabilirsiniz:
shared_data = {
    "slave-0": {}, "slave-1": {}, "slave-2": {}, "slave-3": {},
    "slave-4": {}, "slave-5": {}, "slave-6": {}, "slave-7": {}
}

configured_slaves = []
config_labels = {}
motor_sliders = {}
logs = {}
slider_ids = {}
info_labels = {}

data_logs_for_csv = {}





config_complete = False
all_motor_connected = True
