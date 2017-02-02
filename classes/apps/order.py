from dotmap import DotMap
from ..base import AppBase
from ..utils import Utils
from ..dialogs import MessageBox, Confirm
import tingbot


class Order(AppBase):
    
    def __init__(self, parent):
        super(Order, self).__init__(parent)

        self.supplies = DotMap(tingbot.app.settings['order']['products'])
        for product in self.supplies.toDict().keys():
            self.supplies[product].font = tuple(self.supplies[product].font)
            self.supplies[product].background = tuple(self.supplies[product].background),

        self.colors.background = (65, 190, 198)
        self.colors.font = (244, 245, 245)

        count = 0
        col = 0
        row = 0
        for k, v in self.supplies.iteritems():
            width = 95
            if col % 2 == 0:
                width = 94
            self.create_widget(
                'button',
                k,
                self.confirm,
                xy=(10 + (col * 95 + col * 8), (5 + (row * 95 + row * 8))),
                size=(width, 95),
                color=self.colors.font,
                background=self.colors.background,
                align='topleft',
                text=v.name,
                font=Utils.get_font_resource('akkuratstd-light.ttf'),
                font_size=18,
                icon=v.icon,
                icon_size=48,
                enabled=True
            )
            count += 1
            col += 1
            
            if count % 3 == 0:
                col = 0
                row += 1

    def confirm(self, name):
        def yes_action():
            self.order(name)
        
        def noop():
            pass
        
        self.open_dialog(Confirm(self, message='Are you shure that ' + name + ' ' + self.supplies[name].conjunction + ' missing? Did you look?', yes_callback=yes_action, no_callback=noop))
        
    def order(self, name):
        self.parent.say('OK. Thank you for telling me that ' + name + '  ' + self.supplies[name].conjunction + ' missing!')

        for receiver in self.supplies[name].receiver:
            msg = "Hi " + receiver[0] + ",\n\n"
            msg += "someone is pretty sure that "+name+" is missing! Please order it and everybody will be happy again. ;-)\n"
            msg += "\nThank you.\n\n"
            msg += "\nKind regards\n"
            msg += "The coffee bot.\n"
            Utils.sendmail(receiver[1], receiver[0], 'Order', msg)

        self.open_dialog(MessageBox(self, message='Thank You', callback=self.close))
        self.state.needsRender = True

    def render(self):
        super(Order, self).render()

        self.screen.fill(color=self.colors.background)

        for k, v in self.widgets.iteritems():
            v.widget.render()
