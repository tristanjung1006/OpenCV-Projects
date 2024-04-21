import sys
import random
import time
import cv2
import numpy as np
from ppadb.client import Client as AdbClient
from jamo import h2j, j2hcj
import os

sys.stdin.reconfigure(encoding='utf-8')

korean_alphabet = {
    'ㄱ': 'r',
    'ㄲ': 'R',
    'ㄴ': 's',
    'ㄷ': 'e',
    'ㄸ': 'E',
    'ㄹ': 'f',
    'ㅁ': 'a',
    'ㅂ': 'q',
    'ㅃ': 'Q',
    'ㅅ': 't',
    'ㅆ': 'T',
    'ㅇ': 'd',
    'ㅈ': 'w',
    'ㅉ': 'W',
    'ㅊ': 'c',
    'ㅋ': 'z',
    'ㅌ': 'x',
    'ㅍ': 'v',
    'ㅎ': 'g',
    'ㅏ': 'k',
    'ㅑ': 'i',
    'ㅓ': 'j',
    'ㅕ': 'u',
    'ㅜ': 'n',
    'ㅠ': 'b',
    'ㅗ': 'h',
    'ㅛ': 'y',
    'ㅡ': 'm',
    'ㅣ': 'l',
    'ㅐ': 'o',
    'ㅔ': 'p',
    'ㅚ': 'hl',
    'ㅟ': 'nl',
    'ㅒ': 'O',
    'ㅖ': 'P',
    'ㅘ': 'hk',
    'ㅙ': 'ho',
    'ㅝ': 'nj',
    'ㅞ': 'np',
    'ㅢ': 'ml'
}

# adb 서버 시작
os.system('adb start-server')

# 블루스택 연결
os.system('adb connect 127.0.0.1:5555')

print("[공지] 시스템은 '세로' 버전에서만 실행됩니다. 해상도:720x1280")

# ADB 연결
adb = AdbClient(host="127.0.0.1", port=5037)
devices = adb.devices()
if not devices:
    print("디바이스를 찾을 수 없습니다. 콘솔창에 adb 명령어를 입력하십시오.")
    quit()
device = devices[0]
urls = []
search_keywords = []


def to_english(string):
    result = ''
    for s in string:
        if s == ' ':
            result += ' '
        else:
            result += korean_alphabet[s]
    return result


url = int(input("클릭방지하는 사이트의 갯수를 입력하세요: "))
search_keyword = input("검색할 키워드를 입력하세요: ")
temp = search_keyword
jamo_str = j2hcj(h2j(temp))
result = to_english(jamo_str)
search_keywords.append(result)
repeat_times = int(input("반복할 횟수를 입력하세요: "))
threshold = 0.7


def find_image(template_path):
    screenshot = device.screencap()
    with open("screen.png", "wb") as f:
        f.write(screenshot)
    screen = cv2.imread("screen.png", 0)  # 스크린샷을 한 사진
    template = cv2.imread(template_path, 0)
    time.sleep(3)
    w, h = template.shape[::-1]
    res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    max_val = np.max(res)
    return max_val, loc, w, h, template


def sleep_random_time():
    botprotect = random.randint(1, 2)
    print("봇감지 방지를 위해 " + str(botprotect) + "초만큼 체류합니다.")
    time.sleep(botprotect)


def scroll_screen_down():
    device.shell("input swipe 360 1000 360 200 800")
    print("봇감지 방지를 위해 아래로 스크롤합니다.")


def scroll_screen_up():
    device.shell("input swipe 360 200 360 1000 800")
    print("봇감지 방지를 위해 아래로 스크롤합니다.")


actions = [sleep_random_time(), scroll_screen_down(), scroll_screen_up()]

# 하이아이피 실행
device.shell("am start -n com.haionnet.haiip/com.haionnet.haiip.activities.IntroActivity")
print("VPN 연결을 시작합니다.")
time.sleep(10)

# 반복 횟수에 따른 반복문 추가
for repeat in range(repeat_times):
    for i in range(url):

        # 크롬 쿠키 삭제 후 시크릿 모드로 검색 시작
        device.shell("am start -n com.android.chrome/com.google.android.apps.chrome.Main")
        time.sleep(3)
        device.shell("input tap 34 70")  # 홈버튼 클릭
        time.sleep(2)
        device.shell("input tap 685 78")  # 메뉴버튼 클릭
        time.sleep(2)
        device.shell("input tap 475 220")  # 새 시크릿 탭 클릭
        time.sleep(2)
        device.shell("input tap 265 80")  # 검색바 클릭
        time.sleep(2)
        print("검색 키워드: " + search_keywords[0])
        device.shell(f"input text '{search_keywords[0]}'")  # 검색어 입력
        time.sleep(2)
        device.shell("input tap 38 157")  # 검색 버튼 클릭
        time.sleep(3)
        a_image_path = f"image/a_image_{i}.png"
        c_image_path = f"image/c_image.png"
        time.sleep(1)

        # 설정 이미지를 서치합니다.
        count = 0
        while count <= 4:
            max_val_a, max_loc_a, w_a, h_a, template_a = find_image(a_image_path)
            max_val_c, max_loc_c, w_c, h_c, template_c = find_image(c_image_path)

            if max_val_a > threshold:  # 설정 이미지와 일치하는 것은 클릭하면 안되므로 하단으로 스크롤
                device.shell("input swipe 360 1000 360 200 800")  # 하단으로 스크롤
                time.sleep(2)
            else:  # 설정 이미지와 일치하지 않으므로 클릭한 후 해당 사이트에 체류
                if max_val_c > threshold:
                    device.shell(f"input tap {max_loc_c[1][0] + w_c // 2} {max_loc_c[0][0] + h_c // 2}")
                    time.sleep(15)
                    for _ in range(6):
                        action = random.choice(actions)
                        action()
                    device.shell("input keyevent KEYCODE_BACK")  # 이전 버튼 클릭
                    time.sleep(5)
                    device.shell("input swipe 360 1000 360 200 800")
                    count += 1
                else:
                    print("스폰서 사이트가 더 이상 존재하지 않으므로 서칭을 재시작합니다.")
                    break

        device.shell("am start -n com.android.chrome/com.google.android.apps.chrome.Main")
        time.sleep(2)
        device.shell("input tap 34 70")  # 홈버튼 클릭
        time.sleep(3)
        device.shell("input tap 615 74")  # 탭 관리버튼 클릭
        time.sleep(3)
        device.shell("input tap 320 160")  # 시크릿 탭 닫기
        time.sleep(3)
        device.shell("input keyevent KEYCODE_BACK")  # 이전버튼 클릭
        time.sleep(3)

        # IP 변경
        device.shell("am start -n com.haionnet.haiip/com.haionnet.haiip.activities.IntroActivity")
        time.sleep(2)
        print("IP를 변경합니다.")
        device.shell("input tap 59 243")  # IP 전체선택
        time.sleep(2)
        device.shell("input tap 85 167")  # IP 변경
        time.sleep(2)
        device.shell("input tap 59 243")  # IP 전체해제
        time.sleep(2)
        print("IP 변경 완료했습니다.")
        time.sleep(2)
