from rubicon.objc import ObjCClass

try:
    from objc_arhandler import ARSessionHandler
except RuntimeError:
    ARSessionHandler = ObjCClass('ARSessionHandler')

import objc_util
import ui

class ARPositionTracker:
    def __init__(self):
        self.arsessionhandler = ARSessionHandler.new()
        self.arsessionhandler.did_update_session_info = self.did_update_session_info
        self.position = {'translation': None, 'rotation':None}
    
    @objc_util.on_main_thread
    def start(self):
        self.arsessionhandler.start()
    
    def pause(self):
        self.arsessionhandler.pause()
    
    def did_update_session_info(self, info: str):
        print(info)
    
    def getPosition(self):
        if not self.arsessionhandler or not self.arsessionhandler.session.currentFrame: 
            return {}
        t = repr(self.arsessionhandler.session.currentFrame.camera)
        pos = self.position
        for i in t[t.rfind('<')+1:-4].split(') '):
            for key,value in (i.split('=('),):
                pos[key] = [float(i) for i in value.replace('°','').split()] 
        return pos
    
    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if name == 'did_update_session_info':
            self.arsessionhandler.did_update_session_info = self.did_update_session_info


class ARTrackerControllerUI(ui.View):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.arpositiontracker = ARPositionTracker()
        self.ar_button = ui.Button(
            title='start',
            bg_color='gray',
            action=self.ar_button_action
        )
        self.ar_button.width = 120
        self.ar_info_label = ui.Label(
            text='ar session info',
            frame=(80,20,self.width-80, self.height),
            flex='W'
        )
        self.arpositiontracker.did_update_session_info = self.did_update_session_info
    
        self.add_subview(self.ar_button)
        self.add_subview(self.ar_info_label)
    
    def getPosition(self):
        return self.arpositiontracker.getPosition()
    
    def did_update_session_info(self, text):
        self.ar_info_label.text = text
        print('info:', text)
        
    def ar_button_action(self, sender):
        if sender.title == 'start':
            self.arpositiontracker.start()
            sender.title = 'pause'
            sender.width = 120
        elif sender.title == 'pause':
            self.arpositiontracker.pause()
            sender.title = 'start'
    
    def will_close(self):
        self.arpositiontracker.pause()
        

if __name__ == '__main__':
    ar = ARTrackerControllerUI(bg_color='red')
    ar.present()
