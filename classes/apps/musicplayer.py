import pygame
import random
import os
import threading
from ..utils import Utils
from ..base import AppBase
from ..dialogs import MusicFolderDialog
import datetime


class MusicPlayer(AppBase):
    
    def __init__(self, parent, music_folder, timezone):
        super(MusicPlayer, self).__init__(parent)
        
        self.init_settings(
            folder={},
            timezone=timezone
        )
        
        self.init_states(
            playingMusic=False,
            playingFile=None,
            playingFolder=None,
            loadingFile=False,
            loadingStartedAt=None,
            lastPos=0,
            active_folder=[]
        )

        pygame.mixer.music.set_volume(0.3)

        self.read_music_folder(music_folder)
        print self.settings.folder, self.state.active_folder
            
        self.colors.button.active.background = (255, 222, 45)
        self.colors.button.active.font = (0, 0, 0)

        self.create_widgets()

    def read_music_folder(self, folder, level=0, save_to_folder="unknown"):
        for filename in os.listdir(folder):
            if filename != '.DS_Store':
                if os.path.isdir(os.path.join(folder, filename)):
                    if level == 0:
                        save_to_folder = filename
                    self.read_music_folder(os.path.join(folder, filename), level + 1, save_to_folder=save_to_folder)
                else:
                    if save_to_folder not in self.settings.folder:
                        self.settings.folder[save_to_folder] = []
                        self.state.active_folder.append(save_to_folder)
                    self.settings.folder[save_to_folder].append(os.path.join(folder, filename))

    def is_playing(self):
        return self.state.playingMusic

    def play(self, filename=None, volume=None, mute_talk=False):
        folder = None
        if filename is None:
            folder = random.choice(self.state.active_folder)
            filename = random.choice(self.settings.folder[folder])

        if volume is not None:
            pygame.mixer.music.set_volume(volume)
        else:
            pygame.mixer.music.set_volume(0.1)

        def play():
            print 'Musicfolder: ' + folder
            print 'Musicfile: ' + filename
            pygame.mixer.music.load(filename)
            self.state.loadingFile = False
            self.state.loadingStartedAt = None
            pygame.mixer.music.play()

            self.state.playingFile = os.path.basename(filename)
            self.state.playingFolder = os.path.basename(folder)
            self.state.needs_render = True
            self.parent.needs_render = True

        self.stop(mute_talk=True)
        if mute_talk is False:
            phrases = [
                'Ok. I will play some music.',
                'Let\'s play some music',
                'doody doody doo',
                'As you wish'
            ]
            self.parent.say(random.choice(phrases))

        play_thread = threading.Thread(target=play)
        play_thread.start()
        self.state.playingMusic = True
        self.state.loadingFile = True
        self.state.loadingStartedAt = datetime.datetime.now(self.settings['timezone'])
        self.state.needs_render = True
        self.parent.needs_render = True

    def stop(self, mute_talk=False):
        if mute_talk is False:
            phrases = [
                'Ok. I will stop the music.',
                'I\'ll be quiet.',
                'Ok',
                'As you wish'
            ]
            self.parent.say(random.choice(phrases))

        if pygame.mixer.music.get_busy():
            pygame.mixer.music.fadeout(500)
            while pygame.mixer.music.get_busy():
                continue

        self.state.playingMusic = False
        self.state.playingFile = None
        self.state.playingFolder = None
        self.state.needs_render = True
        self.parent.needs_render = True

    def skip(self, mute_talk=False):
        if mute_talk is False:
            phrases = [
                'Ok. I will play another song.',
                'Skipping',
                'Ok',
                'As you wish'
            ]
            self.parent.say(random.choice(phrases))

        self.stop(mute_talk=True)
        self.play(mute_talk=True)

    def toggle(self):
        if self.is_playing() is True:
            self.stop()
        else:
            self.play()
      
    def create_widgets(self):
        def action():
            self.toggle()
        
        self.create_widget(
            'button',
            'toggle',
            action,
            xy=(10, 75),
            size=(145, 70),
            color=self.colors.button.active.font,
            background=self.colors.button.active.background,
            align='left',
            font_size=28,
            font=Utils.get_font_resource('akkuratstd-light.ttf')
        )

        self.create_widget(
            'button',
            'select_folder',
            self.open_folder_dialog,
            xy=(165, 75),
            size=(145, 70),
            color=self.colors.button.active.font,
            background=self.colors.button.active.background,
            align='left',
            text='select',
            font_size=28,
            font=Utils.get_font_resource('akkuratstd-light.ttf')
        )

    def check_music_playing(self):
        if self.state.loadingFile is False and self.is_playing() is True and pygame.mixer.music.get_pos() == -1:
            self.play(mute_talk=True)
        
    def foreground(self):
        super(MusicPlayer, self).foreground()
        self.check_music_playing()
        
    def background(self):
        super(MusicPlayer, self).background()
        self.check_music_playing()

    def open_folder_dialog(self):
        def callback(action, folder=None):
            if folder is None:
                folder = []

            if action == 'ok':
                if len(folder) == 0:
                    self.state.active_folder = self.settings.folder.keys()
                else:
                    self.state.active_folder = folder

            self.state.needs_render = True
            self.parent.say('Setting new music collection!')
            self.skip(mute_talk=True)

        self.parent.say('OK. Please select what I should play!')

        dialog = MusicFolderDialog(self, folder=self.settings.folder.keys(), active_folder=self.state.active_folder, callback=callback)
        self.open_dialog(dialog)

    def render(self):
        super(MusicPlayer, self).render()
        self.screen.fill(color=self.colors.background)

        if self.state.loadingFile is True and self.state.loadingStartedAt is not None:
            if (self.state.loadingStartedAt + datetime.timedelta(seconds=5)) < datetime.datetime.now(self.settings['timezone']):
                self.parent.say('This song is not loading. I will play another song.')
                self.skip(mute_talk=True)
            else:
                self.screen.image('loader.gif', xy=(160, 75), align='center')
                self.state.needs_render = True
        elif self.state.playingMusic is False and not(pygame.mixer.music.get_busy()):
            self.get_widget('toggle').text = 'Play some music!'
            self.get_widget('toggle').render()
            self.get_widget('select_folder').render()
        else:
            self.get_widget('toggle').text = 'Shush!'
            self.get_widget('toggle').render()
            self.get_widget('select_folder').render()
            folder = ''
            if self.state.playingFolder is not None and self.state.playingFolder != 'unknown':
                folder = ' (' + self.state.playingFolder + ')'
            self.screen.text("Playing" + folder + "\n" + self.state.playingFile, xy=(160, 150), max_width=300, align='center', color=self.colors.font, font_size=14, font=Utils.get_font_resource('akkuratstd-light.ttf'))
