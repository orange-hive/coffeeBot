from ..base import AppBase
from ..utils import Utils
import datetime
import tingbot
import math
import calendar
from dateutil import parser as date_parser



class Kitchenteam(AppBase):
    
    def __init__(self, parent, timezone):
        super(Kitchenteam, self).__init__(parent)

        self.init_settings(
            timezone=timezone
        )

        self.init_persistent_states(
            lastMailSent=None,
            lastTowelMailSent=None
        )

    def is_team_armed(self):
        return (
            (
                self.persistentState.lastMailSent is None
                or not(date_parser.parse(self.persistentState.lastMailSent, '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d') == datetime.datetime.now(self.settings.timezone).strftime('%Y-%m-%d'))
            ) and (
                Utils.time_in_range(
                    datetime.time(8, 0, 0),
                    datetime.time(8, 59, 59),
                    datetime.datetime.now(self.settings.timezone).time()
                )
            )
        )

    def is_towel_cleaning_team_armed(self):
        now = datetime.datetime.now(self.settings.timezone)

        return (
            (
                self.persistentState.lastTowelMailSent is None
                or not(date_parser.parse(self.persistentState.lastTowelMailSent, '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d') == datetime.datetime.now(self.settings.timezone).strftime('%Y-%m-%d'))
            ) and (
                now.strftime('%a').lower() == tingbot.app.settings['kitchenteam']['towels_cleaning']['reminder_email_day']
                and
                Utils.time_in_range(
                    datetime.time(8, 0, 0),
                    datetime.time(18, 59, 59),
                    now.time()
                )
            )
        )

    def sendmail_team(self):
        today = datetime.datetime.now(self.settings.timezone).strftime('%a').lower()
        today_full = datetime.datetime.now(self.settings.timezone).strftime('%A').lower()

        for receiver in tingbot.app.settings['kitchenteam']['teams'][today]:
            team = []
            for member in tingbot.app.settings['kitchenteam']['teams'][today]:
                if receiver[1] != member[1]:
                    team.append(member[0])

            msg = "Good morning " + receiver[0] + ",\n\n"
            msg += "It's " + today_full + " again and as you know, today you are part of the kitchen cleaning team.\n"
            msg += "You're teammates are " + ", ".join(team[:-1]) + " and " + team[-1] + ".\n"
            msg += "\nHave a wonderful day.\n"
            msg += "Kind regards, the coffeeBot\n"
            msg += "\nPS: Here you'll find an overview of the tasks for the kitchen team.\n"
            msg += "http://wiki.orangehive.de/index.php/Kitchen-rules#Duties_for_the_current_team\n"
            Utils.sendmail(receiver[1], receiver[0], 'You\'re part of the team!', msg, expires_minutes=720)

    def sendmail_towel_cleaning_team(self):
        start_date = date_parser.parse(tingbot.app.settings['kitchenteam']['towels_cleaning']['start_date'], '%Y-%m-%d').replace(tzinfo=self.settings.timezone)
        days = (datetime.datetime.now(self.settings.timezone) - start_date).days
        weeks = math.floor(days / 7)
        team_count = len(tingbot.app.settings['kitchenteam']['teams'])
        team_days = {}
        weekdays = list(calendar.day_abbr)
        team_day_count = 1

        for weekday in weekdays:
            if weekday.lower() in tingbot.app.settings['kitchenteam']['teams'].keys():
                team_days[team_day_count] = weekday.lower()
                team_day_count += 1

        if team_count > 0:
            team_day = team_days[weeks % team_count]

            for receiver in tingbot.app.settings['kitchenteam']['teams'][team_day]:
                team = []
                for member in tingbot.app.settings['kitchenteam']['teams'][team_day]:
                    if receiver[1] != member[1]:
                        team.append(member[0])

                msg = "Good morning " + receiver[0] + ",\n\n"
                msg += "It's this time again. This week you are part of the kitchen towel cleaning team.\n"
                msg += "You're teammates are " + ", ".join(team[:-1]) + " and " + team[-1] + ".\n"
                msg += "\nHave a wonderful day.\n"
                msg += "Kind regards, the coffeeBot\n"
                Utils.sendmail(receiver[1], receiver[0], 'You\'re part of the towel cleaning team!', msg, expires_minutes=10080)

    def background(self):
        super(Kitchenteam, self).background()

        if self.is_team_armed():
            self.persistentState.lastMailSent = datetime.datetime.now(self.settings.timezone).strftime('%Y-%m-%dT%H:%M:%S')
            self.parent.save_persistent_state()

            self.sendmail_team()

        if self.is_towel_cleaning_team_armed():
            self.persistentState.lastTowelMailSent = datetime.datetime.now(self.settings.timezone).strftime('%Y-%m-%dT%H:%M:%S')
            self.parent.save_persistent_state()

            self.sendmail_towel_cleaning_team()
