import logging

class CustomLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        return '[%s] %s' % (self.extra['dyno_name'], msg), kwargs

