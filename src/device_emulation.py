import serial
import serial.tools.list_ports
import time
from datetime import datetime
import random

# 流程参考 https://iot.mi.com/v2/new/doc/resources-and-services/personal-developer/embedded-dev#%E8%AE%BE%E5%A4%87%E9%85%8D%E7%BD%91

# 基本配置
DEVICE_MODEL = 'perdev.switch.004'
DEVICE_PID = '18031'
MCU_VERSION = '0001'

SWITCH_STATUS = 'true'
IS_RANDOM_CHANGE_STATE = True

def scan_serial_ports():
    ports = serial.tools.list_ports.comports()
    available_ports = []
    for index, (port, desc, hwid) in enumerate(sorted(ports), start=1):
        print("{}. {}: {} [hwid: {}]".format(index, port, desc, hwid))
        available_ports.append((str(index), port))
    return dict(available_ports)

def user_select_port(available_ports):
    while True:
        choice = input("请选择一个串口（输入对应的编号）: ")
        if choice in available_ports:
            return available_ports[choice]
        else:
            print("无效的选择，请重新输入。")

def send_command(ser, command, expected_response):
    ser.write(command.encode('utf-8'))
    time.sleep(0.1)
    response = ser.readline().decode('utf-8').rstrip()
    if expected_response in response:
        print("{} 【成功】发送指令 '{}' 收到响应: {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), command.strip(), response.strip()))
        return True
    else:
        print("{} 【失败】发送指令 '{}' 收到响应: {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), command.strip(), response.strip()))
        return False

wait_time = random.randint(9, 30)
def randomly_change_state(ser):
    global wait_time
    global SWITCH_STATUS
    global IS_RANDOM_CHANGE_STATE

    if IS_RANDOM_CHANGE_STATE is False:
        return
    
    wait_time = wait_time - 1
    if wait_time <= 0:
        wait_time = random.randint(9, 30)
        send_command(ser, "properties_changed {} {} {}\r".format(2, 1, SWITCH_STATUS), "ok")
        if SWITCH_STATUS == 'true':
            SWITCH_STATUS = 'false'
        else:
            SWITCH_STATUS = 'true'

def main():
    print("扫描可用的串口...")
    available_ports = scan_serial_ports()
    if not available_ports:
        print("未发现可用的串口。")
        return
    selected_port = user_select_port(available_ports)
    print("您选择了串口: {}".format(selected_port))
    
    try:
        ser = serial.Serial(selected_port, 115200, timeout=1)
        print("已连接到 {}，波特率 115200 ...".format(selected_port))
        print("==================================================")
        print("准备发送指令完成小米IoT通用模组基本设置...")

        # 设置设备model并检查响应
        if not send_command(ser, "model {}\r".format(DEVICE_MODEL), "ok"):
            raise Exception("设备model设置失败")

        # 查询设备model并检查响应
        if not send_command(ser, "model\r", DEVICE_MODEL):
            raise Exception("设备model查询失败")

        # 设置蓝牙配网相关信息并检查响应
        if not send_command(ser, "ble_config set {} {}\r".format(DEVICE_PID, MCU_VERSION), "ok"):
            raise Exception("蓝牙配网信息设置失败")

        # 检查蓝牙配网信息并检查响应
        if not send_command(ser, "ble_config dump\r", DEVICE_PID):
            raise Exception("蓝牙配网信息检查失败")

        # 设置MCU固件版本并检查响应
        if not send_command(ser, "mcu_version {}\r".format(MCU_VERSION), "ok"):
            raise Exception("MCU固件版本设置失败")
        
        print("==================================================")
        print("小米IoT通用模组基本设置完成，进入命令处理流程...")
        while True:
            ser.write('get_down\r'.encode('utf-8'))
            data = ser.readline().decode('utf-8').rstrip()
            print("{} get data: {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data))
            cmd_parse = data.split(' ')
            if len(cmd_parse) > 2:
                if cmd_parse[1] == 'set_properties':
                    send_command(ser, "result 2 1 0\r", "ok")
                    send_command(ser, "properties_changed {} {} {}\r".format(cmd_parse[2], cmd_parse[3], cmd_parse[4]), "ok")
                    SWITCH_STATUS = cmd_parse[4]
                elif cmd_parse[1] == 'get_properties':
                    send_command(ser, "result 2 1 0 {}\r".format(SWITCH_STATUS), "ok")
            randomly_change_state(ser)
            time.sleep(0.1)

    except Exception as e:
        print("发生错误:", e)
    finally:
        ser.close()
        print("串口已关闭。")

if __name__ == "__main__":
    main()
