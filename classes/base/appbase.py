from dotmap import DotMap
from tingbot.graphics import Surface
from controllerbase import ControllerBase


class AppBase(ControllerBase):

    @staticmethod
    def _xy_subtract(t1, t2):
        return t1[0] - t2[0], t1[1] - t2[1]

    def __init__(self, parent):
        super(AppBase, self).__init__(parent)
        self.screen = Surface(parent.screen.surface.copy())

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

    def on_touch(self, xy, action):
        xy = self._xy_subtract(
            xy,
            (0, 25)
        )
        super(AppBase, self).on_touch(xy, action)

    def close(self):
        self.parent.set_active_app(self.parent.settings.defaultApp)

    def pre_render(self):
        super(AppBase, self).pre_render()
        self.screen.fill(self.colors.background)
