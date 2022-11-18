from time import strftime, localtime, gmtime


def timestamp_to_string(timestamp, is_date=True):
    if not timestamp:
        return "- - -"
    if is_date:
        return strftime("%H:%M:%S", localtime(timestamp))
    return strftime("%H:%M:%S", gmtime(timestamp))
