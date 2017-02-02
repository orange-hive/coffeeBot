import pygame
from tingbot.graphics import Surface
from dotmap import DotMap
from ..base.widgetbase import WidgetBase


class Container(WidgetBase):

    def __init__(self, parent, name, xy=None, size=(100, 100), align='center', container_size=None):
        
        super(Container, self).__init__(parent, name,  xy=xy, size=size, align=align)
        
        self.state = DotMap(
            needs_render=True
        )
        
        self.containerScreen = self.screen
        self.window = None
        if container_size is not None:
            if container_size[0] > self.screen.size[0] or container_size[1] > self.screen.size[1]:
                self.screen = Surface(pygame.Surface(container_size))
                self.window = pygame.Rect(xy, size)
            
        self.widgets = DotMap()
        
    def render(self):
        super(Container, self).render()
        
        if self.state.needs_render is True:
            self.screen.fill((0, 0, 0))
            for k, v in self.widgets.iteritems():
                v.widget.render()
            self.state.needs_render = False
            
        if self.window is not None:
            self.containerScreen.surface.blit(self.screen.surface, (0, 0), self.window, pygame.BLEND_RGBA_ADD)
        
    def on_touch(self, xy, action):
        super(Container, self).on_touch(xy, action)
    
        if self.window is not None:
            xy = self._xy_subtract(
                xy,
                self.containerScreen.surface.get_abs_offset()
            )
            xy = self._xy_add(
                xy,
                (0, self.window.y)
            )

        if self.window is None or self.window.collidepoint(xy[0], xy[1]):
                for k, v in self.widgets.iteritems():
                    v.widget.on_touch(xy, action)
            
    def get_widget(self, name):
        if name not in self.widgets.toDict().keys():
            raise Exception('Widget ' + name + ' not found in container ' + self.name + ' in ' + self.parent.__class__.__name__)
        return self.widgets[name].widget

    def disable_all_widgets(self):
        for k, v in self.widgets.iteritems():
            v.widget.enabled = False
