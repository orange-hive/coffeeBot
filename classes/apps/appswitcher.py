from ..base import AppBase
from ..utils import Utils


class AppSwitcher(AppBase):
    
    def __init__(self, parent, apps):
        super(AppSwitcher, self).__init__(parent)

        self.apps = apps

        count = 0
        col = 0
        row = 0
        for k, v in self.apps.iteritems():
            width = 95
            if col % 2 == 0:
                width = 94
            self.create_widget(
                'button',
                k,
                self.start_app,
                xy=(10 + (col * 95 + col * 8), (5 + (row * 95 + row * 8))),
                size=(width, 95),
                color=self.apps[k].font,
                background=self.apps[k].background,
                align='topleft',
                text=v.name,
                font=Utils.get_font_resource('akkuratstd-light.ttf'),
                font_size=18,
                icon=v.icon,
                icon_size=48,
                enabled=True
            )
            count += 1
            col += 1
            
            if count % 3 == 0:
                col = 0
                row += 1

    def start_app(self, name):
        self.parent.set_active_app(name)
        
    def render(self):
        super(AppSwitcher, self).render()

        self.screen.fill(color=self.colors.background)

        for k, v in self.widgets.iteritems():
            v.widget.render()
