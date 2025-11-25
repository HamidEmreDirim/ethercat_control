from flask import Flask
from flask_socketio import SocketIO, emit
import threading
import time
import motor_controller
import config
from collections import defaultdict, deque

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global flag for polling thread
polling_active = False
# Queue for motor commands: {motor_idx: deque([...])}
slider_queues = defaultdict(deque)

def update_motors_thread():
    """
    Background thread to process motor commands from the queue.
    Runs every ~10ms to send the latest command for each motor.
    """
    while True:
        if config.config_complete and motor_controller.motor_manager is not None:
            # Iterate over a copy of items to avoid runtime errors if dict changes
            for idx, q in list(slider_queues.items()):
                if not q:
                    continue
                
                # Get the last (most recent) value
                last_val = q.pop()
                q.clear() # Clear the rest of the queue
                
                try:
                    # Logic from motor_controller.py:
                    # Position motors are at indices 0, 2, 4, 6 (based on how they are mapped)
                    # But wait, config.motor_num maps "position_1" -> slave_idx.
                    # The UI sends 'index' 1-4.
                    # Let's rely on the slave_idx we get from config.motor_num.
                    
                    # However, the original code used `idx` in `slider_queues` as the SLAVE INDEX.
                    # The UI sends us (type, index). We need to resolve this to slave_idx BEFORE queuing
                    # or queue with slave_idx.
                    # Let's queue with slave_idx to match original logic closer.
                    
                    # Inversion logic from original: if idx in [0, 2, 4, 6] (which are position motors)
                    # send_val = -last_val if idx in [0, 6] else last_val
                    
                    # We need to know if it's a position or velocity motor to decide on inversion
                    # The original code used the slave_idx to decide.
                    # config.motor_num maps:
                    # velocity_1 -> 1, position_1 -> 0
                    # velocity_2 -> 3, position_2 -> 2
                    # velocity_3 -> 5, position_3 -> 4
                    # velocity_4 -> 7, position_4 -> 6
                    
                    if idx in [0, 2, 4, 6]: # It is a position motor
                        send_val = -last_val if idx in [0, 6] else last_val
                        motor_controller.motor_manager.set_position(idx, send_val)
                        # print(f"Set Position {idx} to {send_val}")
                    else: # Velocity motor
                        motor_controller.motor_manager.set_velocity(idx, last_val)
                        # print(f"Set Velocity {idx} to {last_val}")
                        
                except Exception as e:
                    print(f"Error updating motor {idx}: {e}")
        
        time.sleep(0.01) # 10ms

# Start the motor update thread immediately
t_update = threading.Thread(target=update_motors_thread)
t_update.daemon = True
t_update.start()

def poll_data_thread():
    global polling_active
    while polling_active:
        if config.config_complete and motor_controller.motor_manager is not None:
            data = {}
            for motor_type in ["velocity", "position"]:
                for i in range(1, 5):
                    status_key = f"{motor_type}_motor_{i}"
                    # Check if motor is enabled (logic from original poll_data)
                    if config.switch_status.get(status_key, 0) != 1:
                        continue
                    
                    slave_idx = config.motor_num.get(f"{motor_type}_{i}")
                    if slave_idx is None:
                        continue
                    
                    try:
                        params = motor_controller.motor_manager.get_all_r0_parameters(slave_idx)
                        # Extract relevant data
                        data[f"{motor_type}_{i}"] = {
                            "velocity": params.get("R0.00_Motor_Speed"),
                            "position": params.get("R0.13_Encoder_Feedback_Value"),
                            "load": params.get("R0.17_Motor_Load_Ratio"),
                            "torque": motor_controller.calculate_torque(params.get("R0.06_Current_Torque", 0)),
                            "state": params.get("R0.30_System_State"),
                            "voltage_control": params.get("R0.08_Voltage_of_Control_Power"),
                            "output_voltage": params.get("R0.09_Output_Voltage"),
                            "output_current": params.get("R0.10_Output_Current"),
                            "drive_temp": params.get("R0.11_Drive_Temperature")
                        }
                    except Exception as e:
                        print(f"Error reading slave {slave_idx}: {e}")
            
            if data:
                socketio.emit('status_update', data)
        
        time.sleep(0.1)

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('connect_ethercat')
def handle_connect_ethercat():
    print("Connecting to EtherCAT...")
    try:
        motor_controller.start_config()
        # Start polling thread if not already running
        global polling_active
        if not polling_active:
            polling_active = True
            t = threading.Thread(target=poll_data_thread)
            t.daemon = True
            t.start()
        emit('ethercat_connected', {'status': 'success'})
    except Exception as e:
        emit('ethercat_connected', {'status': 'error', 'message': str(e)})

@socketio.on('set_motor_command')
def handle_motor_command(data):
    # data: { 'type': 'velocity'|'position', 'index': 1-4, 'value': float }
    try:
        m_type = data.get('type')
        idx = data.get('index')
        value = float(data.get('value'))
        
        motor_key = f"{m_type}_{idx}"
        slave_idx = config.motor_num.get(motor_key)
        
        if slave_idx is not None:
            # Push to queue instead of setting directly
            slider_queues[slave_idx].append(value)
            # print(f"Queued {m_type} {idx} (Slave {slave_idx}): {value}")
            
    except Exception as e:
        print(f"Error queuing motor command: {e}")

@socketio.on('toggle_switch')
def handle_toggle_switch(data):
    # data: { 'type': 'velocity_motor_1', 'state': 'on'|'off' }
    try:
        switch_type = data.get('type')
        state = data.get('state')
        
        # Update config logic
        if state == "on":
            config.switch_status[switch_type] += 1
        else:
            config.switch_status[switch_type] -= 1
        config.switch_status[switch_type] = max(0, min(config.switch_status[switch_type], 4))
        
        print(f"Switch {switch_type} toggled to {state}. Status: {config.switch_status[switch_type]}")
    except Exception as e:
        print(f"Error toggling switch: {e}")

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
