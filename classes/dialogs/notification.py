from collections import OrderedDict
from ..base import DialogBase
from ..utils import Utils
from math import ceil


class NotificationDialog(DialogBase):
    
    def __init__(self, parent, receiver=None, callback=None):
        super(NotificationDialog, self).__init__(parent)
        
        self.callback = callback
        
        self.state.selectedReceiver = {}

        receiver_tuple = []
        if receiver is not None:
            for r in receiver:
                receiver_tuple.append(
                    (
                        r[0],
                        (
                            r[1][0],
                            r[1][1],
                        )
                    )
                )

        self.settings.availableReceiver = OrderedDict(receiver_tuple)

        self.create_widgets()

    def create_widgets(self):
        height = 30
        padding = 2
        
        container = self.create_widget(
            'scrollarea',
            'container',
            xy=(0, 0),
            size=(300, 160),
            align='topleft',
            color=self.colors.button.active.background,
            container_size=(300, (ceil(len(self.settings.availableReceiver) / 5.0) * 5) * (height + padding))
        )

        def checkbox_action(name):
            self.get_widget('container').state.needs_render = True
            self.state.needs_render = True
            checkbox = self.get_widget('container').get_widget(name)
            if checkbox.checked is True:
                self.state.selectedReceiver[checkbox.value] = self.settings.availableReceiver[checkbox.value]
            else:
                del self.state.selectedReceiver[checkbox.value]

        xy = (10, 0)
        for key, user in self.settings.availableReceiver.iteritems():
            self.create_widget(
                'checkbox',
                'button_' + key,
                checkbox_action,
                container,
                xy=xy,
                size=(260, height),
                align='topleft',
                color=self.colors.button.active.font,
                text=user[0],
                font=Utils.get_font_resource('akkuratstd-light.ttf'),
                font_size=20,
                icon_size=20,
                value=key
            )
            
            xy = self._xy_add(xy, (0, height + padding))

        def cancel_action(name):
            if self.callback is not None:
                self.callback(name)
            self.close()
            
        self.create_widget(
            'button',
            'cancel',
            cancel_action,
            xy=(165, 170),
            size=(110, 35),
            align='topleft',
            color=self.colors.button.active.font,
            background=self.colors.button.active.background,
            text='Cancel',
            font=Utils.get_font_resource('akkuratstd-light.ttf'),
            font_size=24
        )
        
        def ok_action(name):
            if self.callback is not None:
                self.callback(name, notifications=self.state.selectedReceiver)
            self.close()
        
        self.create_widget(
            'button',
            'ok',
            ok_action,
            xy=(25, 170),
            size=(110, 35),
            align='topleft',
            color=self.colors.button.active.font,
            background=self.colors.button.active.background,
            text='Ok',
            font=Utils.get_font_resource('akkuratstd-light.ttf'),
            font_size=24
        )

    def render(self):
        super(NotificationDialog, self).render()
        
        self.screen.fill((self.colors.background[0], self.colors.background[1], self.colors.background[2], 210))
        
        self.get_widget('container').render()
        self.get_widget('cancel').render()
        self.get_widget('ok').render()
