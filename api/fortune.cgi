#!/usr/local/bin/python3
import sys
import os
import random
import hashlib
import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import _lib

# Fortune data
FORTUNES = [
    "大吉", "中吉", "小吉", "吉", "末吉", "凶", "大凶"
]

FORTUNE_SCORES = {
    "大吉": 100,
    "中吉": 80,
    "小吉": 65,
    "吉": 50,
    "末吉": 35,
    "凶": 20,
    "大凶": 5
}

COLORS = [
    {"name": "赤", "hex": "#FF0000"},
    {"name": "青", "hex": "#0000FF"},
    {"name": "黄", "hex": "#FFFF00"},
    {"name": "緑", "hex": "#00FF00"},
    {"name": "紫", "hex": "#800080"},
    {"name": "オレンジ", "hex": "#FFA500"},
    {"name": "ピンク", "hex": "#FFC0CB"},
    {"name": "白", "hex": "#FFFFFF"},
    {"name": "黒", "hex": "#000000"},
    {"name": "金", "hex": "#FFD700"},
    {"name": "銀", "hex": "#C0C0C0"},
]

ADVICE = [
    "今日は新しいことに挑戦する良い日です",
    "焦らず一歩ずつ進みましょう",
    "周りの人に感謝の気持ちを伝えてみて",
    "直感を信じて行動してみましょう",
    "今日はゆっくり休むことも大切です",
    "笑顔でいることで運気が上がります",
    "小さな変化が大きな幸運を呼びます",
    "今日は何か新しい発見があるかも",
    "人との出会いを大切にしましょう",
    "思い切って決断する時です",
    "コミュニケーションを大切にして",
    "自分を信じて前に進みましょう",
]

LUCKY_ITEMS = [
    "ペン", "ノート", "コーヒー", "お茶", "本", 
    "音楽", "花", "スマートフォン", "時計", "鏡",
    "鍵", "傘", "マグカップ", "クッション", "アクセサリー"
]

def get_daily_seed(date_str=None):
    """Generate a consistent seed for a given date"""
    if date_str is None:
        today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
        date_str = today.strftime("%Y-%m-%d")
    
    seed_hash = hashlib.sha256(date_str.encode()).hexdigest()
    return int(seed_hash[:16], 16)

def handler():
    method = os.environ.get('REQUEST_METHOD', 'GET')
    if method != 'GET':
        raise ValueError("Method not allowed")

    params = _lib.get_query_params()
    date_param = params.get('date', None)  # Optional: YYYY-MM-DD format
    mode = params.get('mode', 'daily').lower()  # 'daily' or 'random'
    
    if mode == 'daily':
        # Use date-based seed for consistent daily fortune
        seed = get_daily_seed(date_param)
        random.seed(seed)
    else:
        # True random for each request
        random.seed()
    
    # Generate fortune
    fortune = random.choice(FORTUNES)
    score = FORTUNE_SCORES[fortune]
    lucky_color = random.choice(COLORS)
    advice = random.choice(ADVICE)
    lucky_item = random.choice(LUCKY_ITEMS)
    lucky_number = random.randint(1, 100)
    
    # Generate sub-category fortunes
    categories = {
        "恋愛運": random.randint(1, 5),
        "仕事運": random.randint(1, 5),
        "金運": random.randint(1, 5),
        "健康運": random.randint(1, 5),
    }
    
    _lib.send_response(data={
        "fortune": fortune,
        "score": score,
        "lucky_color": lucky_color,
        "lucky_item": lucky_item,
        "lucky_number": lucky_number,
        "advice": advice,
        "categories": categories,
        "mode": mode,
        "date": date_param if date_param else datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime("%Y-%m-%d")
    })

if __name__ == "__main__":
    _lib.main(handler)
