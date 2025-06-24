# motor_controller.py
import config
from motor_manager import MotorManager

motor_manager = None  # Burada global tanımlıyoruz, try/except ile init edeceğiz.

# ------------- [YENİ EKLENDİ] -------------
# Slider'dan gelen değerleri tutacağımız tampon sözlük
pending_slider_values = {}  # {motor_idx: en_son_slider_degeri}
# ------------------------------------------

def init_motor_manager():
    global motor_manager
    try:
        motor_manager = MotorManager(interface_name='enp3s0')
        motor_manager.initialize()
    except Exception as e:
        print(f"Error initializing EtherCAT network: {e}")
        motor_manager = None

def calculate_torque(torque):
    torque = float(torque)
    max_torque = 1.3
    return torque * (max_torque / 100)

def handle_switch(switch_var, switch_type):
    current_value = switch_var.get()
    if current_value == "on":
        config.switch_status[switch_type] += 1
    else:
        config.switch_status[switch_type] -= 1
    # clamp [0..4]
    config.switch_status[switch_type] = max(0, min(config.switch_status[switch_type], 4))
    print(f"Updated Status: {config.switch_status}")

def start_config():
    config.config_complete = True
    for key, value in config.switch_status.items():
        if value == 1:
            temp = key.split("_")
            if motor_manager is not None:
                try:
                    slave_index = config.motor_num[f"{temp[0]}_{temp[2]}"]
                    if temp[0] == "velocity":
                        motor_manager.configure_velocity_mode(slave_index)
                    else:
                        motor_manager.configure_position_mode(slave_index)
                    config.configured_slaves.append(slave_index)
                except Exception as e:
                    print(f"Error configuring motor: {e}")

# -------------------------------------------------------------------------
# Aşağıdaki fonksiyonda "SLIDER" ile ilgili kısım değiştirilmiştir.
# Eskiden burada anında set_position/set_velocity çağrısı vardı.
# Artık sadece pending_slider_values sözlüğüne değer kaydediyoruz.
# -------------------------------------------------------------------------
def on_motor_slider_change(slider_value, idx):
    if not config.config_complete or motor_manager is None:
        return

    slider_value_int = int(slider_value)
    if idx in [0, 2, 4, 6]:  # position motor
        # Log penceresine, "gönderildi" yerine "queued" benzeri ifade yazıyoruz
        config.logs[str(idx)].insert("end", f"Position value of {slider_value_int} queued\n")
        config.logs[str(idx)].see("end")
        # Anında göndermek yerine tampon sözlüğüne yaz
        pending_slider_values[idx] = slider_value_int

    else:  # velocity motor
        config.logs[str(idx)].insert("end", f"Velocity value of {slider_value_int} queued\n")
        config.logs[str(idx)].see("end")
        # Anında göndermek yerine tampon sözlüğüne yaz
        pending_slider_values[idx] = slider_value_int

# -------------------------------------------------------------------------
# YENİ EKLENEN Fonksiyon:
# Pending (tampon) sözlükte biriken slider değerlerini motorlara gerçekten gönderen kısım.
# -------------------------------------------------------------------------
def update_motors():
    """
    Belirli aralıklarla (ör. 100ms) çağrılıp pending_slider_values içindeki
    değerleri motor sürücüye gönderir.
    """
    if config.config_complete and motor_manager is not None:
        for idx, val in list(pending_slider_values.items()):
            # Pozisyon motoru mu, hız motoru mu bakıyoruz
            if idx in [0, 2, 4, 6]:
                # Orijinal koddaki gibi 0 veya 6 ise negatif çevirme
                send_val = -val if idx in [0, 6] else val
                motor_manager.set_position(idx, send_val)

                # Gönderildiğini de log'a yazabiliriz:
                config.logs[str(idx)].insert(
                    "end", f"Position value {send_val} has been sent to motor {idx}\n"
                )
                config.logs[str(idx)].see("end")
            else:
                motor_manager.set_velocity(idx, val)
                config.logs[str(idx)].insert(
                    "end", f"Velocity value {val} has been sent to motor {idx}\n"
                )
                config.logs[str(idx)].see("end")

        # Tüm tampon temizlenir
        pending_slider_values.clear()

def poll_data(root):
    # poll_data fonksiyonu, her 100 ms'de bir verileri okuyacak (ESKİ HALİYLE KALDI)
    if config.config_complete and motor_manager is not None:
        for motor_type in ["velocity", "position"]:
            for i in range(1,5):
                status_key = f"{motor_type}_motor_{i}"
                if config.switch_status.get(status_key, 0) != 1:
                    continue
                slave_idx = config.motor_num.get(f"{motor_type}_{i}")
                if slave_idx is None:
                    continue
                try:
                    params = motor_manager.get_all_r0_parameters(slave_idx)
                    load = params["R0.17_Motor_Load_Ratio"]
                    pos = params["R0.13_Encoder_Feedback_Value"]
                    vel = params["R0.00_Motor_Speed"]
                    torque = calculate_torque(params["R0.06_Current_Torque"])

                    error_code = params["R3.0"]
                    print(error_code)

                    config.shared_data[f"slave-{slave_idx}"] = {
                        "velocity": vel,
                        "position": pos,
                        "load": load,
                        "torque": torque,
                        "Voltage_of_Control_Power": params["R0.08_Voltage_of_Control_Power"],
                        "Output_Voltage": params["R0.09_Output_Voltage"],
                        "Output_Current": params["R0.10_Output_Current"],
                        "Drive_Temperature": params["R0.11_Drive_Temperature"]
                    }

                    state = params["R0.30_System_State"]
                    config.config_labels[f"{motor_type}_config_label_{i}"].configure(
                        text=config.state_meanings[int(state)],
                        text_color="green"
                    )

                    # Label güncellemeleri
                    if f"{motor_type}_load_{i}" in config.info_labels:
                        config.info_labels[f"{motor_type}_load_{i}"].configure(text=f"Load: {load:.1f}%")
                    if f"{motor_type}_position_{i}" in config.info_labels:
                        config.info_labels[f"{motor_type}_position_{i}"].configure(text=f"Position: {pos}")
                    if f"{motor_type}_velocity_{i}" in config.info_labels:
                        config.info_labels[f"{motor_type}_velocity_{i}"].configure(text=f"Velocity: {vel:.1f} r/min")
                    if f"{motor_type}_torque_{i}" in config.info_labels:
                        config.info_labels[f"{motor_type}_torque_{i}"].configure(text=f"Torque: {torque:.2f} N/m")

                except Exception as e:
                    print(f"Error reading parameters for slave {slave_idx}: {e}")

    # Tekrar schedule
    root.after(100, lambda: poll_data(root))
