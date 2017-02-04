import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.header import Header
import threading
import tingbot
import datetime
import pytz


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
    def get_screenshot_resource():
        """
        Returns the path to a resource bundled in this app (at fonts/<name>)
        """
        timezone = pytz.timezone(tingbot.app.settings['coffeeBot']['timezone'])

        return os.path.realpath(
            os.path.normpath(
                os.path.join(
                    os.path.dirname(__file__),
                    '..',
                    'screenshots',
                    datetime.datetime.now(timezone).strftime('%Y%m%d%H%M%S') + '.png'
                )
            )
        )

    @staticmethod
    def write_state(state):
        state_ile = os.path.realpath(os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'state.json')))
        f = open(state_ile, 'w')
        json.dump(state, f)
        f.close()

    @staticmethod
    def read_state():
        state_file = os.path.realpath(os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'state.json')))
        if os.path.exists(state_file):
            f = open(state_file, 'r')
            state = json.load(f)
            f.close()
        else:
            state = None
        return state

    @staticmethod
    def sendmail(to_email, to_name, subject, message, attachments=()):
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

            msg = MIMEMultipart()
            msg['Subject'] = Header(subject, 'utf-8')
            msg['From'] = tingbot.app.settings['coffeeBot']['smtp']['sender'][0] + ' <' + tingbot.app.settings['coffeeBot']['smtp']['sender'][1] + '>'
            msg['To'] = "\"%s\" <%s>" % (Header(to_name, 'utf-8'), to_email)

            body = MIMEText(message.encode('utf-8'), 'plain', 'utf-8')
            msg.attach(body)

            for filename in attachments:
                fp = open(filename, 'rb')
                att = MIMEApplication(fp.read(), _subtype=os.path.splitext(filename)[1])
                fp.close()
                att.add_header('Content-Disposition', 'attachment', filename=filename)
                msg.attach(att)

            if tingbot.app.settings['coffeeBot']['debug']:
                server.sendmail(tingbot.app.settings['coffeeBot']['smtp']['sender'][1], tingbot.app.settings['coffeeBot']['debugEmail'], msg.as_string())
            else:
                server.sendmail(tingbot.app.settings['coffeeBot']['smtp']['sender'][1], to_email, msg.as_string())
            server.quit()

        sender_thread = threading.Thread(target=sender)
        sender_thread.start()
