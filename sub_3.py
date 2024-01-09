import sys
import random
import time
import cv2
import numpy as np
from ppadb.client import Client as AdbClient
from jamo import h2j, j2hcj

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

print("[NOTICE] 시스템은 '세로' 버전에서만 실행됩니다. 해상도:720x1280")

# ADB 연결
adb = AdbClient(host="127.0.0.1", port=5037)
devices = adb.devices()
if not devices:
    print("디바이스를 찾을 수 없습니다. 콘솔창에 adb 명령어를 입력하십시오.")
    quit()
device = devices[0]

stay_time = int(input("머무를 시간(초)을 입력하세요: "))
image_time = float(input("이미지 판별할 시간(초)을 입력하세요(소수점 첫째자리까지 가능): "))

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


while len(urls) < 15:
    url = input("URL을 입력하세요 (15개 이하): ")
    if url == "":
        break
    search_keyword = input("검색할 키워드를 입력하세요: ")
    print(url, search_keyword)
    if url:
        urls.append(url)
        temp = search_keyword
        jamo_str = j2hcj(h2j(temp))
        result = to_english(jamo_str)
        search_keywords.append(result)
    else:
        break
print(url, search_keywords)

threshold = 0.7


def find_image(template_path):
    screenshot = device.screencap()
    with open("screen.png", "wb") as f:
        f.write(screenshot)
    screen = cv2.imread("screen.png", 0)  # 스크린샷을 한 사진
    template = cv2.imread(template_path, 0)
    time.sleep(image_time)
    w, h = template.shape[::-1]
    res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    max_val = np.max(res)
    return max_val, loc, w, h, template


# 사용자 입력
repeat_times = int(input("반복할 횟수를 입력하세요: "))

# 하이아이피 실행
device.shell("am start -n com.haionnet.haiip/com.haionnet.haiip.activities.IntroActivity")
print("VPN 연결을 시작합니다.")
time.sleep(12)

# 반복 횟수에 따른 반복문 추가
for repeat in range(repeat_times):
    for i in range(len(urls)):

        # 크롬 쿠키 삭제 후 시크릿 모드로 검색 시작
        device.shell("am start -n com.android.chrome/com.google.android.apps.chrome.Main")
        time.sleep(3)
        device.shell("input tap 34 70")  # 홈버튼 클릭
        time.sleep(2)
        device.shell("input tap 685 78")  # 메뉴버튼 클릭
        time.sleep(1.5)
        device.shell("input tap 475 220")  # 새 시크릿 탭 클릭
        time.sleep(1.5)
        device.shell("input tap 265 80")  # 검색바 클릭
        time.sleep(1.5)
        print("검색 키워드: " + search_keywords[i])
        device.shell(f"input text '{search_keywords[i]}'")  # 검색어 입력
        time.sleep(1.5)
        device.shell("input tap 38 157")  # 검색 버튼 클릭
        time.sleep(3)
        a_image_path = f"image/a_image_{i}.png"
        time.sleep(image_time)

        # 설정 이미지를 서치합니다.
        search_click = 0
        start_time = time.time()
        while True:
            max_val_a, max_loc_a, w_a, h_a, template_a = find_image(a_image_path)

            if max_val_a > threshold:  # 설정 이미지와 일치하여 클릭합니다.
                device.shell(f"input tap {max_loc_a[1][0] + w_a // 2} {max_loc_a[0][0] + h_a // 2}")
                time.sleep(stay_time)
                break
            else:  # 하단으로 스크롤
                device.shell("input swipe 360 1000 360 200 800")
                time.sleep(2)
                end_time = time.time()
                if end_time - start_time >= 30:
                    print("서칭 시간이 만료되었습니다.")
                    break

        # 인터넷 사용기록(쿠키) 삭제
        device.shell("am start -n com.android.chrome/com.google.android.apps.chrome.Main")
        time.sleep(2)
        device.shell("input tap 34 70")  # 홈버튼 클릭
        time.sleep(2)
        device.shell("input tap 685 78")  # 메뉴버튼 클릭
        time.sleep(1.5)
        device.shell("input tap 426 616")  # 설정버튼 클릭
        time.sleep(1.5)
        device.shell("input tap 164 980")  # 개인정보버튼 클릭
        time.sleep(1.5)
        device.shell("input tap 201 248")  # 인터넷 사용기록 삭제버튼 클릭
        time.sleep(1.5)
        device.shell("input tap 563 1211")  # 인터넷 사용기록(쿠키) 삭제버튼 클릭
        time.sleep(1.5)
        device.shell("am start -n com.android.chrome/com.google.android.apps.chrome.Main")
        time.sleep(1.5)
        device.shell("input tap 615 74")  # 탭 관리버튼 클릭
        time.sleep(1.5)
        device.shell("input tap 320 160")  # 시크릿 탭 닫기
        time.sleep(1.5)
        device.shell("input keyevent KEYCODE_BACK")  # 이전버튼 클릭
        time.sleep(1.5)

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
