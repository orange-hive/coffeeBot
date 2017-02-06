from ..base import DialogBase
from ..utils import Utils


class Confirm(DialogBase):
    
    def __init__(self, parent, message, yes_callback, no_callback):
        super(Confirm, self).__init__(parent)
        
        self.message = message
        self.yesCallback = yes_callback
        self.noCallback = no_callback
        
        self.create_widgets()

    def create_widgets(self):

        def yes_action():
            self.yesCallback()
            self.close()
            
        def no_action():
            self.noCallback()
            self.close()

        self.create_widget(
            'button',
            'yes',
            yes_action,
            xy=(90, 150),
            size=(110, 35),
            align='bottom',
            color=self.colors.button.active.font,
            background=self.colors.button.active.background,
            text='Yes',
            font=Utils.get_font_resource('akkuratstd-light.ttf'),
            font_size=24
        )

        self.create_widget(
            'button',
            'no',
            no_action,
            xy=(210, 150),
            size=(110, 35),
            align='bottom',
            color=self.colors.button.active.font,
            background=self.colors.button.active.background,
            text='No',
            font=Utils.get_font_resource('akkuratstd-light.ttf'),
            font_size=24
        )
        
    def render(self):
        super(Confirm, self).render()
        
        self.screen.fill((self.colors.background[0], self.colors.background[1], self.colors.background[2], 210))
        
        self.screen.text(self.message, xy=(150, 70), color=self.colors.font, align='center', font=Utils.get_font_resource('akkuratstd-light.ttf'), font_size=24, max_width=self.parent.screen.width - 20)
        self.get_widget('yes').render()
        self.get_widget('no').render()
