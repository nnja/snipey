from snipey import app
from snipey import event_listener
import logging
import threading


def stream_task():
    event_listener.process_stream(event_listener.open_event_stream())
    # while True:
    #     event_listener.reconnect()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    stream_thread = threading.Thread(target=stream_task)
    stream_thread.daemon = True
    stream_thread.start()

    app.run()
