from ..base.widgetbase import WidgetBase
from ..utils import Utils
from tingbot.utils import call_with_optional_arguments


class Checkbox(WidgetBase):
    
    def __init__(self, parent, name, xy=None, size=(100, 100), color='white', background=None, align='center', text=None, font=None, font_size=18, icon_size=36, enabled=True, checked=False, value=None):
        super(Checkbox, self).__init__(parent, name,  xy=xy, size=size, align=align)

        self.notice = ''
        self.text = text
        self.size = size
        self.color = color
        self.background = background
        self.font = font
        self.font_size = font_size
        self.icon_size = icon_size
        self.enabled = enabled
        self.checked = checked
        self.value = value

    def toggle(self):
        if self.enabled is True:
            if self.checked is True:
                self.checked = False
            else:
                self.checked = True
        
    def render(self):
        super(Checkbox, self).render()
        
        if self.background is not None:
            self.screen.rectangle(xy=self.xy, size=self.size, color=self.background, align=self.align)
        
        if self.checked is True:
            icon = u'\ue834'
        else:
            icon = u'\ue835'
        
        rel_xy = self._xy_add(
            self.xy,
            (0, self.size[1] / 2)
        )
        buttonXY = self._xy_add(
            rel_xy,
            (
                self.icon_size * 0.10,
                0,
            )
        )
        textXY = self._xy_add(
            rel_xy,
            (
                self.icon_size * 1.20,
                0,
            )
        )
        self.screen.text(icon, xy=buttonXY, color=self.color, align='left', font=Utils.get_font_resource('icons.ttf'), font_size=self.icon_size)
        self.screen.text(self.text, xy=textXY, color=self.color, align='left', font=self.font, font_size=self.font_size, max_width=self.size[0] - self.size[0] * 0.20, max_height=self.size[1])

    def on_touch(self, xy, action):
        super(Checkbox, self).on_touch(xy, action)
        
        rel_xy = self._xy_subtract(
            xy,
            self.screen.surface.get_abs_offset()
        )
        if self.enabled and action == 'down' and self.hitarea.collidepoint(rel_xy) and self.action is not None:
            call_with_optional_arguments(self.action, name=self.name)
