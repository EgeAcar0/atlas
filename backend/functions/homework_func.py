import json
import os
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "homework.json")

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def add_homework(date_str, lesson, description):
    """
    Belirtilen tarihe ödev ekler.
    date_str: YYYY-MM-DD formatında string
    """
    data = load_data()
    if date_str not in data:
        data[date_str] = [] # type: ignore
    
    data[date_str].append({
        "lesson": lesson,
        "description": description,
        "added_at": datetime.now().strftime("%H:%M:%S")
    })
    save_data(data)
    return f"{date_str} tarihi için {lesson} dersine ödev eklendi."

def check_homework(date_str):
    """
    Belirtilen tarihteki ödevleri getirir.
    """
    data = load_data()
    if date_str not in data or not data[date_str]:
        return "O tarihte kayıtlı bir ödeviniz görünmüyor efendim."
    
    response = [f"{date_str} tarihindeki ödevleriniz:"]
    for idx, item in enumerate(data[date_str], 1):
        response.append(f"{idx}. {item['lesson']}: {item['description']}")
    
    return "\n".join(response)
