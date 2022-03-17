from typing import Optional
import bpy
from .tracker import tracker
from ..custom_properties import AconSceneProperty


def tracker_file_open() -> Optional[bool]:

    # tracking file_open
    if bpy.data.filepath != "":
        tracker.file_open()
        return True


def change_and_reset_value() -> None:

    # 파일 맨 처음 열었을때 custom properties의 속성들이 업데이트 되지 않는 문제를 해결하기 위해
    # 만들어둔 함수

    properties = AconSceneProperty.__annotations__
    for property in properties:
        original_value = getattr(bpy.context.scene.ACON_prop, property)
        if type(original_value) == float or type(original_value) == int:
            setattr(bpy.context.scene.ACON_prop, property, original_value)
        elif type(original_value) == bool:
            setattr(bpy.context.scene.ACON_prop, property, original_value)

        # string을 뺀 이유 : EnumProperty에 없는 값을 넣어주면 error가 뜸.
        # float = 0, bool = False 처럼 공통으로 들어갈 값이 없음.
        # type 없이 일괄적으로 처리하려고 했으나, EnumProperty에서 error가 나고 에이블러가 멈춰버림
