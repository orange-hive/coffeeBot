from dotmap import DotMap
from tingbot.graphics import Surface
from controllerbase import ControllerBase
import pygame


class AppBase(ControllerBase):

    def __init__(self, parent):
        super(AppBase, self).__init__(parent)
        self.screen = Surface(parent.screen.surface.copy().subsurface((0, 25, 320, 215)))
        self.parentScreen = parent.screen

        self.colors = DotMap({
            'background': (44, 51, 56),
            'font': (244, 245, 245),
            'highlight': (236, 65, 93),
            'button': {
                'active': {
                    'font': (244, 245, 245),
                    'background': (236, 65, 93),
                },
                'inactive': {
                    'font': (107, 112, 116),
                    'background': (65, 71, 76)
                }
            }
        })
        
    def close(self):
        self.parent.set_active_app(self.parent.settings.defaultApp)

    def post_render(self):
        super(AppBase, self).post_render()
        self.parentScreen.surface.set_clip(pygame.Rect(0, 25, 320, 215))
        self.parentScreen.fill((0, 0, 0))
        self.parentScreen.surface.blit(self.screen.surface, (0, 25), None, pygame.BLEND_RGBA_ADD)
        self.parentScreen.surface.set_clip(None)
