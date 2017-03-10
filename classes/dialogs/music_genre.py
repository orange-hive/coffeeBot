from ..base import DialogBase
from ..utils import Utils
from math import ceil


class MusicGenreDialog(DialogBase):
    
    def __init__(self, parent, genres=[], active_genres=[], callback=None):
        super(MusicGenreDialog, self).__init__(parent)
        
        self.callback = callback
        
        self.state.selectedGenres = active_genres
        self.settings.availableGenres = genres

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
            container_size=(300, (ceil(len(self.settings.availableGenres) / 5.0) * 5) * (height + padding))
        )

        def checkbox_action(name):
            self.get_widget('container').state.needs_render = True
            self.state.needs_render = True
            checkbox = self.get_widget('container').get_widget(name)
            if checkbox.checked is True:
                self.state.selectedGenres.append(checkbox.value)
            else:
                self.state.selectedGenres.remove(checkbox.value)

        xy = (10, 0)
        print self.settings.availableGenres
        for genres in self.settings.availableGenres:
            print genres
            self.create_widget(
                'checkbox',
                'button_' + genres,
                checkbox_action,
                container,
                xy=xy,
                size=(260, height),
                align='topleft',
                color=(255, 255, 255),
                text=genres,
                font=Utils.get_font_resource('akkuratstd-light.ttf'),
                font_size=20,
                icon_size=20,
                value=genres,
                checked=(genres in self.state.selectedGenres)
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
                self.callback(name, genres=self.state.selectedGenres)
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
        super(MusicGenreDialog, self).render()
        
        self.screen.fill((self.colors.background[0], self.colors.background[1], self.colors.background[2], 210))
        
        self.get_widget('container').render()
        self.get_widget('cancel').render()
        self.get_widget('ok').render()
