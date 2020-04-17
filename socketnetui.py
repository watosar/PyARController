import ui
import socket

class controllerUI(ui.View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_connected = False
        self.addr_input_view = ui.View(
            frame=(0,0,100,24),
            flex='RW'
        )
        self.addr_host_input = ui.TextField(
            frame=(0,0,50,24),
            flex='RW',
            placeholder='host'
        )
        self.addr_port_input = ui.TextField(
            frame=(50,0,50,24),
            flex='LW',
            placeholder='port'
        )
        self.addr_view = ui.View(
            frame=(0,0,150,24),
            flex='LW',
            bg_color='white'
        )
        self.bind_button = ui.Button(
            frame=(100,-7,50,24),
            flex='LW',
            title='CONNECT',
            font=('<system-bold>', 20),
            action=lambda s:
                self.connect(
                    (self.addr_host_input.text, int(self.addr_port_input.text or '0'))
                )
        )
        
        self.addr_input_view.add_subview(self.addr_host_input)
        self.addr_input_view.add_subview(self.addr_port_input)
        self.addr_view.add_subview(self.addr_input_view)
        self.addr_view.add_subview(self.bind_button)
        self.add_subview(self.addr_view)
        
        self.addr_view.width = self.width/2
        
    def connect(self, addr):
        try:
            self.socket.connect(addr)
            self.is_connected = True
            self.addr_host_input.enabled = False
            self.addr_port_input.enabled = False
            self.bind_button.title = 'CLOSE'
            self.bind_button.action = self.socket_close
        except Exception:
            self.socket.close()
    
    def sendall(self, msg):
        self.socket.sendall(msg)
    
    def socket_close(self, *_):
        print('socket close')
        self.is_connected = False
        self.socket.close()
        self.addr_host_input.enabled = True
        self.addr_port_input.enabled = True
        self.bind_button.title = 'CONNECT'
        self.bind_button.action = self.connect

if __name__ == '__main__':
    v = controllerUI()
    v.present('fullscreen')
