import pygame
from dotmap import DotMap
import math
from ..base import AppBase
from ..dialogs import NotificationDialog
from ..utils import Utils
import tingbot


class Timer(AppBase):
    
    def __init__(self, parent, ticks_per_second):
        super(Timer, self).__init__(parent)

        self.init_states(
            countdown=0,
            countdownTicks=0,
            started=False
        )
        
        self.init_settings(
            ticksPerSecond=ticks_per_second,
            hotCountdownSeconds=5
        )

        self.notifications = {}

        self.channels = DotMap(
            system=pygame.mixer.Channel(0),
        )
        self.channels.system.set_volume(0.4)

        self.sounds = DotMap(
            countdownEnd=pygame.mixer.Sound(Utils.get_audio_resource("antique_alarm_clock_bell_ringing.wav"))
        )

        self.colors.button.active.background = (236, 65, 93)
        self.colors.button.active.dimmed = (107, 112, 116)
        
        self.create_widgets()

    def background(self):
        super(Timer, self).background()
        self.compute()

    def foreground(self):
        super(Timer, self).foreground()
        self.compute()

    def compute(self):
        if self.state.started is True:
            self.state.countdownTicks -= 1

            old_countdown = self.state.countdown

            if self.state.countdownTicks <= 0:
                self.sendmails()
                self.get_widget('notification').checked = False
                self.stop()
                self.play_countdown_end_sound()
            else:
                
                if self.state.countdownTicks <= self.settings.ticksPerSecond * self.settings.hotCountdownSeconds and self.state.countdownTicks % (self.settings.ticksPerSecond / 2) == 0:
                    self.state.needs_render = True

                mins, secs = divmod(int(math.ceil(1.0 * self.state.countdownTicks / self.settings.ticksPerSecond)), 60)
                self.state.countdown = mins * 60 + secs

            if old_countdown != self.state.countdown:
                self.state.needs_render = True

    def set_time(self, name):
        if name == 'tenUp' and self.state.countdown+600 < 3600:
            self.state.countdown += 600
        elif name == 'tenDown' and self.state.countdown >= 600:
            self.state.countdown -= 600
        elif name == 'oneUp' and self.state.countdown+60 < 3600:
            self.state.countdown += 60
        elif name == 'oneDown' and self.state.countdown >= 60:
            self.state.countdown -= 60
        elif name == 'tenthUp' and self.state.countdown+10 < 3600:
            self.state.countdown += 10
        elif name == 'tenthDown' and self.state.countdown >= 10:
            self.state.countdown -= 10
        elif name == 'hundredthUp' and self.state.countdown+5 < 3600:
            self.state.countdown += 5
        elif name == 'hundredthDown' and self.state.countdown >= 5:
            self.state.countdown -= 5
            
        self.state.needs_render = True
         
    def start(self):
        if self.state.countdown > 0 and (self.get_widget('notification').checked is False or len(self.notifications) > 0):
            if len(self.notifications) > 0:
                self.parent.say('OK. I will notify you by email.')
            self.state.started = True
            self.state.countdownTicks = self.state.countdown * self.settings.ticksPerSecond
        
        self.state.needs_render = True
        
    def stop(self):
        self.state.started = False
        self.state.countdown = 0
        self.state.countdownTicks = 0

        checkbox = self.get_widget('notification')
        checkbox.checked = False
        checkbox.move_to((15, 160), 'topleft')
        checkbox.notice = ''

        self.notifications = {}
        self.state.needs_render = True

    def open_notification_dialog(self):
        def callback(action, notifications=None):
            if notifications is None:
                notifications = {}

            checkbox = self.get_widget('notification')
            if action == 'cancel' or (action == 'ok' and len(notifications) == 0):
                checkbox.checked = False
                checkbox.move_to((15, 160), 'topleft')
                checkbox.notice = ''
                self.notifications = {}
            else:
                checkbox.checked = True
                checkbox.move_to((15, 150), 'topleft')
                self.notifications = notifications
                notify_notice = []
                for key, receiver in self.notifications.iteritems():
                    notify_notice.append(key)
                checkbox.notice = ', '.join(notify_notice)

            self.state.needs_render = True

        dialog = NotificationDialog(self, receiver=tingbot.app.settings['timer']['notificationReceiver'], callback=callback)
        self.open_dialog(dialog)

    def play_countdown_end_sound(self):
        self.channels.system.play(self.sounds.countdownEnd)

    def create_widgets(self):
            self.create_widget(
                'button',
                'tenUp',
                self.set_time,
                xy=(35, 13),
                size=(50, 30),
                color=self.colors.button.active.dimmed,
                background=self.colors.background,
                align='topleft',
                text=u'\ue316',
                font=Utils.get_font_resource('icons.ttf'),
                font_size=38
            )
    
            self.create_widget(
                'button',
                'tenDown',
                self.set_time,
                xy=(35, 108),
                size=(50, 30),
                color=self.colors.button.active.dimmed,
                background=self.colors.background,
                align='topleft',
                text=u'\ue313',
                font=Utils.get_font_resource('icons.ttf'),
                font_size=38
            )
    
            self.create_widget(
                'button',
                'oneUp',
                self.set_time,
                xy=(95, 13),
                size=(50, 30),
                color=self.colors.button.active.dimmed,
                background=self.colors.background,
                align='topleft',
                text=u'\ue316',
                font=Utils.get_font_resource('icons.ttf'),
                font_size=38
            )
    
            self.create_widget(
                'button',
                'oneDown',
                self.set_time,
                xy=(95, 108),
                size=(50, 30),
                color=self.colors.button.active.dimmed,
                background=self.colors.background,
                align='topleft',
                text=u'\ue313',
                font=Utils.get_font_resource('icons.ttf'),
                font_size=38
            )
            
            self.create_widget(
                'button',
                'tenthUp',
                self.set_time,
                xy=(175, 13),
                size=(50, 30),
                color=self.colors.button.active.dimmed,
                background=self.colors.background,
                align='topleft',
                text=u'\ue316',
                font=Utils.get_font_resource('icons.ttf'),
                font_size=38
            )
    
            self.create_widget(
                'button',
                'tenthDown',
                self.set_time,
                xy=(175, 108),
                size=(50, 30),
                color=self.colors.button.active.dimmed,
                background=self.colors.background,
                align='topleft',
                text=u'\ue313',
                font=Utils.get_font_resource('icons.ttf'),
                font_size=38
            )
    
            self.create_widget(
                'button',
                'hundredthUp',
                self.set_time,
                xy=(235, 13),
                size=(50, 30),
                color=self.colors.button.active.dimmed,
                background=self.colors.background,
                align='topleft',
                text=u'\ue316',
                font=Utils.get_font_resource('icons.ttf'),
                font_size=38
            )
    
            self.create_widget(
                'button',
                'hundredthDown',
                self.set_time,
                xy=(235, 108),
                size=(50, 30),
                color=self.colors.button.active.dimmed,
                background=self.colors.background,
                align='topleft',
                text=u'\ue313',
                font=Utils.get_font_resource('icons.ttf'),
                font_size=38
            )
    
            self.create_widget(
                'button',
                'start',
                self.start,
                xy=(195, 160),
                size=(110, 40),
                color=self.colors.button.active.font,
                background=self.colors.button.active.background,
                align='topleft',
                text='Start',
                font=Utils.get_font_resource('akkuratstd-light.ttf'),
                font_size=24
            )
            
            def notification_action():
                checkbox = self.get_widget('notification')
                if checkbox.checked is True:
                    self.parent.say('OK. Please select who I should notify!')
                    self.open_notification_dialog()
                else:
                    checkbox.move_to((15, 160), 'topleft')
                    checkbox.notice = ''
                    self.notifications = {}

                self.state.needs_render = True
            
            self.create_widget(
                'checkbox',
                'notification',
                notification_action,
                xy=(15, 160),
                size=(160, 40),
                color=self.colors.button.active.font,
                align='topleft',
                text='Notify by email',
                font=Utils.get_font_resource('akkuratstd-light.ttf'),
                font_size=18,
                icon_size=24
            )

            self.create_widget(
                'button',
                'stop',
                self.stop,
                xy=(95, 140),
                size=(130, 40),
                color=self.colors.button.active.font,
                background=self.colors.button.active.background,
                align='topleft',
                text='Stop',
                font=Utils.get_font_resource('akkuratstd-light.ttf'),
                font_size=24
            )
        
    def sendmails(self):
        for key, receiver in self.notifications.iteritems():
            msg = "Hello " + receiver[0] + ",\n\n"
            msg += "It's time to go to the kitchen!\n"
            msg += "\nKind regards\n"
            msg += "The coffee bot.\n"
    
            Utils.sendmail(receiver[1], receiver[0], 'Kitchen Timer!', msg, expires_minutes=60)

    def render(self):
        super(Timer, self).render()
        self.screen.fill(color=self.colors.background)

        if self.state.started is True:
            background_color = self.colors.background
            if self.state.countdownTicks <= self.settings.ticksPerSecond * self.settings.hotCountdownSeconds: 
                if math.ceil(self.state.countdownTicks / (self.settings.ticksPerSecond / 2)) % 2 == 0:
                    background_color = self.colors.highlight
            self.screen.fill(color=background_color)

        ten = self.state.countdown / 600
        one = (self.state.countdown - ten * 600) / 60
        tenth = (self.state.countdown - ten * 600 - one * 60) / 10
        hundredth = self.state.countdown - ten * 600 - one * 60 - tenth * 10

        self.screen.text(ten, xy=(60, 75), align='center', color=self.colors.font, font_size=90, font=Utils.get_font_resource('akkuratstd-bold.ttf'))
        self.screen.text(one, xy=(120, 75), align='center', color=self.colors.font, font_size=90, font=Utils.get_font_resource('akkuratstd-bold.ttf'))

        self.screen.text(':', xy=(160, 70), align='center', color=self.colors.font, font_size=48, font=Utils.get_font_resource('akkuratstd-bold.ttf'))

        self.screen.text(tenth, xy=(200, 75), align='center', color=self.colors.font, font_size=90, font=Utils.get_font_resource('akkuratstd-bold.ttf'))
        self.screen.text(hundredth, xy=(260, 75), align='center', color=self.colors.font, font_size=90, font=Utils.get_font_resource('akkuratstd-bold.ttf'))

        if self.state.started is False:
            self.disable_all_widgets()
            
            self.get_widget('tenUp').enabled = True
            self.get_widget('tenUp').render()
            
            self.get_widget('tenDown').enabled = True
            self.get_widget('tenDown').render()
            
            self.get_widget('oneUp').enabled = True
            self.get_widget('oneUp').render()
            
            self.get_widget('oneDown').enabled = True
            self.get_widget('oneDown').render()
            
            self.get_widget('tenthUp').enabled = True
            self.get_widget('tenthUp').render()
            
            self.get_widget('tenthDown').enabled = True
            self.get_widget('tenthDown').render()
            
            self.get_widget('hundredthUp').enabled = True
            self.get_widget('hundredthUp').render()
            
            self.get_widget('hundredthDown').enabled = True
            self.get_widget('hundredthDown').render()
            
            self.get_widget('start').enabled = True
            self.get_widget('start').move_to((195, 160), 'topleft')
            self.get_widget('start').render()
            
            self.get_widget('notification').enabled = True
            self.get_widget('notification').render()
            self.screen.text(self.get_widget('notification').notice, xy=(45, 180), align='topleft', max_width=130, max_height=30, color=self.colors.font, font_size=12, font=Utils.get_font_resource('akkuratstd-light.ttf'))

        else:
            self.disable_all_widgets()
            
            if not(self.state.countdownTicks <= self.settings.hotCountdownSeconds * self.settings.ticksPerSecond):
                self.get_widget('stop').enabled = True
                if len(self.notifications) > 0:
                    self.get_widget('stop').move_to((160, 140), 'center')
                    self.screen.text("Notify by email:\n " + self.get_widget('notification').notice, xy=(160, 165), align='top', max_width=300, max_height=50, color=self.colors.font, font_size=16, font=Utils.get_font_resource('akkuratstd-light.ttf'))
                    self.get_widget('stop').render()
                else:
                    self.get_widget('stop').move_to((160, 160), 'center')
                    self.get_widget('stop').render()
