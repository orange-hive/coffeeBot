from ..base.widgetbase import WidgetBase
from ..utils import Utils


class Button(WidgetBase):
    
    def __init__(self, parent, name, xy=None, size=(100, 100), color='white', background=None, align='center', text=None, font=None, font_size=18, icon=None, icon_size=48, enabled=True):
        super(Button, self).__init__(parent, name,  xy=xy, size=size, align=align)

        self.text = text
        self.size = size
        self.color = color
        self.background = background
        self.font = font
        self.font_size = font_size
        self.icon = icon
        self.icon_size = icon_size
        self.enabled = enabled
        
    def render(self):
        super(Button, self).render()
        
        if self.background is not None:
            self.screen.rectangle(xy=self.xy, size=self.size, color=self.background, align=self.align)
        
        if self.text is not None:
            buttonXY = self._xy_add(
                self.xy,
                self._xy_multiply(
                    self.size,
                    self._anchor('center')
                )
            )
            if self.icon is not None:
                
                if self.text is not None:
                    buttonXY = self._xy_subtract(
                        buttonXY,
                        (
                            0,
                            self.size[1] * 0.1
                        )
                    )
                    textXY = self._xy_add(
                        buttonXY,
                        (
                            0,
                            self.size[1] * 0.5
                        )
                    )
                    self.screen.text(self.icon, xy=buttonXY, color=self.color, align='center', font=Utils.get_font_resource('icons.ttf'), font_size=self.icon_size)
                    self.screen.text(self.text, xy=textXY, color=self.color, align='bottom', font=self.font, font_size=self.font_size, max_width=self.size[0], max_height=self.size[1])
                else:
                    self.screen.text(self.icon, xy=buttonXY, color=self.color, align='center', font=Utils.get_font_resource('icons.ttf'), font_size=self.icon_size)

            else:
                self.screen.text(self.text, xy=buttonXY, color=self.color, align='center', font=self.font, font_size=self.font_size, max_width=self.size[0], max_height=self.size[1])

    def on_touch(self, xy, action):
        super(Button, self).on_touch(xy, action)
        
        rel_xy = self._xy_subtract(
            xy,
            self.screen.surface.get_abs_offset()
        )
        if self.enabled and action == 'down' and self.hitarea.collidepoint(rel_xy) and self.action is not None:
            self.action(self.name)
