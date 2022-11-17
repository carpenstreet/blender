import psutil


def is_process_single() -> bool:
    """
    Check if only one Abler process is running

    Window: blender / macOS: abler
    """
    # TODO: Window 에서 프로세스 이름 abler 로 변경하기
    # psutil에서 iteration하면서 process name을 가져올 수 없는 경우가 있어서 try-except로 처리해줌.
    try:
        process_count: int = sum(
            i.startswith("ABLER") or i.startswith("blender") or i.startswith("abler")
            for i in (p.name() for p in psutil.process_iter())
        )
    except Exception as e:
        print(e)
        return True
    else:
        return process_count <= 1
