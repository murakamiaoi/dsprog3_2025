import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

# 日本語フォントの設定（Mac用）
plt.rcParams['font.family'] = 'Hiragino Sans'

class TravelVisualizer:
    def __init__(self, db_name="data/travel_analysis.db"):
        self.db_name = db_name

    def generate_report(self, area_name):
        os.makedirs("output", exist_ok=True) # フォルダ作成
        with sqlite3.connect(self.db_name) as conn:
            df_all = pd.read_sql("SELECT * FROM tourist_spots", conn)
            df_target = pd.read_sql("SELECT * FROM tourist_spots WHERE area_name = ?", 
                                   conn, params=(area_name,))

        if df_target.empty:
            return f"「{area_name}」は見つかりませんでした。"

        plt.figure(figsize=(10, 6))
        plt.scatter(df_all['wiki_length'], df_all['avg_price'], color='skyblue', label='関西の他スポット')
        plt.scatter(df_target['wiki_length'], df_target['avg_price'], color='red', s=200, label='対象')
        
        for i, txt in enumerate(df_all['area_name']):
            plt.annotate(txt, (df_all['wiki_length'].iat[i], df_all['avg_price'].iat[i]))

        plt.title("関西観光地の知名度と宿泊価格の相関")
        plt.xlabel("Wiki文字数")
        plt.ylabel("平均価格(円)")
        
        save_path = f"output/{area_name}_analysis.png"
        plt.savefig(save_path)
        plt.close()
        return f"【成功】グラフを保存しました: {save_path}"