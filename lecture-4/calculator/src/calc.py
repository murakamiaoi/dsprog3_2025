import flet as ft
import math # 科学計算のためにmathモジュールをインポート

# --- ボタンの基底クラス ---
class CalcButton(ft.ElevatedButton):
    def __init__(self, text, button_clicked, expand=1):
        super().__init__()
        self.text = text
        self.expand = expand
        self.on_click = button_clicked
        self.data = text

# --- 数字ボタン (既存) ---
class DigitButton(CalcButton):
    def __init__(self, text, button_clicked, expand=1):
        CalcButton.__init__(self, text, button_clicked, expand)
        self.bgcolor = ft.Colors.WHITE24
        self.color = ft.Colors.WHITE

# --- 算術演算子ボタン (既存) ---
class ActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.Colors.ORANGE
        self.color = ft.Colors.WHITE

# --- AC, +/-, % ボタン (既存) ---
class ExtraActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.Colors.BLUE_GREY_100
        self.color = ft.Colors.BLACK

# --- 科学計算ボタン (新規追加) ---
class ScientificActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        # 科学計算ボタン用に色を設定
        self.bgcolor = ft.Colors.INDIGO_300
        self.color = ft.Colors.WHITE


class CalculatorApp(ft.Container):
    def __init__(self):
        super().__init__()
        self.reset()

        self.result = ft.Text(value="0", color=ft.Colors.WHITE, size=20)
        self.width = 350
        self.bgcolor = ft.Colors.BLACK
        self.border_radius = ft.border_radius.all(20)
        self.padding = 20
        
        # 科学計算ボタンの行を追加
        scientific_buttons = ft.Row(
            controls=[
                ScientificActionButton(text="sin", button_clicked=self.button_clicked),
                ScientificActionButton(text="cos", button_clicked=self.button_clicked),
                ScientificActionButton(text="tan", button_clicked=self.button_clicked),
                ScientificActionButton(text="log", button_clicked=self.button_clicked),
                ScientificActionButton(text="sqrt", button_clicked=self.button_clicked),
            ]
        )

        self.content = ft.Column(
            controls=[
                ft.Row(controls=[self.result], alignment="end"),
                # 科学計算ボタンの行
                scientific_buttons, 
                # 既存のボタンレイアウト
                ft.Row(
                    controls=[
                        ExtraActionButton(text="AC", button_clicked=self.button_clicked),
                        ExtraActionButton(text="+/-", button_clicked=self.button_clicked),
                        ExtraActionButton(text="%", button_clicked=self.button_clicked),
                        ActionButton(text="/", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="7", button_clicked=self.button_clicked),
                        DigitButton(text="8", button_clicked=self.button_clicked),
                        DigitButton(text="9", button_clicked=self.button_clicked),
                        ActionButton(text="*", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="4", button_clicked=self.button_clicked),
                        DigitButton(text="5", button_clicked=self.button_clicked),
                        DigitButton(text="6", button_clicked=self.button_clicked),
                        ActionButton(text="-", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="1", button_clicked=self.button_clicked),
                        DigitButton(text="2", button_clicked=self.button_clicked),
                        DigitButton(text="3", button_clicked=self.button_clicked),
                        ActionButton(text="+", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="0", expand=2, button_clicked=self.button_clicked),
                        DigitButton(text=".", button_clicked=self.button_clicked),
                        ActionButton(text="=", button_clicked=self.button_clicked),
                    ]
                ),
            ]
        )

    def button_clicked(self, e):
        data = e.control.data
        print(f"Button clicked with data = {data}")
        
        # AC (All Clear) or Error state
        if self.result.value == "Error" or data == "AC":
            self.result.value = "0"
            self.reset()
        
        # Digits and Decimal Point
        elif data in ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "."):
            if self.result.value == "0" or self.new_operand == True:
                # 既に小数点が入力されている場合は、二重入力を防ぐ
                if data == "." and "." in self.result.value and not self.new_operand:
                    pass
                else:
                    self.result.value = data if data != "." or self.result.value == "0" else self.result.value + data
                    self.new_operand = False
            else:
                # 既に小数点が入力されている場合は、二重入力を防ぐ
                if data == "." and "." in self.result.value:
                    pass
                else:
                    self.result.value = self.result.value + data

        # Arithmetic Operators (+, -, *, /)
        elif data in ("+", "-", "*", "/"):
            # 前の演算を実行し、結果を次のオペランド1とする
            self.result.value = self.calculate(self.operand1, float(self.result.value), self.operator)
            self.operator = data
            if self.result.value == "Error":
                self.operand1 = "0"
            else:
                self.operand1 = float(self.result.value)
            self.new_operand = True
        
        # Equals (=)
        elif data in ("="):
            self.result.value = self.calculate(self.operand1, float(self.result.value), self.operator)
            self.reset()

        # Percentage (%)
        elif data in ("%"):
            try:
                self.result.value = self.format_number(float(self.result.value) / 100)
                self.new_operand = True
            except ValueError:
                self.result.value = "Error"
                self.reset()

        # Sign Change (+/-)
        elif data in ("+/-"):
            try:
                current_value = float(self.result.value)
                self.result.value = self.format_number(-current_value)
            except ValueError:
                self.result.value = "Error"
                self.reset()
                
        # --- 科学計算ボタンの処理 (新規追加) ---
        elif data in ("sin", "cos", "tan", "log", "sqrt"):
            try:
                current_value = float(self.result.value)
                
                if data == "sin":
                    # Fletは度数法ではないため、ラジアンに変換して計算
                    self.result.value = self.format_number(math.sin(math.radians(current_value)))
                elif data == "cos":
                    self.result.value = self.format_number(math.cos(math.radians(current_value)))
                elif data == "tan":
                    self.result.value = self.format_number(math.tan(math.radians(current_value)))
                elif data == "log":
                    # 負の数やゼロの対数を防ぐ
                    if current_value <= 0:
                        self.result.value = "Error"
                    else:
                        # 自然対数 (ln) を使用 (必要に応じて math.log10 に変更可能)
                        self.result.value = self.format_number(math.log(current_value))
                elif data == "sqrt":
                    # 負の数の平方根を防ぐ
                    if current_value < 0:
                        self.result.value = "Error"
                    else:
                        self.result.value = self.format_number(math.sqrt(current_value))
                        
                # 科学計算ボタンの実行後、次の入力を新しいオペランドとする
                self.new_operand = True
                self.operand1 = 0 # 連続計算をリセット
                self.operator = "+" # 連続計算をリセット

            except ValueError:
                self.result.value = "Error"
                self.reset()
            except Exception: # ゼロ除算などのmathエラー対策
                self.result.value = "Error"
                self.reset()

        self.update()

    def format_number(self, num):
        # 浮動小数点数の桁数を丸める
        if isinstance(num, (float, int)):
            rounded_num = round(num, 10) # 小数点以下10桁に丸める
            if rounded_num % 1 == 0:
                return int(rounded_num)
            else:
                return rounded_num
        return num # 数値でない場合はそのまま返す

    def calculate(self, operand1, operand2, operator):
        # ... (既存の calculate メソッドは変更なし) ...
        if operator == "+":
            return self.format_number(operand1 + operand2)

        elif operator == "-":
            return self.format_number(operand1 - operand2)

        elif operator == "*":
            return self.format_number(operand1 * operand2)

        elif operator == "/":
            if operand2 == 0:
                return "Error"
            else:
                return self.format_number(operand1 / operand2)
        
        # 演算子が設定されていない場合 (例: AC後の=)
        return self.format_number(operand2) 

    def reset(self):
        # ... (既存の reset メソッドは変更なし) ...
        self.operator = "+"
        self.operand1 = 0
        self.new_operand = True


def main(page: ft.Page):
    page.title = "Simple Scientific Calculator"
    # ページ設定を調整して、電卓が見やすくなるようにする
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    calc = CalculatorApp()
    page.add(calc)


ft.app(main)
