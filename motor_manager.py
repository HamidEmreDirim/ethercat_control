import pysoem
import ctypes
import time
import struct


reverse_motors = [0, 1, 2, 3, 5, 7]
motor_rotation_for_one_degree = 27.777777778 * 105.26
# buyuk arac motor_rotation_for_one_degree = 27.777777778 * 138.53

class MotorManager:
    def __init__(self, interface_name):
        self.interface_name = interface_name
        self.master = pysoem.Master()
        self.slaves = []
        self.open()

    def open(self):
        self.master.open(self.interface_name)
        print(f"EtherCAT master opened on {self.interface_name}.")

    def initialize(self):
        if self.master.config_init() > 0:
            self.slaves = self.master.slaves
            #self.slaves.insert(1, self.slaves[6])
            print(f"Found {len(self.slaves)} slave(s).")
            if len(self.slaves) < 1:
                raise Exception("No slaves found.")
            # Gerekirse slaves'e config_map veya config_dc gibi ilave konfigürasyon ekleyebilirsiniz.
            self.master.config_map()
            self.master.state = pysoem.SAFEOP_STATE
            self.master.write_state()
            # Her slave SAFEOP_STATE'e geçene kadar bekle
            for i in range(100):
                self.master.read_state()
                if all(sl.state == pysoem.SAFEOP_STATE for sl in self.slaves):
                    break
                time.sleep(0.01)
            if not all(sl.state == pysoem.SAFEOP_STATE for sl in self.slaves):
                raise Exception("Failed to bring all slaves into SAFEOP_STATE.")
        else:
            raise Exception("Failed to initialize EtherCAT network.")

    def close(self):
        self.master.close()
        print("EtherCAT master closed.")

    #----------------------
    # Position Mode Methods
    #----------------------
    def configure_position_mode(self, slave_index):
        """Belirtilen slave'i pozisyon moduna alır ve operasyonel hale getirir."""
        try:
            slave = self.slaves[slave_index]
            # Mode of Operation: Position Mode = 7
            slave.sdo_write(0x6060, 0, bytes(ctypes.c_int8(7)))  
            time.sleep(0.1)

            # Operational moda geçiş için kontrol word ayarları:
            # Shutdown state
            slave.sdo_write(0x6040, 0, bytes(ctypes.c_uint16(0x0006))) 
            time.sleep(0.1)
            # Switch on
            slave.sdo_write(0x6040, 0, bytes(ctypes.c_uint16(0x0007))) 
            time.sleep(0.1)
            # Enable operation
            slave.sdo_write(0x6040, 0, bytes(ctypes.c_uint16(0x000F))) 
            time.sleep(0.1)

            print(f"Slave {slave_index} configured in Position Mode.")
        except Exception as e:
            print(f"Error configuring slave {slave_index} in Position Mode: {e}")

    def set_position(self, slave_index, target_position):
        """Hedef pozisyonu (Target Position) ayarlar."""
        try:
            slave = self.slaves[slave_index]
            if target_position < -180:
                print("POSITION LIMIT EXEECED SEND A VALUE BETWEEN -180 and +180!")
                raise
            if target_position > 180:
                print("POSITION LIMIT EXEECED SEND A VALUE BETWEEN -180 and +180!")
                raise


            target_position = target_position * motor_rotation_for_one_degree
            target_position = int(round(target_position))


            # Hedef pozisyonu yaz
            if (slave_index in reverse_motors):
                target_position = target_position * -1
            slave.sdo_write(0x607A, 0, bytes(ctypes.c_int32(target_position)))
            # Yeni hedefin işlenmesi için kontrol kelimesi güncellemesi gerekebilir.
            # Genellikle position modda 0x6040'da "New set-point" bitini set edip reset etmek gerekir.
            # Bu genellikle 0x6040 kontrol kelimesindeki bitleri kullanarak yapılır.
            # Burada basitçe tekrar enable operation komutu gönderiyoruz:
            slave.sdo_write(0x6040, 0, bytes(ctypes.c_uint16(0x001F))) 
            # Tekrar esas konuma dön
            slave.sdo_write(0x6040, 0, bytes(ctypes.c_uint16(0x000F))) 
            print(f"Set position of slave {slave_index} to {target_position}.")
        except Exception as e:
            print(f"Error setting position for slave {slave_index}: {e}")

    #----------------------
    # Velocity Mode Methods

    def configure_velocity_mode(self, slave_index):
        try:
            slave = self.slaves[slave_index]
           ##asd 
            slave.sdo_write(0x6060, 0, bytes(ctypes.c_int8(3)))  # Velocity Mode
            slave.sdo_write(0x6046, 2, bytes(ctypes.c_int16(3000)))  # Max velocity
            slave.sdo_write(0x6040, 0, bytes(ctypes.c_uint16(0x0007)))  # Switch on
            slave.sdo_write(0x6040, 0, bytes(ctypes.c_uint16(0x000F)))  # Operational mode
            print(f"Slave {slave_index} configured in Velocity Mode.")
        except Exception as e:
            print(f"Error configuring slave {slave_index} in Velocity Mode: {e}")

    def set_velocity(self, slave_index, target_velocity):
        try:
            
            slave = self.slaves[slave_index]
            if target_velocity > 500:
                print("Too fast send value between -500 and +500")
                raise
            if target_velocity < -500:
                print("Too fast send value between -500 and +500")
                raise
           
           
            if (slave_index in reverse_motors):
                target_velocity = target_velocity * -1
                slave.sdo_write(0x60FF, 0, bytes(ctypes.c_int32(target_velocity)))  # Target velocity
            
            
            slave.sdo_write(0x60FF, 0, bytes(ctypes.c_int32(target_velocity)))  # Target velocity

            print(f"Set velocity of slave {slave_index} to {target_velocity}.")
        except Exception as e:
            print(f"Error setting velocity for slave {slave_index}: {e}")

    def stop_all(self):
        """Tüm motorları durdur."""
        for i, slave in enumerate(self.slaves):
            try:
                slave.sdo_write(0x6040, 0, bytes(ctypes.c_uint16(0x0002)))  # Disable operation
                slave.sdo_write(0x6040, 0, bytes(ctypes.c_uint16(0x0000)))  # Shutdown
                print(f"Stopped slave {i}.")
            except Exception as e:
                print(f"Error stopping slave {i}: {e}")

    
    # Yardımcı veri okuma fonksiyonları

    def _read_sdo_16bit_signed(self, slave_index, index, subindex=0):
        try:
            data = self.slaves[slave_index].sdo_read(index, subindex)

            # Eğer veri eksikse, hata at
            if data is None or len(data) < 2:
                raise ValueError(f"Expected at least 2 bytes, got {len(data) if data else 0} bytes.")

            # Eğer veri tam olarak 2 byte ise, 16-bit signed integer olarak işle
            if len(data) == 2:
                value = struct.unpack("<h", data)[0]  # Little-endian signed 16-bit
                return value

            # Eğer veri 4 byte ise, 32-bit signed integer olarak işle
            elif len(data) == 4:
                value = struct.unpack("<i", data)[0]  # Little-endian signed 32-bit
                return value

            # Eğer veri başka bir uzunlukta ise, hata at
            else:
                raise ValueError(f"Unexpected data length: {len(data)} bytes. Data: {data}")

        except Exception as e:
            print(f"Error reading 16-bit signed parameter {index}:{subindex} for slave {slave_index}: {e}")
            return None


    def _read_sdo_32bit_signed(self, slave_index, index, subindex=0):
        try:
            data = self.slaves[slave_index].sdo_read(index, subindex)
            if len(data) < 4:
                raise ValueError(f"Expected 4 bytes, got {len(data)} bytes.")
            return struct.unpack("<i", data)[0]  # 32-bit signed
        except Exception as e:
            print(f"Error reading 32-bit signed parameter {index}:{subindex}: {e}")
            return None
        
    
    def get_current_torque(self, slave_index):
        """Get R0.06 Current Torque."""
        try:
            raw_value = self._read_sdo_16bit_signed(slave_index, 0x3006, 0x00)
            if raw_value is not None:
                return raw_value / 10.0  # % olarak değer
            return None
        except Exception as e:
            print(f"Error reading R0.06_Current_Torque for slave {slave_index}: {e}")
            return None

    def get_voltage_of_control_power(self, slave_index):
        """Get R0.08 Voltage of Control Power."""
        try:
            raw_value = self._read_sdo_16bit_signed(slave_index, 0x3008, 0x00)
            if raw_value is not None:
                return raw_value / 10.0  # Volt olarak değer
            return None
        except Exception as e:
            print(f"Error reading R0.08_Voltage_of_Control_Power for slave {slave_index}: {e}")
            return None

    def get_output_voltage(self, slave_index):
        """Get R0.09 Output Voltage."""
        try:
            raw_value = self._read_sdo_16bit_signed(slave_index, 0x3009, 0x00)
            if raw_value is not None:
                return raw_value / 10.0  # Vrms olarak değer
            return None
        except Exception as e:
            print(f"Error reading R0.09_Output_Voltage for slave {slave_index}: {e}")
            return None

    def get_output_current(self, slave_index):
        """Get R0.10 Output Current."""
        try:
            raw_value = self._read_sdo_16bit_signed(slave_index, 0x300A, 0x00)
            if raw_value is not None:
                return raw_value / 100.0  # Arms olarak değer
            return None
        except Exception as e:
            print(f"Error reading R0.10_Output_Current for slave {slave_index}: {e}")
            return None

    def get_operation_time(self, slave_index):
        """Get R0.34 Operation Time."""
        try:
            raw_value = self._read_sdo_32bit_signed(slave_index, 0x3022, 0x00)
            if raw_value is not None:
                return raw_value  # Saniye olarak değer
            return None
        except Exception as e:
            print(f"Error reading R0.34_Operation_Time for slave {slave_index}: {e}")
            return None
    
    def get_drive_temperature(self, slave_index):
        """Get R0.11 Drive Temperature."""
        try:
            raw_value = self._read_sdo_16bit_signed(slave_index, 0x300B, 0x00)
            if raw_value is not None:
                return raw_value / 10.0  # ℃ olarak değer
            return None
        except Exception as e:
            print(f"Error reading R0.11_Drive_Temperature for slave {slave_index}: {e}")
            return None

        # R0 grubundaki tüm değerleri okuyan metot
    def get_all_r0_parameters(self, slave_index=0):
        params = {}
        errors = []

        def safe_read(func, *args, param_name):
            try:
                return func(*args)
            except Exception as e:
                errors.append((param_name, str(e)))
                return None

        def safe_divide(value, divisor):
            if value is None:
                return None
            try:
                return value / divisor
            except Exception as e:
                print(f"Error dividing {value} by {divisor}: {e}")
                return None

        # Motor Speed (R0.00)
        params["R0.00_Motor_Speed"] = safe_divide(
            safe_read(self._read_sdo_32bit_signed, slave_index, 0x3000, 0x00, param_name="R0.00_Motor_Speed"),
            10.0
        )
        # Encoder Feedback Value (R0.13)
        params["R0.13_Encoder_Feedback_Value"] = safe_read(
            self._read_sdo_32bit_signed, slave_index, 0x300D, 0x00, param_name="R0.13_Encoder_Feedback_Value"
        )

        params["R0.11_Drive_Temperature"] = safe_divide(
            safe_read(self._read_sdo_16bit_signed, slave_index, 0x300B, 0x00, param_name="R0.11_Drive_Temperature"),
            10.0
        )
        # Motor Load Ratio (R0.17)
        params["R0.17_Motor_Load_Ratio"] = safe_divide(
            safe_read(self._read_sdo_16bit_signed, slave_index, 0x3011, 0x00, param_name="R0.17_Motor_Load_Ratio"),
            10.0
        )
        
        params["R0.06_Current_Torque"] = safe_divide(
            safe_read(self._read_sdo_16bit_signed, slave_index, 0x3006, 0x00, param_name="R0.06_Current_Torque"),
            10.0
        )
        # Voltage of Control Power (R0.08)
        params["R0.08_Voltage_of_Control_Power"] = safe_divide(
            safe_read(self._read_sdo_16bit_signed, slave_index, 0x3008, 0x00, param_name="R0.08_Voltage_of_Control_Power"),
            10.0
        )
        # Output Voltage (R0.09)
        params["R0.09_Output_Voltage"] = safe_divide(
            safe_read(self._read_sdo_16bit_signed, slave_index, 0x3009, 0x00, param_name="R0.09_Output_Voltage"),
            10.0
        )
        # Output Current (R0.10)
        params["R0.10_Output_Current"] = safe_divide(
            safe_read(self._read_sdo_16bit_signed, slave_index, 0x300A, 0x00, param_name="R0.10_Output_Current"),
            100.0
        )
        # Operation Time (R0.34)
        params["R0.34_Operation_Time"] = safe_read(
            self._read_sdo_32bit_signed, slave_index, 0x3022, 0x00, param_name="R0.34_Operation_Time"
        )
        # System State (R0.30)
        params["R0.30_System_State"] = safe_read(
            self._read_sdo_16bit_signed, slave_index, 0x301E, 0x00, param_name="R0.30_System_State"
        )
        params["R3.0"] = safe_read(
            self._read_sdo_16bit_signed, slave_index, 0x3111, 0x00, param_name="R3.0"
        )

        # Hataları yazdır
        for param_name, error_msg in errors:
            print(f"Error reading {param_name}: {error_msg}")

        return params
