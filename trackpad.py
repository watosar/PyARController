import ui

class Trackpad(ui.View):
    def __init__(self,**kwargs):
        super().__init__(
            content_mode=ui.CONTENT_SCALE_ASPECT_FIT,
            **kwargs
        )
        self.track_aria_margin = 50
        self.track_aria_radius = self.frame[2]/2 - self.track_aria_margin
        self.track_image_view = ui.ImageView(image=ui.Image.named('iob:ios7_circle_filled_32'),alpha=0.5)
        self.add_subview(self.track_image_view)
        self.hw, self.hh = 0, 0
    
    def getValue(self):
        x,y = self.track_image_view.center
        return int((x-self.hw)/self.track_aria_radius*100)/100, int((self.hh-y)/self.track_aria_radius*100)/100
        
    def touch_began(self, touch):
        self.track_image_view.alpha = 1.0
        self.touch_moved(touch)
    
    def touch_moved(self, touch):
        x,y = map(float.__sub__ ,touch.location, (self.hw, self.hh))
        r = self.track_aria_radius**2 / (x**2+y**2)
        #print(r)
        if r<1:
            r **= .5
            x *= r
            y *= r
        width = self.track_image_view.width /2
        self.track_image_view.x = x+self.hw - width
        self.track_image_view.y = y+self.hh - width
    
    def touch_ended(self, touch):
        width = self.track_image_view.width /2
        self.track_image_view.x = self.hw - width
        self.track_image_view.y = self.hh - width
        self.track_image_view.alpha = 0.5
        
    def layout(self):
        self.hw, self.hh = self.width/2, self.height/2
        width = self.track_image_view.width /2
        self.track_image_view.x = self.hw - width
        self.track_image_view.y = self.hh - width
        self.set_needs_display()
        
    def draw(self):
        frame = self.frame
        margin = self.track_aria_margin
        R = frame[2]/2 - margin
        self.track_aria_radius = R
        circle_path = ui.Path.oval(margin, frame[3]/2-R, R*2, R*2)
        circle_path.line_width = 2
        ui.set_color('white')
        circle_path.stroke()
        
if __name__ == '__main__':
    v = Trackpad(bg_color='blue')
    v.present('fullscreen')
    
