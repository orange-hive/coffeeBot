import math
import pygame
from dotmap import DotMap
from ..utils import Utils
from ..base import AppBase
import tingbot


class Dishes(AppBase):

    def __init__(self, parent, countdown_seconds, ticks_per_second, timezone):
        super(Dishes, self).__init__(parent)
        
        self.init_settings(
            countdownSeconds=countdown_seconds,
            ticks=ticks_per_second,
            timezone=timezone,
            hotCountdownSeconds=5,
            waitSecondsAfterCountdownStop=5,
            waitSecondsForDismantleSound=12
        )

        self.init_states(
            countdownTicks=0,
            isCountdownStarted=False,
            countdownEndSoundPlayed=False,
            keepActive=False,
            countdownActive=False,
            timeformatted='00:00'
        )
        
        self.channels = DotMap(
            system=pygame.mixer.Channel(0),
            talk=pygame.mixer.Channel(2)
        )
        self.channels.system.set_volume(0.3)
        self.channels.talk.set_volume(0.3)
        
        self.sounds = DotMap(
            dismantle=pygame.mixer.Sound(Utils.get_audio_resource("thanks.wav")),
            countdownEnd=pygame.mixer.Sound(Utils.get_audio_resource("chinese_gong.wav"))
        )
        
        self.colors.button.active.background = (94, 141, 105)

        self.create_widgets()

    @staticmethod
    def sendmail():
        msg = "It's time to start the dish washer!\n"
        msg += "Please bring your used dishes to the kitchen.\n"
        msg += "\nKind regards\n"
        msg += "The coffee bot.\n"

        receiver = tingbot.app.settings['dishes']['email']
        Utils.sendmail(receiver[1], receiver[0], 'Call for Dishes!', msg)

    def play_countdown_end_sound(self):
        self.channels.system.play(self.sounds.countdownEnd)

    def create_widgets(self):
            def action(name):
                self.parent.say('OK. I will call out for dishes!')
                self.state.countdownTicks = self.settings.countdownSeconds * self.settings.ticks
                self.sendmail()
                self.state.countdownActive = True
                self.state.needs_render = True

            self.create_widget(
                'button',
                'c4d',
                action,
                xy=(160, 75),
                size=(300, 70),
                color=self.colors.button.active.font,
                background=self.colors.button.active.background,
                align='center',
                text='Call for Dishes',
                font=Utils.get_font_resource('akkuratstd-light.ttf'),
                font_size=28
            )

    def compute(self):
        if self.state.countdownActive is True:
            self.state.keepActive = True
            self.state.countdownTicks -= 1
    
            oldTimeFormatted = self.state.timeformatted
    
            if self.state.countdownTicks <= 0:
                if self.state.countdownEndSoundPlayed is False:
                    self.state.countdownEndSoundPlayed = True
                    self.play_countdown_end_sound()
                    
                self.state.timeformatted = '00:00'
                
                if self.state.countdownTicks <= self.settings.ticks * self.settings.hotCountdownSeconds and self.state.countdownTicks % (self.settings.ticks / 2) == 0:
                    self.state.needs_render = True
                
                if self.state.countdownTicks <= (self.settings.ticks * self.settings.waitSecondsForDismantleSound * -1):
                    self.state.countdownTicks = 0
                    self.state.countdownEndSoundPlayed = False
                    self.state.keepActive = False
                    self.state.countdownActive = False
                    self.state.needs_render = True

            else:
                mins, secs = divmod(int(math.ceil(1.0 * self.state.countdownTicks / self.settings.ticks)), 60)
                self.state.timeformatted = '{:02d}:{:02d}'.format(mins, secs)
                
            if oldTimeFormatted != self.state.timeformatted:
                self.state.needs_render = True
        
    def background(self):
        super(Dishes, self).background()
        self.compute()
            
    def foreground(self):
        super(Dishes, self).foreground()
        self.compute()
        
    def render(self):
        super(Dishes, self).render()
        self.screen.fill(color=self.colors.background)

        if self.state.countdownActive is True:
            backgroundColor = self.colors.background
            if self.state.countdownTicks <= 0 and self.state.countdownTicks <= self.settings.ticks * self.settings.hotCountdownSeconds: 
                if math.ceil(self.state.countdownTicks / (self.settings.ticks / 2)) % 2 == 0:
                    backgroundColor = self.colors.highlight

            self.screen.fill(color=backgroundColor)

            self.screen.text("Call For Dishes was activated.\nPlease give all a change\nto bringe the dishes in.", font_size=14, xy=(160, 155), color=self.colors.font, font=Utils.get_font_resource('akkuratstd-light.ttf'))
            self.screen.text(self.state.timeformatted, color=self.colors.font, font_size=60, xy=(160, 85), font=Utils.get_font_resource('akkuratstd-bold.ttf'))
        else:
            self.get_widget('c4d').render()
            self.screen.text("Do you want to start the dish washer?\nClick that button if you want\nto call out for dishes.", font_size=14, xy=(160, 155), color=self.colors.font, font=Utils.get_font_resource('akkuratstd-light.ttf'))
