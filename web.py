from snipey import app
from snipey import event_listener
from snipey.model import Stream
import logging
import threading


def stream_task():
    if app.config['DEBUG']:
        since_time = None
    else:
        since_time = Stream.current().since_mtime_milli

    event_listener.connect(since_time=since_time)
    while True:
        event_listener.connect(since_time=Stream.current().since_mtime_milli)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    stream_thread = threading.Thread(target=stream_task)
    stream_thread.daemon = True
    stream_thread.start()

    app.run()
