from dotmap import DotMap
from tingbot.graphics import Surface
from controllerbase import ControllerBase


class AppBase(ControllerBase):

    def __init__(self, parent):
        super(AppBase, self).__init__(parent)
        self.screen = Surface(parent.screen.surface.subsurface((0, 25, 320, 215)))

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
