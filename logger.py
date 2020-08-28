import logging
import timber
from datetime import datetime

_SOURCE_ID = 39380
_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9." \
           "eyJhdWQiOiJodHRwczovL2FwaS50aW1iZXIuaW" \
           "8vIiwiZXhwIjpudWxsLCJpYXQiOjE1OTMxOTQ1ODMsIm" \
           "lzcyI6Imh0dHBzOi8vYXBpLnRpbWJlci5pby9hcGlfa2V5c" \
           "yIsInByb3ZpZGVyX2NsYWltcyI6eyJhcGlfa2V5X2lkIjo4ND" \
           "gyLCJ1c2VyX2lkIjoiYXBpX2tleXw4NDgyIn0sInN1YiI6Im" \
           "FwaV9rZXl8ODQ4MiJ9.Qa6gvuboX-MAv-75YxuMckFZRqmG6SsM3TZ47wjYk8g"


class Logger:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Set to logging.DEBUG if you want all logs
        self.logger.setLevel(logging.INFO)

        timber_handler = timber.TimberHandler(source_id=_SOURCE_ID, api_key=_API_KEY)
        self.logger.addHandler(timber_handler)

    def log_user(self, chat_id, text):
        self.logger.info(text, extra={
            'time': "wadj",
            'chat_id': chat_id
        })

    def log_action(self, text):
        self.logger.info(text, extra={
            'time':datetime.now(),
        })

logger = Logger()
print(4)
logger.log_user("aawdawd","Hey, guys")