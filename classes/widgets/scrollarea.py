import pygame
from container import Container
from ..utils import Utils


class ScrollArea(Container):

    def __init__(self, parent, name, xy=None, size=(100, 100), align='center', container_size=None, color=None, font_color=None):
        
        super(ScrollArea, self).__init__(parent, name,  xy=xy, size=size, align=align, container_size=container_size)
        
        self.scrollbarWidth = 40
        self.buttonHeight = 40
        
        self.scrollbarButtonUp = pygame.Rect(self.containerScreen.width - self.scrollbarWidth, 0, self.scrollbarWidth, self.buttonHeight)
        self.scrollbarButtonDown = pygame.Rect(self.containerScreen.width - self.scrollbarWidth, self.containerScreen.height - self.buttonHeight, self.scrollbarWidth, self.buttonHeight)
        
        self.scrollbar = pygame.Rect(self.containerScreen.width - self.scrollbarWidth, self.scrollbarButtonUp.height, self.scrollbarWidth, self.containerScreen.height - self.scrollbarButtonDown.height)

        self.color = color
        if font_color is None:
            self.font_color = (255, 255, 255)
        else:
            self.font_color = font_color
        
        if self.window is not None:
            self.window.width = self.window.width - self.scrollbar.width

    def render(self):
        super(ScrollArea, self).render()
        
        if self.color is not None:
            pygame.draw.rect(self.containerScreen.surface, self.color, self.hitarea, 1)
            pygame.draw.rect(self.containerScreen.surface, self.color, self.scrollbar, 1)

            pygame.draw.rect(self.containerScreen.surface, self.color, self.scrollbarButtonUp)
            self.containerScreen.text(u'\ue5c7', xy=(self.scrollbarButtonUp.x, self.scrollbarButtonUp.y), color=self.font_color, align='topleft', font=Utils.get_font_resource('icons.ttf'), font_size=40)
            pygame.draw.rect(self.containerScreen.surface, self.color, self.scrollbarButtonDown)
            self.containerScreen.text(u'\ue5c5', xy=(self.scrollbarButtonDown.x, self.scrollbarButtonDown.y), color=self.font_color, align='topleft', font=Utils.get_font_resource('icons.ttf'), font_size=40)

    def on_touch(self, xy, action):
        rel_xy = self._xy_subtract(
            xy,
            self.containerScreen.surface.get_abs_offset()
        )
        
        if self.scrollbarButtonUp.collidepoint(rel_xy[0], rel_xy[1]):
            if action == 'down':
                if self.window is not None:
                    self.window.y -= self.containerScreen.height / 1
                    if self.window.y < 0:
                        self.window.y = 0
                    self.parent.state.needs_render = True
        elif self.scrollbarButtonDown.collidepoint(rel_xy[0], rel_xy[1]):
            if action == 'down':
                if self.window is not None:
                    self.window.y += self.containerScreen.height / 1
                    if self.window.y > self.screen.height - self.window.height:
                        self.window.y = self.screen.height - self.window.height
                    self.parent.state.needs_render = True
        else:
            super(ScrollArea, self).on_touch(xy, action)
