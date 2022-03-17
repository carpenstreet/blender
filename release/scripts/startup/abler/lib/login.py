import psutil


def is_first_open() -> bool:
    # 윈도우에선 blender.exe로 인식
    # 추후 abler.exe로 만들 경우를 대비
    process_count: int = sum(
        i.startswith("ABLER") or i.startswith("blender") or i.startswith("abler")
        for i in (p.name() for p in psutil.process_iter())
    )
    return process_count <= 1
