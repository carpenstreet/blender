from contextlib import contextmanager
import bpy


@contextmanager
def file_view_title(title_enum):
    """
    :param title_enum: WM_types.h 의 abler_fileViewTitle 참고
    """
    # set_fileselect_title가 없어서 발생하는 에러로 인해 if문 추가
    # 해당 이슈 링크: https://www.notion.so/acon3d/file_view_title-set_fileselect_title-98b55d3116f942f69759f0d63dd7be35?pvs=4
    if set_fileselect_title := bpy.context.window_manager.set_fileselect_title:
        set_fileselect_title(title_enum=title_enum)
        yield
        # 바로 기본값으로 되돌리면 위쪽 변경사항이 반영되지 않은 채 파일 다이얼로그가 나타나는 문제가 있어서, 한 틱 뒤에 원상복구
        bpy.app.timers.register(
            lambda: set_fileselect_title(
                title_enum="DEFAULT"
            )
        )
