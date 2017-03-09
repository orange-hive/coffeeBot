from ..base import DialogBase
from ..utils import Utils
from math import ceil


class MusicFolderDialog(DialogBase):
    
    def __init__(self, parent, folder=[], active_folder=[], callback=None):
        super(MusicFolderDialog, self).__init__(parent)
        
        self.callback = callback
        
        self.state.selectedFolder = active_folder
        self.settings.availableFolder = folder

        self.colors.button.active.background = (255, 222, 45)
        self.colors.button.active.font = (0, 0, 0)

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
            font_color=self.colors.button.active.font,
            container_size=(300, (ceil(len(self.settings.availableFolder) / 5.0) * 5) * (height + padding))
        )

        def checkbox_action(name):
            self.get_widget('container').state.needs_render = True
            self.state.needs_render = True
            checkbox = self.get_widget('container').get_widget(name)
            if checkbox.checked is True:
                self.state.selectedFolder.append(checkbox.value)
            else:
                self.state.selectedFolder.remove(checkbox.value)

        xy = (10, 0)
        print self.settings.availableFolder
        for folder in self.settings.availableFolder:
            print folder
            self.create_widget(
                'checkbox',
                'button_' + folder,
                checkbox_action,
                container,
                xy=xy,
                size=(260, height),
                align='topleft',
                color=(255, 255, 255),
                text=folder,
                font=Utils.get_font_resource('akkuratstd-light.ttf'),
                font_size=20,
                icon_size=20,
                value=folder,
                checked=(folder in self.state.selectedFolder)
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
                self.callback(name, folder=self.state.selectedFolder)
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
        super(MusicFolderDialog, self).render()
        
        self.screen.fill((self.colors.background[0], self.colors.background[1], self.colors.background[2], 210))
        
        self.get_widget('container').render()
        self.get_widget('cancel').render()
        self.get_widget('ok').render()
