import re
from typing import Optional

import bpy


def get_version() -> Optional[tuple[int, int, int]]:
    """
    :return version tuple (major, minor, patch) based on release branch name
    """
    branch = bpy.app.build_branch.decode("utf-8", "replace")
    # NOTE: 커밋되지 않은 변경사항이 있는 경우 "branch_name (modified)" 로 출력됨
    if m := re.match(r"release/v(\d+)\.(\d+)\.(\d+)", branch):
        return int(m[1]), int(m[2]), int(m[3])
    else:
        return None
