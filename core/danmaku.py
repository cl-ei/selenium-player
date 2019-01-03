import time
import json
import requests


cookie = "fts=1541171981; sid=b0003jl4; stardustvideo=1; CURRENT_FNVAL=16; buvid3=9645244A-D8C0-410E-833A-5587A2AA599C19606infoc; rpdid=olilokixwsdospoomkopw; UM_distinctid=166d776b4c6b92-09b54593d87465-5701631-384000-166d776b4c74b1; LIVE_BUVID=3b5372efb95a5ec31687743d461b126e; LIVE_BUVID__ckMd5=7ee74f07c3ef3ecb; pgv_pvi=9527141376; _cnt_dyn=undefined; _cnt_pm=0; _cnt_notify=0; uTZ=-480; im_notify_type_129366979=0; im_notify_type_20932326=0; im_local_unread_20932326=0; finger=edc6ecda; CURRENT_QUALITY=116; im_seqno_20932326=2506; DedeUserID=20932326; DedeUserID__ckMd5=65761b2ed76c89e1; SESSDATA=784abdaa%2C1548343766%2C9c840bc1; bili_jct=cf64a4808187752fbc9e45928ad38171; _uuid=52A71081-9654-EDD0-2524-BAF112B1EDCD95100infoc; _dfcaptcha=fa14fcede35dd638f2b610143c76667a; bp_t_offset_20932326=203696585018921402; Hm_lvt_8a6e55dbd2870f0f5bc9194cddf32a02=1546270514,1546270816,1546271038,1546271371; Hm_lpvt_8a6e55dbd2870f0f5bc9194cddf32a02=1546273260"
csrf_token = ""

for kv in cookie.split(";"):
    if "bili_jct" in kv:
        csrf_token = kv.split("=")[-1].strip()
        break
headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko)",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Cookie": cookie,
}


def send_danmaku(msg, roomid=13369254, color=0xffffff):
    data = {
        "color": color,
        "fontsize": 25,
        "mode": 1,
        "msg": msg,
        "rnd": int(time.time()),
        "roomid": roomid,
        "csrf_token": csrf_token,
    }
    r = requests.post(url="https://live.bilibili.com/msg/send", data=data, headers=headers)
    try:
        response = json.loads(r.content.decode("utf-8"))
        if response.get("code") == 0:
            return True
        print("SEND_DANMAKU ERROR: req: %s, response: %s" % (data, r.content))
    except Exception as e:
        print("SEND_DANMAKU ERROR: %s, data: %s" % (e, data))
