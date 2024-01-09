import sys
import random
import time
import cv2
import numpy as np
import clipboard
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


while len(urls) < 10:
    url = input("URL을 입력하세요 (10개 이하): ")
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
    w, h = template.shape[::-1]
    res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    max_val = np.max(res)
    return max_val, loc, w, h, template


# 사용자 입력
repeat_times = int(input("반복할 횟수를 입력하세요: "))

kc_image_path = "image/koreavpn_connected.png"  # ip 연결 성공을 확인할 수 있는 지표

# koreavpn 접속 후 첫 실행
device.shell("am start -n com.lwfd.koreavpn/com.lwfd.koreavpn.MainActivity")
print("VPN 연결을 시작하고 있습니다.")
time.sleep(5)
device.shell("input tap 350 730")  # Korea VPN 재생버튼 클릭

per = 0
while True:
    max_val_kc, max_loc_kc, w_kc, h_kc, template_kc = find_image(kc_image_path)
    if max_val_kc > 0.9:
        time.sleep(2)
        print("\n새로운 IP 연결에 성공했습니다.")
        break
    else:
        if per == 0:
            print("새로운 IP로 연결중입니다.")
            print("로딩중", end="..")
            per += 1
        else:
            print("..", end="")
            time.sleep(1)
            continue

ip_list = []


def ip_vp():
    # IP Variety Percentage 계산(미사용 함수)
    device.shell("am start -n com.android.chrome/com.google.android.apps.chrome.Main")
    time.sleep(2)
    device.shell("input tap 34 70")  # 홈버튼 클릭
    time.sleep(3)
    device.shell("input tap 677 74")  # 메뉴버튼 클릭
    time.sleep(2)
    device.shell("input tap 435 455")  # 북마크 클릭
    time.sleep(2)

    bm_image_path = "image/moblie_bookmark.png"
    count = 0
    while True:
        max_val_bm, max_loc_bm, w_bm, h_bm, template_bm = find_image(bm_image_path)
        if max_val_bm > 0.7:
            device.shell(f"input tap {max_loc_bm[1][0] + w_bm // 2} {max_loc_bm[0][0] + h_bm // 2}")
            time.sleep(2)
            break
        elif count > 10:
            break
        else:
            count += 1
            continue

    device.shell("input tap 151 165")  # youip.net 사이트 클릭
    time.sleep(3)
    print("IP 수집을 시작합니다.")
    device.shell(f"input tap 250 483")
    clip_text = clipboard.paste()
    ip_list.append(clip_text)
    print(ip_list)


# 반복 횟수에 따른 반복문 추가
for repeat in range(repeat_times):
    for i in range(len(urls)):

        # 검색 시작
        device.shell("am start -n com.android.chrome/com.google.android.apps.chrome.Main")
        time.sleep(2)
        device.shell("input tap 34 70")  # 홈버튼 클릭
        time.sleep(3)
        device.shell("input tap 355 370")  # 검색바 클릭
        time.sleep(2)
        print(search_keywords[i])
        device.shell(f"input text '{search_keywords[i]}'")  # 검색어 입력
        time.sleep(2)
        device.shell("input tap 38 157")  # 검색 버튼 클릭
        time.sleep(4)
        a_image_path = f"image/a_image_{i}.png"
        b_image_path = "image/b_image.png"
        c_image_path = "image/c_image.png"
        d_image_path = "image/d_image.png"

        # 설정 이미지를 서치합니다.
        search_click = 0
        while True:
            max_val_a, max_loc_a, w_a, h_a, template_a = find_image(a_image_path)
            max_val_b, max_loc_b, w_b, h_b, template_b = find_image(b_image_path)
            max_val_c, max_loc_c, w_c, h_c, template_c = find_image(c_image_path)
            max_val_d, max_loc_d, w_d, h_d, template_d = find_image(d_image_path)

            if max_val_a > threshold:  # 설정 이미지와 일치하여 클릭합니다.
                device.shell(f"input tap {max_loc_a[1][0] + w_a // 2} {max_loc_a[0][0] + h_a // 2}")
                break
            elif max_val_b > threshold:  # 검색결과 더보기를 1번만 시행합니다.
                if search_click == 1:
                    device.shell("input swipe 360 200 360 1000 800")
                    break
                else:
                    device.shell(f"input tap {max_loc_b[1][0] + w_b // 2} {max_loc_b[0][0] + h_b // 2}")
                    time.sleep(stay_time)
                    time.sleep(random.randint(1, 4))
                    search_click += 1
            elif max_val_d > threshold:  # 생략된 검색 결과를 포함해 다시 검색합니다.
                device.shell(f"input tap {max_loc_d[1][0] + w_d // 2} {max_loc_d[0][0] + h_d // 2}")
                time.sleep(stay_time)
                time.sleep(random.randint(1, 4))
            elif max_val_c > threshold:  # 모든 정보를 검색하여 홈으로 돌아갈 준비를 합니다.
                device.shell("input swipe 360 200 360 1000 800")
                break
            else:  # 하단으로 스크롤
                device.shell("input swipe 360 1000 360 200 800")
                time.sleep(2)

        # 크롬 기본 사이트로 이동
        device.shell("am start -n com.android.chrome/com.google.android.apps.chrome.Main")
        time.sleep(2)

        # IP 변경
        print("IP 변경 중...")

        device.shell("am start -n com.lwfd.koreavpn/com.lwfd.koreavpn.MainActivity")
        time.sleep(3)
        device.shell("input tap 485 776")  # Korea VPN 정지버튼 클릭
        time.sleep(2)
        device.shell("input tap 231 770")  # Korea VPN ip갱신버튼 클릭
        time.sleep(2)
        device.shell("input tap 350 772")  # Korea VPN 재생버튼 클릭
        time.sleep(2)

        newper = 0
        while True:
            max_val_kc, max_loc_kc, w_kc, h_kc, template_kc = find_image(kc_image_path)
            if max_val_kc > 0.9:
                time.sleep(2)
                print("\n새로운 IP 연결에 성공했습니다.")
                break
            else:
                if newper == 0:
                    print("새로운 IP로 연결중입니다.")
                    print("로딩중", end="..")
                    newper += 1
                else:
                    print("..", end="")
                    time.sleep(1)
                    continue

        time.sleep(2)
        print("IP 변경 완료...")