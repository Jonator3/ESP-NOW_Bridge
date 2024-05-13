import time

import serial
from threading import Thread


class ESP_NOW_BRIDGE(object):

    def __init__(self, port="/dev/ttyUSB0", baudrate=230400, *, on_receive=lambda data, source: None, on_send=lambda success: None, debug=False):
        self.esp = serial.Serial(port, baudrate)
        self.port = port
        self.baudrate = baudrate
        self.debug = debug

        self.on_receive = on_receive
        self.on_send = on_send

        self.default_target = "ff:ff:ff:ff:ff:ff"
        self.mac = None

        self.thread = Thread(target=self._loop)
        self.thread.daemon = True

        self.thread.start()
        self.esp.write(int(self.default_target.replace(":", ""), 16).to_bytes(6, "big")+(0).to_bytes(1)+b'\n')
        time.sleep(0.1)

    def send(self, data, target=None):
        if len(data) == 0:
            raise ValueError("Empty input")
        if type(data) == str:
            if not data.isascii():
                raise ValueError("Data must be ascii string")
            if data.__contains__("\n"):  # split message into single lines
                for line in data.split("\n"):
                    self.send(line, target)
                return
            data = data.encode("ascii")
        if target is None:
            target = self.default_target

        mac = int(target.replace(":", ""), 16)

        byte_data = mac.to_bytes(6, byteorder="big")+ len(data).to_bytes(1)+ data +"\n".encode("ascii")
        self.esp.write(byte_data)
        if self.debug:
            print(">>>", byte_data)

    def _loop(self):
        while True:
            data = self.esp.readline()
            if self.debug:
                print("<<<", data)
            if data.startswith(b'msg:'):
                self.on_receive(data[10:-2], data[4:10].hex(":", 1))
            elif data.startswith(b'snd:'):
                self.on_send(data[4:-2] == b'1')
            elif data.startswith(b'mac:'):
                self.mac = data[4:-2].decode("ascii")


def decoder(byte_str):
    msg = ""
    for byte in byte_str:
        if byte >= 128:
            break
        msg += chr(byte)
    return msg


if __name__ == "__main__":
    def receiver(msg, source):
        print(source, ">>", decoder(msg))


    def sender(state):
        if not state:
            print("Sending failed!")
    esp = ESP_NOW_BRIDGE(on_receive=receiver, on_send=sender)
    print("Running ESP-NOW Bridge on:", esp.mac)
    while True:
        msg = input()
        esp.send(msg)
