import psutil


def is_process_single() -> bool:
    """
    Check if only one Abler process is running

    Window: blender / macOS: abler
    """
    # TODO: Window 에서 프로세스 이름 abler 로 변경하기
    process_count: int = sum(
        i.startswith("ABLER") or i.startswith("blender") or i.startswith("abler")
        for i in (p.name() for p in psutil.process_iter())
    )
    return process_count <= 1
