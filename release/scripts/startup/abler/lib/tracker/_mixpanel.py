import threading
from typing import Optional, Any
import os
from uuid import uuid4, UUID
import threading

from mixpanel import Mixpanel, BufferedConsumer
import bpy

from ._tracker import Tracker


_user_path = bpy.utils.resource_path("USER")
_tid_path = os.path.join(_user_path, "abler_tid")
_tid_length = 36  # UUID str length


def _nonblock(runner):
    def wrapper(*args, **kwargs):
        threading.Thread(target=runner, daemon=True, args=args, kwargs=kwargs).start()

    return wrapper


def read_tid() -> Optional[str]:
    if not os.path.exists(_tid_path):
        return None
    try:
        with open(_tid_path, "r") as f:
            uuid_str = f.read(_tid_length)
            uuid = UUID(uuid_str)  # possible TypeError if uuid_str is invalid
            return str(uuid)
    except:
        remove_tid()
        return None


def generate_and_write_tid() -> Optional[str]:
    try:
        with open(_tid_path, "w") as f:
            tid = str(uuid4())
            f.write(tid)
            return tid
    except:
        return None


def remove_tid():
    try:
        os.remove(_tid_path)
    except:
        pass


class MixpanelResourceInitializeError(Exception):
    pass


class MixpanelResource:
    mp: Mixpanel
    timer: threading.Timer
    # Tracking ID, 기기마다 유일한 것으로 기대됨
    tid: str
    _repeating: bool
    _consumer: BufferedConsumer
    _flush_interval = 5  # seconds

    def __init__(self, token: str):
        self._repeating = True
        self._consumer = BufferedConsumer(max_size=100)

        self.mp = Mixpanel(token, consumer=self._consumer)

        # NOTE: 로그아웃 후 다른 이메일로 로그인하는 경우는 고려하지 않음
        if tid := read_tid() or generate_and_write_tid():
            self.tid = tid
            self.flush_repeatedly()
        else:
            raise MixpanelResourceInitializeError()

    def flush_repeatedly(self):
        if not self._repeating:
            return

        try:
            timer = threading.Timer(self._flush_interval, self.flush_repeatedly)
            timer.daemon = True
            timer.start()
            self.timer = timer

            self._consumer.flush()
        except Exception as e:
            self._repeating = False
            raise e


class MixpanelTracker(Tracker):
    _r: Optional[MixpanelResource] = None
    _mixpanel_token: str

    def __init__(self, mixpanel_token: str):
        super().__init__()
        self._mixpanel_token = mixpanel_token

    def _ensure_resource(self):
        try:
            if self._r is None:
                self._r = MixpanelResource(self._mixpanel_token)
        except Exception as e:
            self.turn_off()
            raise e

    @_nonblock
    def _enqueue_event(self, event_name: str, properties: dict[str, Any]):
        self._ensure_resource()
        self._r.mp.track(self._r.tid, event_name, properties)

    @_nonblock
    def _enqueue_email_update(self, email: str):
        self._ensure_resource()
        self._r.mp.people_set_once(self._r.tid, {"$email": email})
        self._r.mp.alias(self._r.tid, email)
