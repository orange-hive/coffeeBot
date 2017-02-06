from dotmap import DotMap
from ..widgets import Button, Checkbox, ScrollArea
from time import time
from tingbot.utils import call_with_optional_arguments


class ControllerBase(object):

    def __init__(self, parent):
        self.parent = parent

        self.state = DotMap(
            keepActive=False,
            needs_render=True
        )
        self.persistentState = DotMap()
        self.settings = DotMap()
        self.widgets = DotMap()
        self.dialog = None
        
    def get_state(self):
        return self.state

    def set_state(self, state):
        self.state = state

    def init_states(self, **kwargs):
        for name, value in kwargs.iteritems():
            self.state[name] = value

    def get_persistent_state(self):
        return self.persistentState

    def set_persistent_state(self, persistent_state):
        self.persistentState = persistent_state

    def init_persistent_states(self, **kwargs):
        for name, value in kwargs.iteritems():
            self.persistentState[name] = value

    def init_settings(self, **kwargs):
        for name, value in kwargs.iteritems():
            self.settings[name] = value

    def keep_active(self):
        return self.state.keepActive or (self.has_dialog() is True and self.dialog.keep_active() is True)
        
    def background(self):
        pass

    def foreground(self):
        pass
    
    def render(self):
        print 'render ' + str(time()) + ' - ' + self.__class__.__name__

        self.state.needs_render = False
        
    def update(self, execution_type='fg'):
        if execution_type == 'fg':
            self.foreground()
            if self.state.needs_render is True or (self.has_dialog() is True and self.dialog.state.needs_render is True):
                self.render()
                if self.has_dialog() is True and self.dialog.state.needs_render is True:
                    self.dialog.render()
        else:
            self.background()

    def create_widget(self, widget_type, name, callback=None, parent=None, **kwargs):
        if parent is None:
            parent = self
        
        def noop():
            pass

        if callback is None:
            callback = noop

        if name in self.widgets.toDict().keys():
            raise Exception('Widget ' + name + ' already defined in ' + self.__class__.__name__)
            
        if widget_type == 'button':
            widget = Button(parent, name, **kwargs)

            def default_action():
                noop()
        elif widget_type == 'checkbox':
            widget = Checkbox(parent, name, **kwargs)

            def default_action():
                widget.toggle()
        elif widget_type == 'scrollarea':
            widget = ScrollArea(parent, name, **kwargs)
            
            def default_action():
                noop()
        else:
            raise Exception('unknown control of type ' + widget_type)
            
        def action():
            call_with_optional_arguments(default_action, name=name)
            call_with_optional_arguments(callback, name=name)
            
        widget.action = action

        parent.widgets[name] = DotMap(
            widget=widget,
            type=widget_type
        )

        return parent.widgets[name].widget
            
    def get_widget(self, name):
        if name not in self.widgets.toDict().keys():
            raise Exception('Widget ' + name + ' not found in ' + self.__class__.__name__)
        return self.widgets[name].widget

    def disable_all_widgets(self):
        for k, v in self.widgets.iteritems():
            v.widget.enabled = False

    def on_touch(self, xy, action):
        if self.has_dialog() is False:
            for k, v in self.widgets.iteritems():
                v.widget.on_touch(xy, action)
        else:
            self.dialog.on_touch(xy, action)

    def open_dialog(self, dialog):
        if self.dialog is not None:
            self.dialog.close()
            
        self.dialog = dialog
        self.state.needs_render = True

    def close_dialog(self):
        if self.dialog is not None:
            self.dialog.cleanup()
            
        self.dialog = None
        self.state.needs_render = True

    def has_dialog(self):
        return self.dialog is not None
