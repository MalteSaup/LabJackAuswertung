import threading
import time

def test():
    while True:
        print(time.perf_counter())
        time.sleep(0.5)



t = threading.Thread(target=test)
t.start()
