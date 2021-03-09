def sec_to_hhmm(seconds):
    hours = seconds//3600
    minutes = (seconds-3600*hours)//60
    return str(int(hours)) + ":" + str(int(minutes)).zfill(2)