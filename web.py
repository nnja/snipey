import time
import logging
import threading

from requests import RequestException

from snipey import app
from snipey import event_listener
from snipey.model import Stream

RECONNECT_TIME = 5


def stream_task():
    if app.config['DEBUG']:
        since_time = None
    else:
        since_time = Stream.current().since_mtime_milli

    while True:
        try:
            event_listener.connect(since_time=since_time)
        except RequestException as e:
            logging.error(
                'ERROR: %s. A connection error occured. '
                'Attempting Reconnection in %s seconds...'
                % (e, RECONNECT_TIME))
            time.sleep(RECONNECT_TIME)
        since_time = Stream.current().since_mtime_milli

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')

    stream_thread = threading.Thread(target=stream_task)
    stream_thread.daemon = True
    stream_thread.start()

    app.run()
