from classes import *
import tingbot
from tingbot import *
import datetime
import pytz
from random import randint
import subprocess
from classes.utils import Utils
import json

settings = {
    'ticksPerSecond': 10,
    'countdownSeconds': 300,
    'sleepAfterSeconds': 300,
    'timezone': pytz.timezone('Europe/Berlin'),
    'musicFolder': tingbot.app.settings['coffeeBot']['musicFolder']
}
startup = True
activeScreen = True
oldActiveScreen = activeScreen
lastActionAt = datetime.datetime.now(settings['timezone'])
coffeeBot = CoffeeBot(screen, settings['countdownSeconds'], settings['ticksPerSecond'], settings['timezone'], settings['musicFolder'])
screensaverCoordinates = (randint(45, 275), randint(75, 195))
screensaverNeedsUpdate = True


@left_button.hold
def shutdown():
    screen.brightness = 0
    subprocess.check_call(['shutdown', '-h', 'now'])


@right_button.hold
def quit_app():
    screen.brightness = 100
    quit()


@left_button.press
def left_button():
    global lastActionAt

    lastActionAt = datetime.datetime.now(settings['timezone'])
    if activeScreen:
        coffeeBot.button_press('left')


@midleft_button.press
def midleft_button():
    global lastActionAt

    lastActionAt = datetime.datetime.now(settings['timezone'])
    if activeScreen:
        coffeeBot.button_press('midleft')


@midright_button.press
def midright_button():
    global lastActionAt

    lastActionAt = datetime.datetime.now(settings['timezone'])
    if activeScreen:
        coffeeBot.button_press('midright')


@right_button.press
def right_button():
    global lastActionAt

    lastActionAt = datetime.datetime.now(settings['timezone'])
    if activeScreen:
        coffeeBot.button_press('right')


@touch()
def on_touch(xy, action):
    global activeScreen
    global lastActionAt

    lastActionAt = datetime.datetime.now(settings['timezone'])

    if activeScreen:
        coffeeBot.on_touch(xy, action)


@webhook('coffeeBot')
def on_webhook(data):
    global startup

    if startup is True:
        startup = False
    else:
        try:
            payload = json.loads(data)
            coffeeBot.on_webhook(payload)
        except ValueError:
            pass


@every(seconds=1.0/5)
def activitycheck():
    global lastActionAt
    global activeScreen
    global oldActiveScreen

    oldActiveScreen = activeScreen
    if (
        (lastActionAt + datetime.timedelta(seconds=settings['sleepAfterSeconds'])) > datetime.datetime.now(settings['timezone'])
        or coffeeBot.keep_active() is True
    ):
        activeScreen = True
        screen.brightness = 100
    else:
        activeScreen = False
        screen.brightness = 50


@every(seconds=4.0/1)
def updatescreensavercoordinates():
    global screensaverCoordinates
    global screensaverNeedsUpdate

    screensaverCoordinates = (randint(45, 275), randint(75, 170))
    screensaverNeedsUpdate = True


@every(seconds=1.0/settings['ticksPerSecond'])
def loop():
    global activeScreen
    global oldActiveScreen
    global screensaverNeedsUpdate

    if activeScreen:
        if oldActiveScreen != activeScreen:
            coffeeBot.state.needs_render = True
            coffeeBot.apps[coffeeBot.get_active_app()].state.needs_render = True
            oldActiveScreen = activeScreen
        coffeeBot.update('fg')
    else:
        coffeeBot.update('bg')
        if screensaverNeedsUpdate:
            screen.fill('black')
            screen.image('icon.png', xy=screensaverCoordinates, max_width=90, max_height=90, scale='fit', align="center")
            screen.text(
                datetime.datetime.now(settings['timezone']).strftime('%H:%M'),
                xy=(screensaverCoordinates[0], screensaverCoordinates[1] + 55),
                color=(255, 255, 255),
                font_size=16, font=Utils.get_font_resource('akkuratstd-bold.ttf')
            )
            screensaverNeedsUpdate = False

tingbot.run()
