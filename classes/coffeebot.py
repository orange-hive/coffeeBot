from apps import AppSwitcher, Dishes, LastCallForCoffee, MusicPlayer, Order, Timer, Kitchenteam
from dotmap import DotMap
import threading
from tempfile import NamedTemporaryFile
from time import time
import pygame
import os
import subprocess
import platform
from gtts import gTTS
from hashlib import sha1
from utils import Utils
import tingbot
from tingbot.graphics import Surface
import random
import datetime
import json


class CoffeeBot(object):
    
    def __init__(self, screen, countdown_seconds, ticks_per_second, timezone, music_folder):
        self.screen = Surface(pygame.Surface((320, 215)))
        self.screen.surface.convert()
        self.screen.surface.set_alpha(255)

        self.main_screen = Surface(pygame.Surface(screen.surface.get_size()))
        self.main_screen.surface.convert()
        self.main_screen.surface.set_alpha(255)

        self.display = screen

        self.appsInfos = DotMap({
            'lc4c': {
                'name': 'LC4C',
                'fullname': 'Last Call For Coffee',
                'icon': u'\ue541',
                'font': (244, 245, 245),
                'background': (172, 122, 99)
            },
            'dishes': {
                'name': 'Dishes',
                'fullname': 'Call For Dishes',
                'icon': u'\ue903',
                'font': (244, 245, 245),
                'background': (94, 141, 105)
            },
            'timer': {
                'name': 'Timer',
                'fullname': 'Kitchen Timer',
                'icon': u'\ue01b',
                'font': (244, 245, 245),
                'background': (236, 65, 93)
            },
            'order': {
                'name': 'Order',
                'fullname': 'What is missing?',
                'icon': u'\ue8cc',
                'font': (244, 245, 245),
                'background': (65, 190, 198)
            },
            'music': {
                'name': 'Music',
                'fullname': 'Music Player',
                'icon': u'\ue3a1',
                'font': (65, 71, 76),
                'background': (255, 222, 45)
            },
        })
        
        self.apps = DotMap(
            appswitcher=AppSwitcher(
                self,
                self.appsInfos
            ),
            lc4c=LastCallForCoffee(self, countdown_seconds, ticks_per_second, timezone),
            dishes=Dishes(self, countdown_seconds, ticks_per_second, timezone),
            music=MusicPlayer(self, music_folder, timezone),
            timer=Timer(self, ticks_per_second),
            order=Order(self),
            kitchenteam=Kitchenteam(self, timezone),
        )

        self.settings = DotMap(
            defaultApp='appswitcher',
            timezone=timezone,
            ticks_per_second=ticks_per_second
        )

        self.state = DotMap(
            activeApp=self.settings.defaultApp,
            previousApp=None,
            needs_render=True,
            tween_start_time=None,
            tween_typ=None,
            tween_value=None,
            tween_to=None,
            tween_step=None
        )
        
        self.persistentState = DotMap(
            version='unknown'
        )
        try:
            appinfo_file = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'app.tbinfo'))
            if os.path.exists(appinfo_file):
                f = open(appinfo_file, 'r')
                appinfo = json.load(f)
                f.close()
                self.persistentState.version = appinfo['version']
        except ValueError:
            pass

        self.read_persistent_state()
        
        if self.apps.music.is_playing() is True:
            self.apps.music.play()

        self.colors = DotMap(
            background=(44, 51, 56),
            font=(255, 255, 255),
        )

        self.main_screen.fill((0, 0, 0, 0))

        self.channels = DotMap(
            talk=pygame.mixer.Channel(2)
        )
        self.channels.talk.set_volume(0.1)
        
        self.say('Hi, I am the coffee bot! What shall I do for you?')

    def say(self, phrase):
        if phrase:
            audio_file = Utils.get_audio_text_resource(sha1(phrase).hexdigest() + '.wav')

            def action():
                if not(os.path.isfile(audio_file)):
                    if platform.system() == 'Darwin':
                        mpg123_path = '/opt/local/bin/mpg123'
                    else:
                        mpg123_path = 'mpg123'

                    tts = gTTS(text=phrase, lang='en-us')
                    with NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                        tempfile = f.name
                    tts.save(tempfile)
                    subprocess.call([mpg123_path, '-w', audio_file, tempfile])
                    os.remove(f.name)

                self.channels.talk.play(pygame.mixer.Sound(audio_file))

            say_thread = threading.Thread(target=action)
            say_thread.start()

    def save_persistent_state(self):
        global_state = DotMap()
        
        for name, app in self.apps.iteritems():
            global_state[name] = app.get_persistent_state()
        
        global_state.coffeeBot = self.persistentState
        Utils.write_state(global_state.toDict())

    def read_persistent_state(self):
        global_state = Utils.read_state()

        if (
            global_state is None
            or 'coffeeBot' not in global_state.keys()
            or 'version' not in global_state['coffeeBot'].keys()
            or global_state['coffeeBot']['version'] != self.persistentState.version
            or self.persistentState.version.find('dev') != -1
        ):
            print 'reset states'
            self.save_persistent_state()
        else:            
            for name, app in self.apps.iteritems():
                if name in global_state.keys():
                    app.set_persistent_state(DotMap(global_state[name]))
            if 'coffeeBot' in global_state.keys():
                self.persistentState = DotMap(global_state['coffeeBot'])
        
    def set_active_app(self, app_name):
        if self.apps[self.state.activeApp].keep_active() is False:
            self.state.previousApp = self.state.activeApp
            self.state.activeApp = app_name
            if self.state.previousApp is not None and self.state.activeApp != self.state.previousApp:
                if app_name == self.settings.defaultApp:
                    self.on_hide()
                else:
                    self.on_show()
            self.apps[self.state.activeApp].state.needs_render = True
            if self.apps[self.state.activeApp].has_dialog():
                self.apps[self.state.activeApp].dialog.state.needs_render = True
            self.save_persistent_state()
        else:
            self.say('Sorry. You cannot leave this application at the moment.')

    def on_show(self):
        self.tween_start('show', 100, 0, 100, -1)

    def on_hide(self):
        self.tween_start('hide', 0, 100, 100, 1)
        pass

    def tween_start(self, typ, start, end, duration, step):
        self.state.tween_typ = typ
        self.state.tween_value = start
        self.state.tween_to = end
        self.state.tween_duration = float(duration * self.settings.ticks_per_second)
        self.state.tween_step = step
        self.state.tween_ticks = 0

    def tween(self):
        completed = True

        if self.state.tween_value != self.state.tween_to:
            completed = False

            t = self.state.tween_ticks * 1000
            c = self.state.tween_step
            b = self.state.tween_value
            d = self.state.tween_duration

            if self.state.tween_typ == 'show':
                t /= d
                self.state.tween_value = c * t * t + b

            elif self.state.tween_typ == 'hide':
                t /= d
                self.state.tween_value = c * t * t + b

            if (
                self.state.tween_step > 0
                and
                self.state.tween_value >= self.state.tween_to
            ) or (
                self.state.tween_step < 0
                and
                self.state.tween_value <= self.state.tween_to
            ):
                self.state.tween_value = self.state.tween_to

            self.state.tween_ticks += 1

        return completed

    def get_active_app(self):
        return self.state.activeApp

    def button_press(self, position):
        self.state.needs_render = True
        
        if position == 'left':
            self.apps.music.toggle() 
        elif position == 'midleft':
            self.apps.music.skip()
        elif position == 'midright':
            pass
        elif position == 'right':
            if self.state.activeApp == 'appswitcher' and self.state.previousApp is not None:
                self.set_active_app(self.state.previousApp)
            else:
                self.set_active_app('appswitcher')

    def on_touch(self, xy, action):
        if action == 'down':
            self.state.needs_render = True
        self.apps[self.state.activeApp].on_touch(xy, action)

    def on_webhook(self, payload):
        if tingbot.app.settings['coffeeBot']['webhook_active'] is True and 'key' in payload.keys():
            if payload['key'] == tingbot.app.settings['coffeeBot']['webhook_key']:
                if 'action' in payload.keys():
                    if payload['action'] == 'say':
                        if 'text' in payload.keys():
                            self.say(payload['text'])
                    elif payload['action'] == 'screenshot':
                        screenshot_file = Utils.get_screenshot_resource()
                        pygame.image.save(self.screen.surface, screenshot_file)
                        Utils.sendmail(
                            tingbot.app.settings['coffeeBot']['screenshot_receiver'][1],
                            tingbot.app.settings['coffeeBot']['screenshot_receiver'][0],
                            'Screenshot',
                            "Here is your Screenshot\n\n",
                            (screenshot_file,)
                        )
                    elif 'action' in payload.keys():
                        if payload['action'] == 'quit':
                            quit()

                    elif 'app' in payload.keys() and payload['app'] in self.apps.toDict().keys():
                        if payload['action'] == 'open':
                            self.set_active_app(payload['app'])
                        elif payload['app'] == 'music':
                            if payload['action'] == 'play':
                                self.apps['music'].play()

    def keep_active(self):
        return self.apps[self.state.activeApp].keep_active()

    def render(self):
        print 'render ' + str(time()) + ' - ' + self.__class__.__name__
        
        self.main_screen.fill(self.colors.background)

        if self.apps.music.is_playing() is True:
            self.main_screen.text(u'\ue047', font_size=20, xy=(4, 2), align='topleft', color=self.colors.font, font=Utils.get_font_resource('icons.ttf'))
        else:
            self.main_screen.text(u'\ue037', font_size=20, xy=(4, 2), align='topleft', color=self.colors.font, font=Utils.get_font_resource('icons.ttf'))
            
        self.main_screen.text(u'\ue044', font_size=20, xy=(30, 2), align='topleft', color=self.colors.font, font=Utils.get_font_resource('icons.ttf'))
#        self.main_screen.text('', font_size=20, xy=(290, 2), align='topright', color=self.colors.font, font=Utils.getFontResource('icons.ttf'))
        self.main_screen.text(u'\ue5c3', font_size=20, xy=(313, 2), align='topright', color=self.colors.font, font=Utils.get_font_resource('icons.ttf'))
        
        if self.state.activeApp == 'appswitcher':
            self.main_screen.text('What shall I do for you?', font_size=16, xy=(160, 3), align='top', color=self.colors.font, font=Utils.get_font_resource('akkuratstd-light.ttf'))
        else:
            self.main_screen.text(self.appsInfos[self.state.activeApp].fullname, font_size=16, xy=(160, 3), align='top', color=self.colors.font, font=Utils.get_font_resource('akkuratstd-light.ttf'))

        self.state.needs_render = False

    def i_am_alive(self):
        if not(self.channels.talk.get_busy()):
            now = datetime.datetime.now(self.settings.timezone).strftime('%H:%M:%S')
            random_time = str(random.randint(1, 23)) + ':' + str(random.randint(0, 59)) + ':' + str(random.randint(0, 59))
            if now == random_time:
                phrases = [
                    'I am alive!',
                    'Is somebody out there?',
                    'Hoo, Hoo?',
                    'I feel so lonely',
                    'dumb dee dumb',
                    'doo dee doo',
                    'Is this Orange Hive?',
                    'I never saw my creator!'
                ]
                self.say(random.choice(phrases))
                print "i am alive: " + now

    def update(self, execution_type='fg'):
        if execution_type == 'fg':
            updated = False

            if self.state.needs_render is True:
                self.render()
                updated = True

            updated = (updated or self.apps[self.state.activeApp].update('fg'))

            tween_completed = self.tween()
            if updated is True or tween_completed is False:
                if self.state.tween_value is not None:
                    y = self.screen.height * (self.state.tween_value / 100)
                else:
                    y = self.screen.height

                self.display.surface.blit(self.main_screen.surface, (0, 0))

                if self.state.tween_typ == 'show':
                    if self.state.previousApp is not None:
                        self.display.surface.blit(self.apps[self.state.previousApp].screen.surface, (0, 25))
                    self.display.surface.blit(self.apps[self.state.activeApp].screen.surface, (0, 25),
                                              (0, y, self.screen.width, self.screen.height))
                elif self.state.tween_typ == 'hide':
                    self.display.surface.blit(self.apps[self.state.activeApp].screen.surface, (0, 25))
                    if self.state.previousApp is not None:
                        self.display.surface.blit(self.apps[self.state.previousApp].screen.surface, (0, 25),
                                              (0, y, self.screen.width, self.screen.height))
                else:
                    self.display.surface.blit(self.apps[self.state.activeApp].screen.surface, (0, 25))

                if tingbot.app.settings['coffeeBot']['debug']:
                    version_text = self.persistentState.version + ' - debug'
                else:
                    version_text = self.persistentState.version

                self.display.text(version_text, font_size=10, xy=(317, 238), align='bottomright',
                                  color=(129, 133, 135), font=Utils.get_font_resource('akkuratstd-light.ttf'))

                self.display.update()

            for name, app in self.apps.iteritems():
                if name != self.state.activeApp:
                    app.update('bg')
        else:
            for name, app in self.apps.iteritems():
                    app.update('bg')

        self.i_am_alive()
