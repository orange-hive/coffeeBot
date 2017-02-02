from dotmap import DotMap
from pygame import Rect
from tingbot.graphics import Surface
from controllerbase import ControllerBase


class DialogBase(ControllerBase):

    @staticmethod
    def _xy_add(t1, t2):
        return t1[0] + t2[0], t1[1] + t2[1]

    def __init__(self, parent, xy=(10, 0), size=(300, 205)):
        super(DialogBase, self).__init__(parent)
        self.screen = Surface(parent.screen.surface.subsurface(Rect(xy, size)))

        self.state.enabled = True
        
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

    def enable(self):
        self.state.enabled = True
            
    def disable(self):
        self.state.disable = False
            
    def close(self):
        self.close_dialog()
        self.parent.close_dialog()
        
    def cleanup(self):
        pass
