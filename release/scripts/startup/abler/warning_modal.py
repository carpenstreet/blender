import platform
import ctypes
import bpy


modal_running = False


class BlockingModalOperator(bpy.types.Operator):
    """
    특정 조건을 만족할 때까지 끌 수 없는 모달

    모달이 닫히게 만드는 방법은 두 가지입니다.
    - acon3d.close_blocking_modal 오퍼레이터를 통해 직접 close_modal 을 호출하거나
    - should_close 에서 False 를 반환하게 만들기

    상속 후, 필요하다면 draw_modal, should_close, after_close 를 오버라이드해서 사용하세요.
    """

    pass_key = {
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "H",
        "I",
        "J",
        "K",
        "L",
        "M",
        "N",
        "O",
        "P",
        "Q",
        "R",
        "S",
        "T",
        "U",
        "V",
        "W",
        "X",
        "Y",
        "Z",
        "ZERO",
        "ONE",
        "TWO",
        "THREE",
        "FOUR",
        "FIVE",
        "SIX",
        "SEVEN",
        "EIGHT",
        "NINE",
        "BACK_SPACE",
        "SEMI_COLON",
        "PERIOD",
        "COMMA",
        "QUOTE",
        "ACCENT_GRAVE",
        "MINUS",
        "PLUS",
        "SLASH",
        "BACK_SLASH",
        "EQUAL",
        "LEFT_BRACKET",
        "RIGHT_BRACKET",
        "NUMPAD_2",
        "NUMPAD_4",
        "NUMPAD_6",
        "NUMPAD_8",
        "NUMPAD_1",
        "NUMPAD_3",
        "NUMPAD_5",
        "NUMPAD_7",
        "NUMPAD_9",
        "NUMPAD_PERIOD",
        "NUMPAD_SLASH",
        "NUMPAD_ASTERIX",
        "NUMPAD_0",
        "NUMPAD_MINUS",
        "NUMPAD_ENTER",
        "NUMPAD_PLUS",
    }

    @classmethod
    def close_modal(cls):
        global modal_running
        modal_running = False
        WM_MT_splash_modal.draw_func = None

    def draw_modal(self, layout):
        raise NotImplementedError()

    def should_close(self, context, event) -> bool:
        global modal_running
        return not modal_running

    def after_close(self, context, event):
        pass

    def execute(self, context):
        return {"FINISHED"}

    def modal(self, context, event):
        if self.should_close(context, event):
            self.close_modal()
            self.after_close(context, event)
            return {"FINISHED"}

        if event.type in ("LEFTMOUSE", "MIDDLEMOUSE", "RIGHTMOUSE"):
            self._invoke_actual_modal(context, event)

        self._sanitize_input(context, event)

        return {"RUNNING_MODAL"}

    def invoke(self, context, event):
        WM_MT_splash_modal.draw_func = self.draw_modal
        context.window_manager.modal_handler_add(self)
        global modal_running
        modal_running = True
        self._invoke_actual_modal(context, event)
        return {"RUNNING_MODAL"}

    def _invoke_actual_modal(self, context, event):
        bpy.ops.wm.splash_modal("INVOKE_DEFAULT")

    def _sanitize_input(self, context, event):
        def char2key(c):
            # 로그인 modal 창 밖에서 마우스 홀드로 modal 없는 상태에서 키보드로 연타할 때
            # ord() expected a character, but string of length 0 found 발생
            # length가 0일 때도 splash 실행
            if not c:
                self._invoke_actual_modal(context, event)

            else:
                result = ctypes.windll.User32.VkKeyScanW(ord(c))
                shift_state = (result & 0xFF00) >> 8
                return result & 0xFF

        if event.type in self.pass_key:
            if platform.system() == "Windows":
                if event.type == "BACK_SPACE":
                    ctypes.windll.user32.keybd_event(char2key("\b"))
                else:
                    ctypes.windll.user32.keybd_event(char2key(event.unicode))
            elif platform.system() == "Darwin":
                import keyboard

                try:
                    if event.type == "BACK_SPACE":
                        keyboard.send("delete")
                    else:
                        keyboard.write(event.unicode)
                except Exception as e:
                    print(e)
            elif platform.system() == "Linux":
                print("Linux")


class CloseBlockingModalOperator(bpy.types.Operator):
    """Close Tutorial Guide"""

    bl_idname = "acon3d.close_blocking_modal"
    bl_label = "OK"

    def execute(self, context):
        BlockingModalOperator.close_modal()
        bpy.ops.wm.splash_modal_close("INVOKE_DEFAULT")
        return {"CANCELLED"}


class WM_MT_splash_modal(bpy.types.Menu):
    """C 코드에서 Python 을 통해 UI 를 그리기 위해 존재하는 클래스

    wm_splash_screen.c 참고
    """

    bl_label = "Warning Modal"
    draw_func = None

    def draw(self, context):
        self.draw_func(self.layout)


classes = (
    WM_MT_splash_modal,
    CloseBlockingModalOperator,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
