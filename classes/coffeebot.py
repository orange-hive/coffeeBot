from apps import AppSwitcher, Dishes, LastCallForCoffee, MusicPlayer, Order, Timer
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
import random
import datetime
import json


class CoffeeBot(object):
    
    def __init__(self, screen, countdown_seconds, ticks_per_second, timezone, music_folder):
        self.screen = screen

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
            order=Order(self)
        )

        self.settings = DotMap(
            defaultApp='appswitcher',
            timezone=timezone
        )

        self.state = DotMap(
            activeApp=self.settings.defaultApp,
            previousApp=None,
            needs_render=True
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

        self.channels = DotMap(
            talk=pygame.mixer.Channel(2)
        )
        self.channels.talk.set_volume(0.3)
        
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

                    tts = gTTS(text=phrase, lang='en-US')
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
            self.apps[self.state.activeApp].state.needs_render = True
            self.save_persistent_state()
        else:
            self.say('Sorry. You cannot leave this application at the moment.')
        
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
        if 'key' in payload.keys():
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
        
        self.screen.surface.set_clip(pygame.Rect(0, 0, 320, 25))
        self.screen.fill(self.colors.background)
        self.screen.surface.set_clip(None)
        
        if self.apps.music.is_playing() is True:
            self.screen.text(u'\ue047', font_size=20, xy=(4, 2), align='topleft', color=self.colors.font, font=Utils.get_font_resource('icons.ttf'))
        else:
            self.screen.text(u'\ue037', font_size=20, xy=(4, 2), align='topleft', color=self.colors.font, font=Utils.get_font_resource('icons.ttf'))
            
        self.screen.text(u'\ue044', font_size=20, xy=(30, 2), align='topleft', color=self.colors.font, font=Utils.get_font_resource('icons.ttf'))
#        self.screen.text('', font_size=20, xy=(290, 2), align='topright', color=self.colors.font, font=Utils.getFontResource('icons.ttf'))
        self.screen.text(u'\ue5c3', font_size=20, xy=(313, 2), align='topright', color=self.colors.font, font=Utils.get_font_resource('icons.ttf'))
        
        if self.state.activeApp == 'appswitcher':
            self.screen.text('What shall I do for you?', font_size=16, xy=(160, 3), align='top', color=self.colors.font, font=Utils.get_font_resource('akkuratstd-light.ttf'))
        else:
            self.screen.text(self.appsInfos[self.state.activeApp].fullname, font_size=16, xy=(160, 3), align='top', color=self.colors.font, font=Utils.get_font_resource('akkuratstd-light.ttf'))

        self.state.needs_render = False

    def i_am_alive(self):
        if not(self.channels.talk.get_busy()):
            now = datetime.datetime.now(self.settings.timezone).strftime('%H:%M:%S')
            random_time = str(random.randint(1, 23)) + ':' + str(random.randint(0, 59)) + ':' + str(random.randint(0, 59))
            if now == random_time:
                phrases = [
                    'I am alive!',
                    'Is somebody out there?',
                    'Hoo Hoo?',
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
            if self.state.needs_render is True:
                self.render()
                
            self.apps[self.state.activeApp].update('fg')
            self.screen.update()

            if tingbot.app.settings['coffeeBot']['debug']:
                version_text = self.persistentState.version + ' - debug'
            else:
                version_text = self.persistentState.version

            self.screen.text(version_text, font_size=10, xy=(317, 238), align='bottomright', color=(129, 133, 135), font=Utils.get_font_resource('akkuratstd-light.ttf'))

            for name, app in self.apps.iteritems():
                if name != self.state.activeApp:
                    app.update('bg')
        else:
            for name, app in self.apps.iteritems():
                    app.update('bg')

        self.i_am_alive()
