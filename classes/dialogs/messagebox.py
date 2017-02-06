from ..base import DialogBase
from ..utils import Utils


class MessageBox(DialogBase):
    
    def __init__(self, parent, message, callback):
        super(MessageBox, self).__init__(parent)
        
        self.message = message
        self.callback = callback
        
        self.create_widgets()

    def create_widgets(self):

        def ok_action():
            self.callback()
            self.close()
            
        self.create_widget(
            'button',
            'ok',
            ok_action,
            xy=(150, 150),
            size=(110, 35),
            align='bottom',
            color=self.colors.button.active.font,
            background=self.colors.button.active.background,
            text='OK',
            font=Utils.get_font_resource('akkuratstd-light.ttf'),
            font_size=24
        )
        
    def render(self):
        super(MessageBox, self).render()
        
        self.screen.fill((self.colors.background[0], self.colors.background[1], self.colors.background[2], 210))
        
        self.screen.text(self.message, xy=(150, 90), color=self.colors.font, align='center', font=Utils.get_font_resource('akkuratstd-light.ttf'), font_size=24, max_width=self.parent.screen.width - 20)
        self.get_widget('ok').render()
