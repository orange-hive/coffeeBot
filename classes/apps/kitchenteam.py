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

        team = []
        for receiver in tingbot.app.settings['kitchenteam'][today]:
            team.append(receiver[0])

        for receiver in tingbot.app.settings['kitchenteam'][today]:
            msg = "Hi " + receiver[0] + ",\n\n"
            msg += "I kindly remember you, that you are part of the kitchen team today.\n"
            msg += "\nThe team today consists of:\n\n" + "\n".join(team) + "\n\n"
            msg += "\nThank you.\n\n"
            msg += "\nKind regards\n"
            msg += "The coffee bot.\n"
            Utils.sendmail(receiver[1], receiver[0], 'Kitchen Team', msg)

    def background(self):
        super(Kitchenteam, self).background()

        if self.is_armed():
            self.persistentState.lastMailSent = datetime.datetime.now(self.settings.timezone).strftime('%Y-%m-%dT%H:%M:%S')
            self.parent.save_persistent_state()

            self.sendmail()
