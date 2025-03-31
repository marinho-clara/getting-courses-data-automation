import time

def start_count_time():
    return time.time()

def end_count_time(start_time):
    end_time = time.time()
    execution_time_seconds = end_time - start_time
    minutes = int(execution_time_seconds // 60)
    seconds = int(execution_time_seconds % 60)
    return f"{minutes}min e {seconds}seg"