# serial_communicator.py
import serial
import time
import binascii

# 串口配置（可根据需要调整）
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 115200
TIMEOUT = 1


class SerialCommunicator:
    def __init__(self, port=SERIAL_PORT, baud_rate=BAUD_RATE, timeout=TIMEOUT):
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.ser = None

    def connect(self):
        """连接到串口设备"""
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout
            )
            print(f"已连接到 {self.ser.name}，波特率 {self.baud_rate}")
            return True
        except serial.SerialException as e:
            print(f"串口连接错误: {e}")
            return False

    def disconnect(self):
        """断开串口连接"""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("串口连接已关闭")

    def send_fixed_hex(self, hex_data):
        """
        向下位机发送固定的16进制数据

        参数:
        hex_data: 要发送的16进制数据字符串 (例如: "AABBCCDDEEFF")

        返回:
        bool: 发送是否成功
        str: 收到的响应数据(16进制格式)，若无响应则为空字符串
        """
        if not self.ser or not self.ser.is_open:
            if not self.connect():
                return False, ""

        try:
            # 预处理16进制数据
            clean_hex = hex_data.replace(" ", "").replace(",", "").replace("0x", "").replace("\\x", "")

            # 验证是否为有效16进制
            if not all(c in "0123456789ABCDEFabcdef" for c in clean_hex):
                print("错误: 包含非16进制字符")
                return False, ""

            if len(clean_hex) % 2 != 0:
                print("错误: 16进制数据长度应为偶数")
                return False, ""

            # 将16进制字符串转换为字节数据
            binary_data = binascii.unhexlify(clean_hex)

            # 发送数据
            self.ser.write(binary_data)
            print(f"已发送 {len(binary_data)} 字节: {hex_data}")

            # 添加延时确保数据发送完成
            time.sleep(0.1)

            # 接收下位机响应
            response_hex = ""
            if self.ser.in_waiting:
                response = self.ser.read(self.ser.in_waiting)
                response_hex = binascii.hexlify(response).decode('utf-8').upper()
                print(f"收到响应: {response_hex}")
            else:
                print("未收到响应")

            return True, response_hex

        except serial.SerialException as e:
            print(f"串口错误: {e}")
            return False, ""
        except binascii.Error as e:
            print(f"16进制转换错误: {e}")
            return False, ""
        except Exception as e:
            print(f"意外错误: {e}")
            return False, ""

    def send_location_command(self, area):
        """
        发送位置命令到下位机

        参数:
        area: 区域代码 (如 'A', 'B', 'C')
        shelf: 书架编号 (整数)

        返回:
        bool: 发送是否成功
        str: 收到的响应数据
        """
        # 将区域转换为ASCII码的十六进制表示
        area_hex = binascii.hexlify(area.encode('ascii')).decode('ascii').upper()

        # 将书架编号转换为两位十六进制
        # shelf_hex = f"{shelf:02X}"

        # 组合命令 (例如: "A3" -> "4133" 其中41是'A'的十六进制，33是'3'的十六进制)
        command = area_hex

        return self.send_fixed_hex(command)