from pygame import Rect
from tingbot.graphics import Surface


class WidgetBase(object):

    @staticmethod
    def _anchor(align):
        mapping = {
            'topleft': (0, 0),
            'left': (0, 0.5),
            'bottomleft': (0, 1),
            'top': (0.5, 0),
            'center': (0.5, 0.5),
            'bottom': (0.5, 1),
            'topright': (1, 0),
            'right': (1, 0.5),
            'bottomright': (1, 1),
        }
    
        return mapping[align]
    
    @staticmethod
    def _xy_add(t1, t2):
        return t1[0] + t2[0], t1[1] + t2[1]
    
    @staticmethod
    def _xy_subtract(t1, t2):
        return t1[0] - t2[0], t1[1] - t2[1]
    
    @staticmethod
    def _xy_multiply(t1, t2):
        return t1[0] * t2[0], t1[1] * t2[1]
    
    def _xy_from_align(self, align, surface_size):
        return self._xy_multiply(surface_size, self._anchor(align))
    
    def _topleft_from_aligned_xy(self, xy, align, size, surface_size):
        if xy is None:
            xy = self._xy_from_align(align, surface_size)
    
        anchor_offset = self._xy_multiply(self._anchor(align), size)
        return self._xy_subtract(xy, anchor_offset)

    def __init__(self, parent, name, xy=None, size=(100, 100), align='center'):
        self.parent = parent

        self.name = name
        self.action = None

        self.enabled = True

        self.screen = Surface(
            parent.screen.surface.subsurface(
                Rect(
                    self._topleft_from_aligned_xy(xy, align, size, parent.screen.size),
                    size
                )
            )
        )
        
        self.xy = (0, 0)
        self.align = 'topleft'

        self.hitarea = Rect(
            self.xy,
            size
        )

    def move_to(self, xy=None, align='center'):
        self.screen = Surface(
            self.parent.screen.surface.subsurface(
                Rect(
                    self._topleft_from_aligned_xy(xy, align, self.screen.size, self.parent.screen.size),
                    self.screen.size
                )
            )
        )

    def render(self):
        pass
    
    def on_touch(self, xy, action):
        pass
