#-*- coding: utf-8 -*-
import json
import websocket
import time
import datetime
import sys
import os
from threading import Thread


def print_f(*args, **kwargs):
    pass


ROOM_ID = 13369254
monitor_url = "ws://broadcastlv.chat.bilibili.com:2244/sub"
PACKAGE_HEADER_LENGTH = 16
CONST_MIGIC = 16
CONST_VERSION = 1
CONST_PARAM = 1
CONST_HEART_BEAT = 2
CONST_MESSAGE = 7

MESSAGE_QUEUE = None


def show_danmaku(msg):
    cmd = msg.get("cmd")
    if cmd == "DANMU_MSG":
        content = msg.get("info", "")
        raw_msg = content[1]
        user = content[2][1]
        ul = content[4][0]
        try:
            decoration = content[3][1]
            dl = content[3][0]
        except Exception:
            decoration = ""
            dl = ""

        datetime_str = str(datetime.datetime.now())[:-7]
        msg = '[{}] [UL {: >2}] [{:　<4}{: >2}] {} -> {}'.format(datetime_str, ul, decoration, dl, user, raw_msg)
        print_f(msg)
        if MESSAGE_QUEUE:
            MESSAGE_QUEUE.put([user, raw_msg])


def on_message(ws, message):
    while message:
        length = (message[0] << 24) + (message[1] << 16) + (message[2] << 8) + message[3]
        current_msg = message[:length]
        message = message[length:]
        if len(current_msg) > 16 and current_msg[16] != 0:
            try:
                msg = current_msg[16:].decode("utf-8", errors="ignore")
                msg = json.loads(msg)
                show_danmaku(msg)
            except Exception as e:
                print_f("e: %s, m: %s" % (e, current_msg))
                pass


def on_error(ws, error):
    print_f(error)


def on_close(ws):
    print_f("### closed ###")
    raise RuntimeError("Error! ")


def on_open(ws):
    print_f("ws opened: %s" % ws)
    send_join_room(ws)


def gen_randuser():
    from random import random
    from math import floor
    return int(1E15 + floor(2E15 * random()))


def send_heart_beat(ws):
    hb = generate_heartbeat()
    while True:
        time.sleep(10)
        ws.send(hb)


def send_join_room(ws, uid=None):
    roomid = ROOM_ID
    if not uid:
        uid = gen_randuser()

    package = '{"uid":%s,"roomid":%s}' % (uid, roomid)
    binmsg = generate_packet(CONST_MESSAGE, package)
    ws.send(binmsg)
    t = Thread(target=send_heart_beat, args=(ws, ))
    t.start()


def generate_packet(action, payload=""):
    payload = payload.encode("utf-8")
    packet_length = len(payload) + PACKAGE_HEADER_LENGTH

    buff = bytearray(PACKAGE_HEADER_LENGTH)

    # 前4字节为包长
    buff[0] = (packet_length >> 24) & 0xFF
    buff[1] = (packet_length >> 16) & 0xFF
    buff[2] = (packet_length >> 8) & 0xFF
    buff[3] = packet_length & 0xFF

    # migic & version
    buff[4] = 0
    buff[5] = 16
    buff[6] = 0
    buff[7] = 1

    # action
    buff[8] = 0
    buff[9] = 0
    buff[10] = 0
    buff[11] = action

    # migic parma
    buff[12] = 0
    buff[13] = 0
    buff[14] = 0
    buff[15] = 1

    return buff + payload


def generate_heartbeat():
    return generate_packet(CONST_HEART_BEAT)


def start_damaku_monitor(q=None):
    global MESSAGE_QUEUE
    MESSAGE_QUEUE = q
    ws = websocket.WebSocketApp(
        url=monitor_url,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.on_open = on_open
    ws.run_forever()


if __name__ == "__main__":
    start_damaku_monitor()
