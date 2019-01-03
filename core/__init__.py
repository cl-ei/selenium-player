import os
import sys
import time
import random
from multiprocessing import Process, Queue
from threading import Thread
from core.client import start_damaku_monitor
from core import excutor
from core.danmaku import send_danmaku


def print_f(s):
    with open("./sys.txt", "ab") as f:
        f.write(b"\n" + s.encode("utf-8"))
        f.flush()
    print(s)


def play_a_song(q, song):
    t = Thread(target=excutor.player, args=(song, ))
    t.setDaemon(True)
    t.start()

    while True:
        try:
            msg = q.get(block=False)
        except Exception:
            msg = ""

        if msg == "kill" or not t.is_alive():
            print("Prepare to exit player, msg: %s." % msg)

            while len(excutor.GLOBAL_BROWSER) > 0:
                b = excutor.GLOBAL_BROWSER.pop()
                try:
                    b.close()
                    pass
                except Exception:
                    pass
            sys.exit(0)


class Core(object):
    def __init__(self, **kwargs):
        self.BROWSER_DRIVER_PATH = kwargs.get("BROWSER_DRIVER_PATH", "")
        self.BLOCK_USERS = kwargs.get("BLOCK_USERS", set())
        self.DEFAULT_SONGS = kwargs.get("DEFAULT_SONGS", [])

    def run(self):
        q = Queue()
        monitor_process = Process(target=start_damaku_monitor, args=(q, ), daemon=True)
        monitor_process.start()

        player_q = Queue()
        song_list = []
        exc = None
        song_list_idle = False

        while True:
            time.sleep(1)
            try:
                user, msg = q.get(block=False)

                if user in self.BLOCK_USERS:
                    raise ValueError("Skip")
                if "点歌" not in msg:
                    raise ValueError("Skip")

                song_name = msg.split("点歌")[1].strip()
                if len(song_list) >= 10:
                    send_danmaku("队列里歌曲比较多，请稍后再点歌。")
                elif song_name in song_list:
                    send_danmaku("%s已经在队列里。" % song_name)
                else:
                    song_list.insert(0, song_name)

                    if song_list_idle:
                        player_q.put("kill")
                        while exc and exc.is_alive():
                            pass
                    else:
                        send_danmaku("%s将在%s首歌后播放。" % (song_name, len(song_list)))
            except Exception:
                pass

            if exc is None or not exc.is_alive():
                if song_list:
                    song = song_list.pop()
                    song_list_idle = False
                else:
                    song = random.choice(self.DEFAULT_SONGS)
                    song_list_idle = True
                send_danmaku("现在播放: %s" % song)
                exc = Process(target=play_a_song, args=(player_q, song))
                exc.start()

                while not exc.is_alive():
                    pass
