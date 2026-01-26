import sys
import os

# フォルダの場所を正しく認識させる設定
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 自作したファイルの読み込み
try:
    from src.データベース import DBHandler
    from src.データ取得 import WikiFetcher
    from src.可視化 import TravelVisualizer
except ImportError as e:
    print(f"エラー: ファイルが見つかりません。フォルダ構造を確認してください。\n{e}")
    sys.exit()

import random

def main():
    print("--- システムを起動しています ---")
    db = DBHandler()
    fetcher = WikiFetcher()
    viz = TravelVisualizer()

    kansai_spots = ["清水寺", "金閣寺", "東大寺", "ユニバーサル・スタジオ・ジャパン", "有馬温泉", "姫路城"]
    
    print("Wikipediaからデータを確認中...")
    for spot in kansai_spots:
        length = fetcher.fetch_length(spot)
        # 知名度に応じた価格をシミュレーション
        price = (length // 6) + random.randint(8000, 18000)
        db.upsert_data(spot, length, price)

    print("\n--- 関西観光データ分析システム ---")
    print(f"分析可能リスト: {', '.join(kansai_spots)}")
    target = input("分析したい地名を入力してください: ")
    
    if target:
        result = viz.generate_report(target)
        print(result)
    else:
        print("地名が入力されませんでした。")

if __name__ == "__main__":
    main()