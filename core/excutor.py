#-*- coding: utf-8 -*-
import time
from selenium import webdriver


SONG_FILE_PATH = "./song.txt"
SEARCH_URL = "http://music.163.com/#/search/m/?s="
PLAY_URL = "http://music.163.com/#/song?id="

GLOBAL_BROWSER = []


def player(song):
    print("\tSYSTEM ACTION: Play: [%s]" % song)
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-infobars")
    browser = webdriver.Chrome(executable_path="./chromedriver.exe", port=9515, options=options)

    GLOBAL_BROWSER.insert(0, browser)

    browser.set_window_position(1000, 0)
    browser.set_window_size(1050, 1120)
    try:
        browser.get(SEARCH_URL + song)
        browser.switch_to.frame("g_iframe")
        es = browser.find_elements_by_css_selector(".srchsongst .item")
        song_id = ""
        for e in es:
            try:
                if "js-dis" in e.get_attribute("class"):
                    continue
                song_id = e.find_element_by_tag_name("a").get_attribute("id").split("_")[-1]
                break
            except Exception:
                continue

        if song_id:
            print("\tSYSTEM ACTION: Got Song [%s] id: %s" % (song, song_id))
        else:
            print("\tSYSTEM ACTION: Song [%s] not found!" % song)
            return

        browser.get(PLAY_URL + song_id)
        browser.find_element_by_css_selector(".btn[data-action='lock']").click()
        for _ in range(10):
            try:
                browser.find_element_by_css_selector(".btn[data-action='lock']").click()
            except Exception:
                pass

            time.sleep(0.5)
            try:
                browser.find_element_by_class_name("m-playbar-lock")
            except Exception:
                continue
            else:
                break
        else:
            print("\tSYSTEM EXCEPTION: 因网络问题播放器已关闭。")
            return

        browser.switch_to.frame("g_iframe")
        for _ in range(20):
            try:
                browser.find_element_by_class_name("u-btni-addply").click()
                break
            except Exception:
                time.sleep(0.5)
                continue
        else:
            print("\tSYSTEM EXCEPTION: 因网络问题播放器已关闭。")
            return

        try:
            browser.find_element_by_id("flag_ctrl").click()
        except Exception:
            pass

        browser.switch_to.default_content()
        time.sleep(5)

        try:
            current_time, total_time = browser.find_element_by_css_selector(".m-pbar .time").text.split("/")
            current_time = [int(x) for x in current_time.strip(" ").split(":")]
            total_time = [int(x) for x in total_time.strip(" ").split(":")]
            sleep_time = (total_time[0] - current_time[0])*60 + (total_time[1] - current_time[1])
            time.sleep(sleep_time - 1)
        except Exception:
            pass
        return
    except Exception as e:
        print("\tSYSTEM EXCEPTION: An error happend when playing [%s]: %s" % (song, e))
    finally:
        browser.close()
        GLOBAL_BROWSER.remove(browser)
        print("\tSYSTEM ACTION: Player[%s] closed." % song)
