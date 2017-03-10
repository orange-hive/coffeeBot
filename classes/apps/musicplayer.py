import pygame
import random
import os
import threading
from ..utils import Utils
from ..base import AppBase
from ..dialogs import MusicGenreDialog
import datetime
from mutagen.easyid3 import EasyID3
from mutagen import File as ID3File
from cStringIO import StringIO


class MusicPlayer(AppBase):
    
    def __init__(self, parent, music_folder, timezone):
        super(MusicPlayer, self).__init__(parent)
        
        self.init_settings(
            genres={},
            timezone=timezone
        )
        
        self.init_states(
            playingMusic=False,
            playingFile=None,
            loadingFile=False,
            loadingStartedAt=None,
            lastPos=0,
            active_genres=[],
            files=[]
        )

        pygame.mixer.music.set_volume(0.3)

        self.read_music_folder(music_folder)
        print self.settings.genres, self.state.active_genres
            
        self.colors.button.active.background = (255, 222, 45)
        self.colors.button.active.font = (0, 0, 0)

        self.create_widgets()

    def read_music_folder(self, folder):
        for filename in os.listdir(folder):
            if filename != '.DS_Store':
                if os.path.isdir(os.path.join(folder, filename)):
                    self.read_music_folder(os.path.join(folder, filename))
                else:
                    id3 = EasyID3(os.path.join(folder, filename))
                    genres = []
                    if 'genre' in id3.keys():
                        for genre_raw in id3['genre']:
                            for genre in genre_raw.split(';'):
                                genres.append(genre.strip())

                    if len(genres) == 0:
                        genres.append('unknown')

                    for genre in genres:
                        if genre not in self.settings.genres:
                            self.settings.genres[genre] = []
                            self.state.active_genres.append(genre)
                        self.settings.genres[genre].append(os.path.join(folder, filename))
                        self.state.files.append(os.path.join(folder, filename))

    def is_playing(self):
        return self.state.playingMusic

    def play(self, filename=None, volume=None, mute_talk=False):
        if filename is None:
            filename = random.choice(self.state.files)

        if volume is not None:
            pygame.mixer.music.set_volume(volume)
        else:
            pygame.mixer.music.set_volume(0.1)

        def play():
            print 'music file: ' + filename
            pygame.mixer.music.load(filename)
            self.state.loadingFile = False
            self.state.loadingStartedAt = None
            try:
                pygame.mixer.music.play()
            except:
                self.skip(mute_talk=True)

            self.state.playingFile = filename
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
            xy=(10, 55),
            size=(145, 70),
            color=self.colors.button.active.font,
            background=self.colors.button.active.background,
            align='left',
            font_size=28,
            font=Utils.get_font_resource('akkuratstd-light.ttf')
        )

        self.create_widget(
            'button',
            'select_genre',
            self.open_genre_dialog,
            xy=(165, 55),
            size=(145, 70),
            color=self.colors.button.active.font,
            background=self.colors.button.active.background,
            align='left',
            text='Select',
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

    def open_genre_dialog(self):
        def callback(action, genres=None):
            if genres is None:
                genres = []

            if action == 'ok':
                if len(genres) == 0:
                    self.state.active_genres = self.settings.genres.keys()
                else:
                    self.state.active_genres = genres

                self.parent.say('Setting new music collection!')
                self.state.files = []
                for genre in self.state.active_genres:
                    self.state.files.extend(self.settings.genres[genre])

                self.skip(mute_talk=True)

            self.state.needs_render = True

        self.parent.say('OK. Please select what I should play!')

        dialog = MusicGenreDialog(self, genres=self.settings.genres.keys(), active_genres=self.state.active_genres, callback=callback)
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
            self.get_widget('toggle').text = 'Play!'
            self.get_widget('toggle').render()
            self.get_widget('select_genre').render()
        else:
            self.get_widget('toggle').text = 'Shush!'
            self.get_widget('toggle').render()
            self.get_widget('select_genre').render()

            try:
                id3 = EasyID3(self.state.playingFile)
                genres = '; '.join(id3['genre'])
                artist = ' '.join(id3['artist'])
                album = ' '.join(id3['album'])
                title = ' '.join(id3['title'])
                file_info = title + "\n" + artist + "\n" + album + "\n" + genres

                id3Raw = ID3File(self.state.playingFile)
                if 'APIC:' in id3Raw.keys():
                    artwork = StringIO(id3Raw.tags['APIC:'].data)
                    self.screen.image(pygame.image.load(artwork), xy=(310, 180), align='bottomright', max_height=75, max_width=75)
            except (RuntimeError, TypeError):
                file_info = os.path.basename(self.state.playingFile)

            self.screen.text(file_info, xy=(10, 140), max_width=300, align='left', color=self.colors.font, font_size=14, font=Utils.get_font_resource('akkuratstd-light.ttf'))
