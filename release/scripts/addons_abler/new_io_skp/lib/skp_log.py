import sys


def skp_log(*args):
    if len(args) > 0:
        print("SU | " + " ".join("%s" % a for a in args))


def progress_bar(head, numerator, denominator):
    rate = numerator / denominator
    bar_length = 50
    block_fill = int(bar_length * rate)
    block_empty = bar_length - block_fill

    # Color: Cyan
    unit_color = "\033[36m"
    end_color = "\033[0m"
    msg_fill = "\033[7m" + " " * block_fill + "\033[27m"
    msg_empty = " " * block_empty
    msg = f"\r{head}: |{unit_color}{msg_fill}{end_color}{msg_empty}| {int(rate * 100)}% ({numerator}/{denominator})"

    # Progress Bar 작업이 끝나면 줄바꿈 추가
    if rate == 1:
        msg += "\n"

    sys.stdout.write(msg)
    sys.stdout.flush()
