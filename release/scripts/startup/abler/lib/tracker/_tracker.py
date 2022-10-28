from abc import *
import enum
from typing import Any, Optional

import bpy

from ._versioning import get_version
from ._get_ip import user_ip


class EventKind(enum.Enum):
    login = "Login"
    login_fail = "Login Fail"
    login_auto = "Login Auto"
    logout = "Logout"
    file_open = "File Open"
    file_open_fail = "File Open Fail"
    render_quick = "Render Quick"
    render_full = "Render Full"
    render_line = "Render Line"
    render_shadow = "Render Shadow"
    render_all_scenes = "Render All Scenes"
    render_snip = "Render Snip"
    import_blend = "Import *.blend"
    import_blend_fail = "Import *.blend Fail"
    import_same_blend_fail = "Import Same *.blend Fail"
    import_fbx = "Import FBX"
    import_fbx_fail = "Import FBX Fail"
    toggle_toolbar = "Toggle Toolbar"
    fly_mode = "Fly Mode"
    scene_add = "Scene Add"
    look_at_me = "Look At Me"
    use_state_on = "Use State On"
    use_state_off = "Use State Off"
    depth_of_field_on = "Depth of Field On"
    depth_of_field_off = "Depth of Field Off"
    background_images_on = "Background Images On"
    background_images_off = "Background Images Off"
    bloom_on = "Bloom On"
    bloom_off = "Bloom Off"
    save = "save"
    save_fail = "Save Fail"
    save_as = "save_as"
    save_as_fail = "Save As Fail"
    group_navigate_bottom = "Group Navigate Bottom"
    group_navigate_top = "Group Navigate Top"
    group_navigate_down = "Group Navigate Down"
    group_navigate_up = "Group Navigate Up"


def accumulate(interval=0):
    """
    동시에 여러 번 실행되는 이벤트를 한 번만 트래킹하고 싶을 때 사용할 수 있는 데코레이터

    첫 호출 이후 다음 이벤트 루프(interval 주어진 경우는 해당 시간이 지나기 전)까지의 호출은 무시
    """

    def deco(f):
        accumulating = False

        def wrapper(*args, **kwargs):
            nonlocal accumulating

            if not accumulating:
                accumulating = True

                def unregister_timer_and_run():
                    nonlocal accumulating
                    f(*args, **kwargs)
                    bpy.app.timers.unregister(unregister_timer_and_run)
                    accumulating = False

                bpy.app.timers.register(
                    unregister_timer_and_run, first_interval=interval
                )

        return wrapper

    return deco


class Tracker(metaclass=ABCMeta):
    def __init__(self):
        self._agreed = True
        self._default_properties = {}
        self._enabled = True

        if v := get_version():
            major, minor, patch = v
            self._default_properties["version"] = f"{major}.{minor}.{patch}"
        else:
            self._default_properties["version"] = "development"

        if user_ip is not None:
            self._default_properties["ip"] = user_ip

    def turn_on(self):
        self._enabled = True

    def turn_off(self):
        self._enabled = False

    @abstractmethod
    def _enqueue_event(self, event_name: str, properties: dict[str, Any]):
        """
        Enqueue a user event to be tracked.

        Implementations must be asynchronous.
        """
        pass

    @abstractmethod
    def _enqueue_profile_update(self, email: str, ip: str):
        """
        Enqueue update of user email and ip.

        Implementations must be asynchronous.
        """
        pass

    def _track(
        self, event_name: str, properties: Optional[dict[str, Any]] = None
    ) -> bool:
        if not self._enabled:
            return False
        if not self._agreed:
            return False

        next_properties = {}
        next_properties.update(self._default_properties)
        if properties:
            next_properties.update(properties)
        try:
            self._enqueue_event(event_name, next_properties)
        except Exception as e:
            print(e)
            return False
        else:
            return True

    def login(self):
        self._track(EventKind.login.value)

    def update_profile(self, email: str, ip: str):
        self._enqueue_profile_update(email, ip)

    def login_fail(self, reason: str):
        self._track(EventKind.login_fail.value, {"reason": reason})

    def login_auto(self):
        self._track(EventKind.login_auto.value)

    def logout(self):
        self._track(EventKind.logout.value)

    def file_open(self):
        self._track(EventKind.file_open.value)

    def file_open_fail(self):
        self._track(EventKind.file_open_fail.value)

    def render_quick(self):
        self._track(EventKind.render_quick.value)

    def render_full(self):
        self._track(EventKind.render_full.value)

    def render_line(self):
        self._track(EventKind.render_line.value)

    def render_shadow(self):
        self._track(EventKind.render_shadow.value)

    def render_all_scenes(self):
        self._track(EventKind.render_all_scenes.value)

    def render_snip(self):
        self._track(EventKind.render_snip.value)

    def import_blend(self):
        self._track(EventKind.import_blend.value)

    def import_blend_fail(self):
        self._track(EventKind.import_blend_fail.value)

    def import_same_blend_fail(self):
        self._track(EventKind.import_same_blend_fail.value)

    def import_fbx(self):
        self._track(EventKind.import_fbx.value)

    def import_fbx_fail(self):
        self._track(EventKind.import_fbx_fail.value)

    def scene_add(self):
        self._track(EventKind.scene_add.value)

    @accumulate()
    def look_at_me(self):
        self._track(EventKind.look_at_me.value)

    def toggle_toolbar(self):
        self._track(EventKind.toggle_toolbar.value)

    def fly_mode(self):
        self._track(EventKind.fly_mode.value)

    @accumulate()
    def use_state_on(self):
        self._track(EventKind.use_state_on.value)

    @accumulate()
    def use_state_off(self):
        self._track(EventKind.use_state_off.value)

    def depth_of_field_on(self):
        self._track(EventKind.depth_of_field_on.value)

    def depth_of_field_off(self):
        self._track(EventKind.depth_of_field_off.value)

    def background_images_on(self):
        self._track(EventKind.background_images_on.value)

    def background_images_off(self):
        self._track(EventKind.background_images_off.value)

    def bloom_on(self):
        self._track(EventKind.bloom_on.value)

    def bloom_off(self):
        self._track(EventKind.bloom_off.value)

    def save(self):
        self._track(EventKind.save.value)

    def save_fail(self):
        self._track(EventKind.save_fail.value)

    def save_as(self):
        self._track(EventKind.save_as.value)

    def save_as_fail(self):
        self._track(EventKind.save_as_fail.value)

    def group_navigate_bottom(self):
        self._track(EventKind.group_navigate_bottom.value)

    def group_navigate_top(self):
        self._track(EventKind.group_navigate_top.value)

    def group_navigate_down(self):
        self._track(EventKind.group_navigate_down.value)

    def group_navigate_up(self):
        self._track(EventKind.group_navigate_up.value)


class DummyTracker(Tracker):
    def __init__(self):
        super().__init__()
        self._agreed = False

    def _enqueue_event(self, event_name: str, properties: dict[str, Any]):
        pass

    def _enqueue_profile_update(self, email: str, ip: str):
        pass


class AggregateTracker(Tracker):
    def __init__(self, *trackers: Tracker):
        super().__init__()
        self.trackers = trackers

    def _enqueue_event(self, event_name: str, properties: dict[str, Any]):
        for t in self.trackers:
            t._enqueue_event(event_name, properties)

    def _enqueue_profile_update(self, email: str, ip: str):
        for t in self.trackers:
            t._enqueue_profile_update(email, ip)
