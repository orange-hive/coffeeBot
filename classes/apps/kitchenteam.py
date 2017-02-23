from ..base import AppBase
from ..utils import Utils
import datetime
import tingbot


class Kitchenteam(AppBase):
    
    def __init__(self, parent, timezone):
        super(Kitchenteam, self).__init__(parent)

        self.init_settings(
            timezone=timezone
        )

        self.init_persistent_states(
            lastMailSent=None
        )

    def is_armed(self):
        return (
            (
                self.persistentState.lastMailSent is None
                or not(datetime.datetime.strptime(self.persistentState.lastMailSent, '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d') == datetime.datetime.now(self.settings.timezone).strftime('%Y-%m-%d'))
            ) and (
                Utils.time_in_range(
                    datetime.time(8, 0, 0),
                    datetime.time(8, 59, 59),
                    datetime.datetime.now(self.settings.timezone).time()
                )
            )
        )

    def sendmail(self):
        today = datetime.datetime.now(self.settings.timezone).strftime('%a').lower()
        today_full = datetime.datetime.now(self.settings.timezone).strftime('%A').lower()

        for receiver in tingbot.app.settings['kitchenteam'][today]:
            team = []
            for member in tingbot.app.settings['kitchenteam'][today]:
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

    def background(self):
        super(Kitchenteam, self).background()

        if self.is_armed():
            self.persistentState.lastMailSent = datetime.datetime.now(self.settings.timezone).strftime('%Y-%m-%dT%H:%M:%S')
            self.parent.save_persistent_state()

            self.sendmail()
