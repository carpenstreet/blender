from contextlib import contextmanager
import bpy


@contextmanager
def file_view_title(title_enum):
    """
    :param title_enum: WM_types.h 의 abler_fileViewTitle 참고
    """
    if bpy.context.window_manager.set_fileselect_title:
        bpy.context.window_manager.set_fileselect_title(title_enum=title_enum)
        yield
        # 바로 기본값으로 되돌리면 위쪽 변경사항이 반영되지 않은 채 파일 다이얼로그가 나타나는 문제가 있어서, 한 틱 뒤에 원상복구
        bpy.app.timers.register(
            lambda: bpy.context.window_manager.set_fileselect_title(
                title_enum="DEFAULT"
            )
        )
