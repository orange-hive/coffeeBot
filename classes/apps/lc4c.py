import datetime
import math
import pygame
from dotmap import DotMap
from ..utils import Utils
from ..base import AppBase
import tingbot



class LastCallForCoffee(AppBase):

    def __init__(self, parent, countdown_seconds, ticks_per_second, timezone):
        super(LastCallForCoffee, self).__init__(parent)
        
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
            dismantleSoundPlayed=False,
            countdownEndSoundPlayed=False,
            keepActive=False,
            countdownActive=False,
            timeformatted='00:00'
        )
        
        self.init_persistent_states(
            lastActivated=None
        )

        self.channels = DotMap(
            system=pygame.mixer.Channel(0)
        )
        self.channels.system.set_volume(0.3)

        self.sounds = DotMap(
            countdownEnd=pygame.mixer.Sound(Utils.get_audio_resource("chinese_gong.wav"))
        )
        
        self.colors.button.active.background = (172, 122, 99)

        self.create_widgets()

    def is_armed(self):
        return (
            (
                self.persistentState.lastActivated is None
                or not(datetime.datetime.strptime(self.persistentState.lastActivated, '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d') == datetime.datetime.now(self.settings.timezone).strftime('%Y-%m-%d'))
            ) and (
                Utils.time_in_range(
                    datetime.time(16, 45, 0),
                    datetime.time(23, 59, 59),
                    datetime.datetime.now(self.settings.timezone).time()
                )
            )
        )

    def sendmail(self):
        dismantle_time = (datetime.datetime.now(self.settings.timezone) + datetime.timedelta(minutes=5)).strftime('%H:%M')

        msg = "It's time to shutdown the coffee machine!\n"
        msg += "\nYour last chance to get a steaming hot cup of a delious coffeine containing energizer ends at " + dismantle_time + ".\n"
        msg += "\nAnd while you're on the way, please bring your used dishes with you.\n"
        msg += "\nKind regards\n"
        msg += "The coffee bot.\n"

        receiver = tingbot.app.settings['lc4c']['email']
        Utils.sendmail(receiver[1], receiver[0], 'Last Call for Coffee!', msg, expires_minutes=15)

    def play_dismantle_sound(self):
        self.parent.say('The fantastic coffeemachine can now be disassembled! Thank you for waiting!')

    def play_countdown_end_sound(self):
        self.channels.system.play(self.sounds.countdownEnd)

    def create_widgets(self):
            def action():
                if self.is_armed() is True:
                    self.parent.say('OK. I will make a last call for coffee!')
                    self.get_widget('lc4c').enabled = False
                    self.state.countdownTicks = self.settings.countdownSeconds * self.settings.ticks
                    self.sendmail()
                    self.persistentState.lastActivated = datetime.datetime.now(self.settings.timezone).strftime('%Y-%m-%dT%H:%M:%S')
                    self.parent.save_persistent_state()
                    self.state.countdownActive = True
                    self.state.needs_render = True

            self.create_widget(
                'button',
                'lc4c',
                action,
                xy=(160, 75),
                size=(300, 70),
                color=self.colors.button.active.font,
                background=self.colors.button.active.background,
                align='center',
                text='Last Call for Coffee',
                font=Utils.get_font_resource('akkuratstd-light.ttf'),
                font_size=28,
                enabled=False
            )

            self.create_widget(
                'button',
                'inactive_lc4c',
                None,
                xy=(160, 75),
                size=(300, 70),
                color=self.colors.button.inactive.font,
                background=self.colors.button.inactive.background,
                align='center',
                text='Last Call for Coffee',
                font=Utils.get_font_resource('akkuratstd-light.ttf'),
                font_size=28,
                enabled=False
            )

    def compute(self):
        if self.state.countdownActive is True:
            self.state.keepActive = True
            self.state.countdownTicks -= 1
    
            old_time_formatted = self.state.timeformatted
    
            if self.state.countdownTicks <= 0:
                if self.state.countdownEndSoundPlayed is False:
                    self.state.countdownEndSoundPlayed = True
                    self.play_countdown_end_sound()
                    
                if self.state.dismantleSoundPlayed is False and self.state.countdownTicks <= (self.settings.ticks * self.settings.waitSecondsAfterCountdownStop * -1):
                    self.state.dismantleSoundPlayed = True
                    self.play_dismantle_sound()
                
                self.state.timeformatted = '00:00'
                
                if self.state.countdownTicks <= self.settings.ticks * self.settings.hotCountdownSeconds and self.state.countdownTicks % (self.settings.ticks / 2) == 0:
                    self.state.needs_render = True
                
                if self.state.countdownTicks <= (self.settings.ticks * self.settings.waitSecondsForDismantleSound * -1):
                    self.state.countdownTicks = 0
                    self.state.dismantleSoundPlayed = False
                    self.state.countdownEndSoundPlayed = False
                    self.state.keepActive = False
                    self.state.countdownActive = False
                    self.state.needs_render = True

            else:
                mins, secs = divmod(int(math.ceil(1.0 * self.state.countdownTicks / self.settings.ticks)), 60)
                self.state.timeformatted = '{:02d}:{:02d}'.format(mins, secs)
                
            if old_time_formatted != self.state.timeformatted:
                self.state.needs_render = True
        
    def background(self):
        super(LastCallForCoffee, self).background()
        self.compute()
            
    def foreground(self):
        super(LastCallForCoffee, self).foreground()
        self.compute()
        
    def render(self):
        super(LastCallForCoffee, self).render()
        self.screen.fill(color=self.colors.background)

        if self.state.countdownActive is True:
            background_color = self.colors.background
            if self.state.countdownTicks <= 0 and self.state.countdownTicks <= self.settings.ticks * self.settings.hotCountdownSeconds: 
                if math.ceil(self.state.countdownTicks / (self.settings.ticks / 2)) % 2 == 0:
                    background_color = self.colors.highlight

            self.screen.fill(color=background_color)

            self.screen.text("Last Call For Coffee was activated.\nPlease give these coffee junkies\nsome time to come and get their medicine.", font_size=14, xy=(160, 155), color=self.colors.font, font=Utils.get_font_resource('akkuratstd-light.ttf'))
            self.screen.text(self.state.timeformatted, color=self.colors.font, font_size=60, xy=(160, 85), font=Utils.get_font_resource('akkuratstd-bold.ttf'))
        else:
            if self.is_armed() is True:
                self.get_widget('lc4c').enabled = True
                self.get_widget('lc4c').render()
                self.screen.text("Is it that late again?\nClick that button if you are about\nto disassemble the coffee machine.", font_size=14, xy=(160, 155), color=self.colors.font, font=Utils.get_font_resource('akkuratstd-light.ttf'))
            else:            
                self.get_widget('lc4c').enabled = False
                self.get_widget('inactive_lc4c').render()
                if (
                    self.persistentState.lastActivated is None
                    or not(datetime.datetime.strptime(self.persistentState.lastActivated, '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d') == datetime.datetime.now(self.settings.timezone).strftime('%Y-%m-%d'))
                ):
                    self.screen.text("You're out of the \"lc4c time\".\nThe system activates at 16:45.\nMay I play some gentle music instead?", font_size=14, xy=(160, 155), color=self.colors.button.active.font, font=Utils.get_font_resource('akkuratstd-light.ttf'))
                else:
                    self.screen.text("The system has already been\nactivated at " + datetime.datetime.strptime(self.persistentState.lastActivated, '%Y-%m-%dT%H:%M:%S').strftime('%H:%M') + ".\nMay I play some gentle music instead?", font_size=14, xy=(160, 155), color=self.colors.button.active.font, font=Utils.get_font_resource('akkuratstd-light.ttf'))
