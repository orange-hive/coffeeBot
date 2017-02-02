import os
import json
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import threading
import tingbot


class Utils(object):

    @staticmethod
    def time_in_range(start, end, x):
        """Return true if x is in the range [start, end]"""
        if start <= end:
            return start <= x <= end
        else:
            return start <= x or x <= end        

    @staticmethod
    def get_audio_resource(name):
        """
        Returns the path to a resource bundled in this app (at audio/<name>)
        """
        return os.path.realpath(os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'audio', name)))

    @staticmethod
    def get_audio_text_resource(name):
        """
        Returns the path to a resource bundled in this app (at audio/text/<name>)
        """
        return os.path.realpath(os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'audio', 'text', name)))

    @staticmethod
    def get_font_resource(name):
        """
        Returns the path to a resource bundled in this app (at fonts/<name>)
        """
        return os.path.realpath(os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'fonts', name)))
        
    @staticmethod
    def write_state(state):
        stateFile = os.path.realpath(os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'state.json')))
        f = open(stateFile, 'w')
        json.dump(state, f)
        f.close()

    @staticmethod
    def read_state():
        stateFile = os.path.realpath(os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'state.json')))
        if os.path.exists(stateFile):
            f = open(stateFile, 'r')
            state = json.load(f)
            f.close()
        else:
            state = None
        return state

    @staticmethod
    def sendmail(to_email, to_name, subject, message):
        def sender():
            server = smtplib.SMTP(
                tingbot.app.settings['coffeeBot']['smtp']['host'],
                tingbot.app.settings['coffeeBot']['smtp']['port'],
                tingbot.app.settings['coffeeBot']['smtp']['helo']
            )
            server.login(
                tingbot.app.settings['coffeeBot']['smtp']['login'],
                tingbot.app.settings['coffeeBot']['smtp']['password']
            )

            msg = MIMEText(message.encode('utf-8'), 'plain', 'utf-8')
            msg['Subject'] = Header(subject, 'utf-8')
            msg['From'] = tingbot.app.settings['coffeeBot']['smtp']['sender'][0] + ' <' + tingbot.app.settings['coffeeBot']['smtp']['sender'][1] + '>'
            msg['To'] = "\"%s\" <%s>" % (Header(to_name, 'utf-8'), to_email)

            if tingbot.app.settings['coffeeBot']['debug']:
                server.sendmail(tingbot.app.settings['coffeeBot']['smtp']['sender'][1], tingbot.app.settings['coffeeBot']['debugEmail'], msg.as_string())
            else:
                server.sendmail(tingbot.app.settings['coffeeBot']['smtp']['sender'][1], to_email, msg.as_string())
            server.quit()

        senderThread = threading.Thread(target=sender)
        senderThread.start()
