import time
from typing import Any

import bpy
import sentry_sdk

from ._tracker import Tracker
from ._versioning import get_version


class SentryTracker(Tracker):
    def __init__(self, sentry_dsn: str):
        super().__init__()
        sentry_sdk.init(
            sentry_dsn,
            release=make_release_version(),
            environment="production" if get_version() else "development",
        )

    def _enqueue_event(self, event_name: str, properties: dict[str, Any]):
        sentry_sdk.add_breadcrumb(
            category="event", message=event_name, timestamp=time.time()
        )

    def _enqueue_email_update(self, email: str):
        sentry_sdk.set_user({"email": email})


def make_release_version():
    """
    release/v0.0.1 형태의 경우 -> abler.release@0.0.1+hash 형태로 출력.
    기타 -> abler.devel@hash 형태로 출력.
    참고: https://docs.sentry.io/platforms/python/configuration/releases/
    """

    package = "abler.devel"
    version = bpy.app.build_hash.decode("ascii")

    if v := get_version():
        major, minor, patch = v
        package = "abler.release"
        version = f"{major}.{minor}.{patch}+{version}"

    return package + "@" + version
