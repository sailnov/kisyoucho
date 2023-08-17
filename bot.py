import requests, bs4, re, datetime
from typing import NamedTuple

#month, dayは0埋め
TARGET_URL = "https://www.data.jma.go.jp/stats/etrn/view/hourly_s1.php?prec_no=62&block_no=47772&year={year}&month={month}&day={day}&view=p1"

DATA_DIR = "./data"

START_DATETIME = "2000-01-01"

def get_weather(
        year: int,
        month: int,
        day: int
    ) -> dict:

    url = TARGET_URL.format(year=year, month=month, day=day)
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.content, "html.parser")

    WEATHER_DATA = {}

    # 1時間ごとの気象データを取得
    weather_data = soup.find_all("tr", class_="mtx")
    index = 0
    for item in weather_data:
        if index <= 1:
            index += 1
            continue
        inner_elements = item.find_all("td")
        hour = inner_elements[0].text
        hpa_gentic = inner_elements[1].text
        hpa_sea = inner_elements[2].text
        rain_mm = inner_elements[3].text
        temperature = inner_elements[4].text
        dew_point = inner_elements[5].text
        steam_pressure = inner_elements[6].text
        humidity = inner_elements[7].text
        wind_speed = inner_elements[8].text
        wind_direction = inner_elements[9].text
        sun_hour = inner_elements[10].text
        sun_mj = inner_elements[11].text
        snow_fall = inner_elements[12].text
        snow_in_ground = inner_elements[13].text
        weather_img = re.match(r".*\/(.*)\.gif", str(inner_elements[14].find("img"))).group(1) if inner_elements[14].find("img") else ""
        cloud = inner_elements[15].text
        visibility = inner_elements[16].text
        WEATHER_DATA[hour] = {
            "気圧（現地）": hpa_gentic,
            "気圧（海面）": hpa_sea,
            "降水量（mm）": rain_mm,
            "気温（摂氏）": temperature,
            "露点温度（摂氏）": dew_point,
            "蒸気圧（hPa）": steam_pressure,
            "湿度（％）": humidity,
            "風速（m/s）": wind_speed,
            "風向": wind_direction,
            "日照時間（時間）": sun_hour,
            "日照量（MJ/㎡）": sun_mj,
            "降雪（cm）": snow_fall,
            "積雪（cm）": snow_in_ground,
            "天気": weather_img,
            "雲量": cloud,
            "視程（km）": visibility
        }
        index += 1
    return WEATHER_DATA

def is_day_file_exist(
        year: int,
        month: int,
        day: int,
        ext: str = "csv"
    ) -> bool:
    file_in_dir = f"{DATA_DIR}/{year}_{month}_{day}.{ext}"
    try:
        with open(file_in_dir) as f:
            return True
    except FileNotFoundError:
        return False

def save_weather_data(
    weather_data: dict,
    year: int,
    month: int,
    day: int,
    ext: str = "csv"
    ) -> None:
    file_in_dir = f"{DATA_DIR}/{year}_{month}_{day}.{ext}"
    with open(file_in_dir, "w") as f:
        weather_data_keys = list(weather_data.keys())
        f.write("時刻,気圧（現地）,気圧（海面）,降水量（mm）,気温（摂氏）,露点温度（摂氏）,蒸気圧（hPa）,湿度（％）,風速（m/s）,風向,日照時間（時間）,日照量（MJ/㎡）,降雪（cm）,積雪（cm）,天気,雲量,視程（km）\n")
        for key in weather_data_keys:
            f.write(f"{key},{weather_data[key]['気圧（現地）']},{weather_data[key]['気圧（海面）']},{weather_data[key]['降水量（mm）']},{weather_data[key]['気温（摂氏）']},{weather_data[key]['露点温度（摂氏）']},{weather_data[key]['蒸気圧（hPa）']},{weather_data[key]['湿度（％）']},{weather_data[key]['風速（m/s）']},{weather_data[key]['風向']},{weather_data[key]['日照時間（時間）']},{weather_data[key]['日照量（MJ/㎡）']},{weather_data[key]['降雪（cm）']},{weather_data[key]['積雪（cm）']},{weather_data[key]['天気']},{weather_data[key]['雲量']},{weather_data[key]['視程（km）']}\n")

if __name__ == "__main__":
    assert START_DATETIME, "START_DATETIMEが設定されていません"
    assert DATA_DIR, "DATA_DIRが設定されていません"
    assert TARGET_URL, "TARGET_URLが設定されていません"
    assert re.match(r"\d{4}-\d{2}-\d{2}", START_DATETIME), "START_DATETIMEの🍜ーマットが不正です"

    start_year, start_month, start_day = START_DATETIME.split("-")
    for year in range(int(start_year), datetime.datetime.now().year + 1):
        for month in range(1, 13):
            for day in range(1, 32):
                print(f"[-] {year}年{month}月{day}日のデータを取得します")
                if is_day_file_exist(year, month, day, ext="csv"):
                    print("[-] 既にファイルが存在するためスキップします")
                    continue
                try:
                    weather_data = get_weather(year, month, day)
                    print("[+] データの取得に成功しました")
                    print("[-] ファイルを保存します...")
                    save_weather_data(weather_data, year, month, day)
                    print(f"[+] ファイルの保存に成功しました: {DATA_DIR}/{year}_{month}_{day}.csv")
                except Exception as e:
                    print(f"エラーが発生しました。{e}")
                    continue