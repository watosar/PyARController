import ui
import trackpad
import socketnetui
import arpositiontracker
import json

trans = str.maketrans({'(':'[',')':']'})

class ControllerUI(ui.View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update_interval = 1/15
        
        self.hand_id = 0
        self.name='右手'
        self.change_hand_button = ui.ButtonItem(
            title='change_hand',
            action=self.change_hand
        )
        self.right_button_items = [self.change_hand_button]
        
        self.trackpad = trackpad.Trackpad(
            frame=(0,self.frame.size.height-250-150,250,250),
            flex='LRT',
            bg_color='blue'
        )
        self.trackpadclicked_switch = ui.Switch(
            frame=(0, self.height-450, 100, 100),
            flex='LRT',
        )
        
        self.trigger = ui.Slider(
            frame=(0,self.height-150, 100, 30),
            flex='LRT'
        )
        
        self.socketcontroller = socketnetui.controllerUI(flex='RW')
        self.socketcontroller.width = self.width
        
        self.info_label = ui.Label(flex='W',scales_font=True,number_of_lines=0)
        self.info_label.y = 40
        
        self.arposcontrollui = arpositiontracker.ARTrackerControllerUI(flex='WT', bg_color='red')
        self.arposcontrollui.width = self.width
        
        self.add_subview(self.info_label)
        self.add_subview(self.socketcontroller)
        self.add_subview(self.trackpad)
        self.add_subview(self.trackpadclicked_switch)
        self.add_subview(self.trigger)
        self.add_subview(self.arposcontrollui)
    
    def change_hand(self, _):
        self.hand_id ^= 1
        self.name = ('右手', '左手')[self.hand_id]
    
    def update(self):
        data = {
            'id': self.hand_id, 
            'trackpad': self.trackpad.getValue(), 
            'clicked': self.trackpadclicked_switch.value, 
            'trigger': int(self.trigger.value*100)/100,
            **self.arposcontrollui.getPosition()
        }
        datas = json.dumps(data)
        self.info_label.text = datas
        if self.socketcontroller.is_connected:
            self.socketcontroller.sendall(datas.encode()+b'\0')
        
    def will_close(self):
        self.socketcontroller.socket_close()
        self.arposcontrollui.will_close()
        

if __name__ == '__main__':
    v = ControllerUI(bg_color='white')
    v.socketcontroller.addr_host_input.text = '192.168.137.1'
    v.socketcontroller.addr_port_input.text = '27015'
    v.present('fullscreen')

