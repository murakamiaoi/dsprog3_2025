import flet as ft
import requests
import sqlite3
from datetime import datetime

# 定数
AREA_URL = "http://www.jma.go.jp/bosai/common/const/area.json"
FORECAST_URL = "https://www.jma.go.jp/bosai/forecast/data/forecast/{}.json"
DB_NAME = "weather_history_app.db"

class WeatherDB:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        # エリア情報（オプション: エリア情報をDBに格納）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS areas (
                code TEXT PRIMARY KEY,
                name TEXT
            )
        """)
        # 天気予報
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS forecasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                area_code TEXT,
                report_datetime TEXT,
                forecast_date TEXT,
                weather_text TEXT,
                UNIQUE(area_code, report_datetime, forecast_date)
            )
        """)
        self.conn.commit()

    def save_areas(self, areas_dict):
        cursor = self.conn.cursor()
        for code, info in areas_dict.items():
            cursor.execute("INSERT OR REPLACE INTO areas VALUES (?, ?)", (code, info["name"]))
        self.conn.commit()

    def get_areas(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT code, name FROM areas ORDER BY code")
        return cursor.fetchall()

    def save_forecast(self, area_code, report_time, forecast_list):
        cursor = self.conn.cursor()
        for date, weather in forecast_list:
            cursor.execute("""
                INSERT OR IGNORE INTO forecasts (area_code, report_datetime, forecast_date, weather_text)
                VALUES (?, ?, ?, ?)
            """, (area_code, report_time, date, weather))
        self.conn.commit()

    def get_forecast_by_date(self, area_code, target_date):
        """（オプション: 日付選択で過去の予報を閲覧）"""
        cursor = self.conn.cursor()
        # 指定された日付の予報をすべて取得（発表日時が新しい順）
        cursor.execute("""
            SELECT report_datetime, weather_text FROM forecasts 
            WHERE area_code = ? AND forecast_date = ?
            ORDER BY report_datetime DESC
        """, (area_code, target_date))
        return cursor.fetchall()

class WeatherApp:
    def __init__(self):
        self.db = WeatherDB()

    def initialize_data(self):
        """エリア情報が空ならAPIから取得してDBに保存"""
        areas = self.db.get_areas()
        if not areas:
            print("DBにエリア情報がないため、APIから取得します...")
            res = requests.get(AREA_URL)
            offices = res.json().get("offices", {})
            self.db.save_areas(offices)

    def sync_weather(self, area_code):
        """最新の天気を取得してDBに保存（蓄積）"""
        try:
            res = requests.get(FORECAST_URL.format(area_code))
            data = res.json()
            report_time = data[0]["reportDatetime"]
            time_series = data[0]["timeSeries"][0]
            
            times = [t[:10] for t in time_series["timeDefines"]]
            weathers = time_series["areas"][0]["weathers"]
            
            self.db.save_forecast(area_code, report_time, list(zip(times, weathers)))
        except Exception as e:
            print(f"同期エラー: {e}")

def main(page: ft.Page):
    page.title = "気象庁 天気予報 履歴閲覧システム"
    page.window_width = 900
    page.window_height = 800
    
    app = WeatherApp()
    app.initialize_data()

    # 状態管理用
    state = {"selected_area_code": None, "selected_area_name": None}

    weather_display = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)
    
    def display_weather_cards(area_code, area_name, target_date):
        """DBからデータを読み取って表示"""
        results = app.db.get_forecast_by_date(area_code, target_date)
        
        weather_display.controls.clear()
        weather_display.controls.append(
            ft.Text(f"{area_name} : {target_date} の予報履歴", style=ft.TextThemeStyle.HEADLINE_SMALL)
        )
        
        if not results:
            weather_display.controls.append(ft.Text("該当日のデータがDBにありません。地域を選択して最新データを取得してください。"))
        else:
            grid = ft.ResponsiveRow()
            for report_time, weather in results:
                grid.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text(f"発表時刻: {report_time}", size=12, color=ft.Colors.BLUE_700),
                                ft.Text(weather, size=14),
                            ]),
                            padding=15,
                        ),
                        col={"sm": 12, "md": 6}
                    )
                )
            weather_display.controls.append(grid)
        page.update()

    # 日付選択ハンドラ
    def on_date_change(e):
        if state["selected_area_code"]:
            target_date = e.control.value.strftime("%Y-%m-%d")
            display_weather_cards(state["selected_area_code"], state["selected_area_name"], target_date)

    date_picker = ft.DatePicker(on_change=on_date_change)
    page.overlay.append(date_picker)

    def on_area_click(e):
        state["selected_area_code"] = e.control.data
        state["selected_area_name"] = e.control.title.value
        
        # 最新情報を取得してDBへ
        app.sync_weather(state["selected_area_code"])
        
        # 今日（最新）の情報を表示
        today = datetime.now().strftime("%Y-%m-%d")
        display_weather_cards(state["selected_area_code"], state["selected_area_name"], today)

    # UI構成
    area_list = ft.ListView(expand=True, spacing=2)
    for code, name in app.db.get_areas():
        area_list.controls.append(
            ft.ListTile(title=ft.Text(name), on_click=on_area_click, data=code)
        )

    # メイン表示エリアのヘッダー
    header = ft.Row([
        ft.ElevatedButton("日付を選択して過去予報を閲覧", 
                          icon=ft.Icons.CALENDAR_MONTH, 
                          on_click=lambda _: date_picker.pick_date()),
    ])

    page.add(
        ft.Row(
            [
                ft.Container(content=area_list, width=250, bgcolor=ft.Colors.GREY_100),
                ft.VerticalDivider(width=1),
                ft.Container(
                    content=ft.Column([header, weather_display], expand=True),
                    expand=True, padding=20
                ),
            ],
            expand=True,
        )
    )

if __name__ == "__main__":
    ft.app(target=main)