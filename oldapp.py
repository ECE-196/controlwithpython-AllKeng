from __future__ import annotations
from threading import Thread, Lock
from serial import Serial, SerialException
from serial.tools.list_ports import comports

import tkinter as tk
import tkinter.ttk as ttk
from tkinter.messagebox import showerror

S_OK: int = 0xaa
S_ERR: int = 0xff

def detached_callback(f):
    return lambda *args, **kwargs: Thread(target=f, args=args, kwargs=kwargs).start()

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

class SerialPortal(tk.Toplevel):
    def __init__(self, parent: App):
        super().__init__(parent)
        
        self.parent = parent
        self.parent.withdraw()
        
        ttk.OptionMenu(self, parent.port, '', *[d.device for d in comports()]).pack()
        ttk.Button(self, text='Connect', command=self.connect, default='active').pack()
        
    @detached_callback
    def connect(self):
        self.parent.connect()
        self.destroy()
        self.parent.deiconify()

class App(tk.Tk):
    ser: LockedSerial
    
    def __init__(self):
        super().__init__()
        
        self.title("LED Blinker")
        
        self.port = tk.StringVar()
        self.led = tk.BooleanVar()
        
        ttk.Checkbutton(self, text='Toggle LED', variable=self.led, command=self.update_led).pack()
        ttk.Button(self, text='Send Invalid', command=self.send_invalid).pack()
        ttk.Button(self, text='Disconnect', command=self.disconnect, default='active').pack()
        
        SerialPortal(self)
        
    @detached_callback
    def connect(self):
        self.ser = LockedSerial(self.port.get())
    
    @detached_callback
    def disconnect(self):
        self.ser.close()
            
        SerialPortal(self)
            
    @detached_callback
    def update_led(self):
        self.write(bytes([self.led.get()]))
                
    @detached_callback
    def send_invalid(self):
        self.write(bytes([0x10]))
        
    def write(self, b: bytes):
        try:
            self.ser.write(b)
            if int.from_bytes(self.ser.read(), 'big') == S_ERR:
                showerror('Device Error', 'The device reported an invalid command.')
        except SerialException:
            showerror('Serial Error', 'Write failed.')
        
    def __enter__(self):
        return self
    
    def __exit__(self, *_):
        self.disconnect()
        
if __name__ == '__main__':
    with App() as app:
        app.mainloop()