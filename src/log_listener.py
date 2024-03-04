import serial
import serial.tools.list_ports
import time

def scan_serial_ports():
    """扫描并列出当前系统下的所有可用串口"""
    ports = serial.tools.list_ports.comports()
    available_ports = []
    for index, (port, desc, hwid) in enumerate(sorted(ports), start=1):
        print(f"{index}. {port}: {desc} [hwid: {hwid}]")
        available_ports.append(port)
    return available_ports

def user_select_port(available_ports):
    """让用户从列表中选择一个串口"""
    index_to_port = {str(index): port for index, port in enumerate(available_ports, start=1)}
    while True:
        choice = input("请选择一个串口（输入对应的编号）: ")
        if choice in index_to_port:
            return index_to_port[choice]
        else:
            print("无效的选择，请重新输入。")

def open_and_listen_port(port):
    """打开并监听选定的串口"""
    try:
        ser = serial.Serial(port, 115200, timeout=1)
        print(f"已连接到 {port}，正在监听数据（按 CTRL+C 结束）...")
        while True:
            if ser.in_waiting:
                data = ser.readline().decode('utf-8').rstrip()
                print(f"接收到数据: {data}")
            time.sleep(0.1)
    except serial.SerialException as e:
        print(f"串口错误: {e}")
    except KeyboardInterrupt:
        print("程序已手动中断。")
    finally:
        ser.close()
        print("串口已关闭。")

def main():
    print("扫描可用的串口...")
    available_ports = scan_serial_ports()
    if not available_ports:
        print("未发现可用的串口。")
        return
    selected_port = user_select_port(available_ports)
    print(f"您选择了串口: {selected_port}")
    open_and_listen_port(selected_port)

if __name__ == "__main__":
    main()
