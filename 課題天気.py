import flet as ft
import requests

# 気象庁APIのエンドポイント
AREA_URL = "http://www.jma.go.jp/bosai/common/const/area.json"
FORECAST_URL = "https://www.jma.go.jp/bosai/forecast/data/forecast/{}.json"

class WeatherApp:
    def __init__(self):
        self.areas = {}

    def fetch_areas(self):
        """地域リストを取得"""
        try:
            res = requests.get(AREA_URL)
            res.raise_for_status()
            # 「offices」階層から都府県のリストを取得
            self.areas = res.json().get("offices", {})
        except Exception as e:
            print(f"エリア取得エラー: {e}")

    def fetch_weather(self, area_code):
        """特定の地域の天気情報を取得"""
        try:
            res = requests.get(FORECAST_URL.format(area_code))
            res.raise_for_status()
            return res.json()
        except Exception as e:
            print(f"天気取得エラー: {e}")
            return None

def main(page: ft.Page):
    page.title = "気象庁 天気予報"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 850
    page.window_height = 700
    
    app = WeatherApp()
    app.fetch_areas()

    # 右側：天気表示エリア
    # エラー回避のため、Colorsは大文字の「ft.Colors」を使用します
    weather_display = ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        controls=[ft.Text("左のリストから地域を選択してください", size=16, color=ft.Colors.GREY_500)]
    )

    def on_area_click(e):
        area_code = e.control.data
        area_name = app.areas[area_code]["name"]
        
        weather_display.controls = [ft.ProgressBar(width=400, color="blue")]
        page.update()

        data = app.fetch_weather(area_code)
        
        if data:
            # 予報データの抽出
            report_time = data[0]["reportDatetime"]
            time_series = data[0]["timeSeries"][0]
            forecast_area = time_series["areas"][0]
            
            times = time_series["timeDefines"]
            weathers = forecast_area["weathers"]

            # 表示の更新
            weather_display.controls = [
                ft.Text(f"{area_name} の予報", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.Text(f"発表: {report_time}", size=12, color=ft.Colors.GREY_700),
                ft.Divider(),
            ]
            
            # 各日の予報をカード形式で表示
            grid = ft.ResponsiveRow()
            for i in range(len(weathers)):
                grid.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text(times[i][:10], weight=ft.FontWeight.BOLD),
                                ft.Text(weathers[i], size=13),
                            ]),
                            padding=15,
                        ),
                        col={"sm": 12, "md": 6, "lg": 4} # 画面幅に応じて調整
                    )
                )
            weather_display.controls.append(grid)
        else:
            weather_display.controls = [ft.Text("データの取得に失敗しました", color=ft.Colors.RED)]
        
        page.update()

    # 左側：地域リスト
    area_list = ft.ListView(expand=True, spacing=2)
    for code, info in sorted(app.areas.items()):
        area_list.controls.append(
            ft.ListTile(
                title=ft.Text(info["name"]),
                on_click=on_area_click,
                data=code,
                hover_color=ft.Colors.BLUE_50,
            )
        )

    # 全体レイアウト
    page.add(
        ft.Row(
            [
                ft.Container(
                    content=area_list,
                    width=250,
                    bgcolor=ft.Colors.GREY_100,
                    padding=5,
                ),
                ft.VerticalDivider(width=1),
                ft.Container(
                    content=weather_display,
                    expand=True,
                    padding=20,
                ),
            ],
            expand=True,
        )
    )

# 実行
if __name__ == "__main__":
    ft.app(target=main)