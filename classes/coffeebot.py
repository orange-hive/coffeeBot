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
            defaultApp='appswitcher'
        )

        self.state = DotMap(
            activeApp=self.settings.defaultApp,
            previousApp=None,
            needsRender=True
        )
        
        self.persistentState = DotMap(
            version='1.5.0'
        )
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
        audioFile = Utils.get_audio_text_resource(sha1(phrase).hexdigest() + '.wav')

        def action():
            if not(os.path.isfile(audioFile)):
                if platform.system() == 'Darwin':
                    mpg123Path = '/opt/local/bin/mpg123'
                else:
                    mpg123Path = 'mpg123'

                tts = gTTS(text=phrase, lang='en-US')
                with NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                    tempfile = f.name
                tts.save(tempfile)
                subprocess.call([mpg123Path, '-w', audioFile, tempfile])
                os.remove(f.name)
                
            self.channels.talk.play(pygame.mixer.Sound(audioFile))

        sayThread = threading.Thread(target=action)
        sayThread.start()

    def save_persistent_state(self):
        globalState = DotMap()
        
        for name, app in self.apps.iteritems():
            globalState[name] = app.get_persistent_state()
        
        globalState.coffeeBot = self.persistentState
        Utils.write_state(globalState.toDict())

    def read_persistent_state(self):
        globalState = Utils.read_state()

        if (
            globalState is None
            or 'coffeeBot' not in globalState.keys()
            or 'version' not in globalState['coffeeBot'].keys()
            or globalState['coffeeBot']['version'] != self.persistentState.version
            or self.persistentState.version.find('dev') != -1
        ):
            print 'reset states'
            self.save_persistent_state()
        else:            
            for name, app in self.apps.iteritems():
                if name in globalState.keys():
                    app.set_persistent_state(DotMap(globalState[name]))
            if 'coffeeBot' in globalState.keys():
                self.persistentState = DotMap(globalState['coffeeBot'])
        
    def set_active_app(self, app_name):
        if self.apps[self.state.activeApp].keep_active() is False:
            self.state.previousApp = self.state.activeApp
            self.state.activeApp = app_name
            self.apps[self.state.activeApp].state.needsRender = True
            self.save_persistent_state()
        else:
            self.say('Sorry. You cannot leave this application at the moment.')
        
    def get_active_app(self):
        return self.state.activeApp

    def button_press(self, position):
        self.state.needsRender = True
        
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
            self.state.needsRender = True
        self.apps[self.state.activeApp].on_touch(xy, action)

    def keep_active(self):
        return self.apps[self.state.activeApp].keep_active()

    def render(self):
        print 'render ' + str(time()) + ' - ' + self.__class__.__name__
        
        self.screen.surface.set_clip(pygame.Rect(0, 0, 320, 25))
        self.screen.fill(self.colors.background)
        self.screen.surface.set_clip(None)
        
        if self.apps.music.is_playing() is True:
            self.screen.text(u'\ue047', font_size=20, xy=(5, 2), align='topleft', color=self.colors.font, font=Utils.get_font_resource('icons.ttf'))
        else:
            self.screen.text(u'\ue037', font_size=20, xy=(5, 2), align='topleft', color=self.colors.font, font=Utils.get_font_resource('icons.ttf'))
            
        self.screen.text(u'\ue044', font_size=20, xy=(30, 2), align='topleft', color=self.colors.font, font=Utils.get_font_resource('icons.ttf'))
#        self.screen.text('', font_size=20, xy=(290, 2), align='topright', color=self.colors.font, font=Utils.getFontResource('icons.ttf'))
        self.screen.text(u'\ue5c3', font_size=20, xy=(315, 2), align='topright', color=self.colors.font, font=Utils.get_font_resource('icons.ttf'))
        
        if self.state.activeApp == 'appswitcher':
            self.screen.text('What shall I do for you?', font_size=16, xy=(160, 3), align='top', color=self.colors.font, font=Utils.get_font_resource('akkuratstd-light.ttf'))
        else:
            self.screen.text(self.appsInfos[self.state.activeApp].fullname, font_size=16, xy=(160, 3), align='top', color=self.colors.font, font=Utils.get_font_resource('akkuratstd-light.ttf'))

        self.state.needsRender = False
        
    def update(self, execution_type='fg'):
        if execution_type == 'fg':
            if self.state.needsRender is True:
                self.render()
                
            self.apps[self.state.activeApp].update('fg')
            self.screen.update()

            if tingbot.app.settings['coffeeBot']['debug']:
                versionText = self.persistentState.version + ' - debug'
            else:
                versionText = self.persistentState.version

            self.screen.text(versionText, font_size=10, xy=(317, 238), align='bottomright', color=(129, 133, 135), font=Utils.get_font_resource('akkuratstd-light.ttf'))

            for name, app in self.apps.iteritems():
                if name != self.state.activeApp:
                    app.update('bg')
        else:
            for name, app in self.apps.iteritems():
                    app.update('bg')
