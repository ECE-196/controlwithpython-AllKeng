from __future__ import annotations
from serial import Serial, SerialException
from serial.tools.list_ports import comports
#########################################################################################
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.messagebox import showerror
from threading import Thread, Lock # we'll use Lock later ;)

def detached_callback(f):
    return lambda *args, **kwargs: Thread(target=f, args=args, kwargs=kwargs).start()

S_OK: int = 0xaa
S_ERR: int = 0xff

#with Serial('/your/port', 9600) as ser:
 #   ser.write(bytes([0x1]))
  #  print(ser.read() == bytes([0xaa]))
#
 #   ser.write(bytes([0x0]))
  #  print(ser.read() == bytes([0xaa]))
#
 #   ser.write(bytes([0x2]))
  #  print(ser.read() == bytes([0xff]))

############################################################################################
class LockedSerial(Serial):
    _lock: Lock = Lock()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def read(self, size=1) -> bytes:
        with self._lock:
            return super().read(size)

    def write(self, b: bytes, /) -> int | None:
        with self._lock:
            super().write(b)

    def close(self):
        with self._lock:
            super().close()


#######################################################################################
class SerialPortal(tk.Toplevel):
    def __init__(self, parent: App):
        super().__init__(parent)

        self.geometry("300x300")
        self.parent = parent
        self.parent.withdraw() # hide App until connected

        ttk.OptionMenu(self, parent.port, 'Click here to pick a port', *[d.device for d in comports()]).place(relx=.5, rely=0.35, anchor="center")
        ttk.Button(self, text='Connect', command=self.connect, default='active').place(relx=.5, rely=0.5, anchor="center")

    def connect(self):
        self.parent.connect()
        self.destroy()
        self.parent.deiconify() # reveal App

class App(tk.Tk):
    ser: Serial
    def __init__(self):
        super().__init__()

        self.title("LED Blinker")
        self.geometry("300x300")
        self.port = tk.StringVar()
        self.led = tk.BooleanVar()

        check1 = ttk.Checkbutton(self, text ='Toggle LED', variable=self.led, command=self.update_led).place(relx=.5, rely=0.35, anchor="center")
        button1 = ttk.Button(self, text = 'Send invalid', command=self.send_invalid).place(relx=.5, rely=0.5, anchor="center")
        button2 = ttk.Button(self, text = 'Disconnect', default='active', command=self.disconnect).place(relx=.5, rely=0.65, anchor="center")
        #check1.pack()

        SerialPortal(self) # and this

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.disconnect()

    def connect(self):
        self.ser = LockedSerial(self.port.get())

    @detached_callback
    def update_led(self):
        self.write(bytes([self.led.get()]))

    def disconnect(self):
        self.ser.close()

        SerialPortal(self) # display portal to reconnect

    def send_invalid(self):
       self.write(bytes([0x10]))

    def write(self, b: bytes):
        try:
            self.ser.write(b)
            if int.from_bytes(self.ser.read(), 'big') == S_ERR:
                showerror('Device Error', 'The device reported an invalid command.')
        except SerialException:
            showerror('Serial Error', 'Write failed.')


if __name__ == '__main__':
    with App() as app: 
        app.mainloop()
