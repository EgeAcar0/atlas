import os
import requests # type: ignore
from dotenv import load_dotenv # type: ignore

load_dotenv()

def get_weather(city: str):
    """
    WeatherAPI kullanarak hava durumu bilgisini çeker.
    """
    api_key = os.getenv("WEATHERAPI_KEY") # .env dosmanda anahtar ismini güncellemeyi unutma
    if not api_key:
        return "Hata: API anahtarı yapılandırılmamış."

    # WeatherAPI URL yapısı
    url = "http://api.weatherapi.com/v1/current.json"
    params = {
        "key": api_key,
        "q": city,
        "lang": "tr"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        
        # HTTP hatalarını (404, 500 vb.) yakalamak için
        response.raise_for_status() 
        
        data = response.json()
        
        location = data["location"]["name"]
        temp = data["current"]["temp_c"]
        condition = data["current"]["condition"]["text"]

        return f"{location} için hava durumu: {condition} Sıcaklık: {temp}°C"

    except requests.exceptions.HTTPError:
        # Şehir bulunamadığında veya API hatasında burası çalışır
        return f"Hata: '{city}' şehri bulunamadı veya servis hatası oluştu."
    except Exception as e:
        return f"Beklenmedik bir hata oluştu: {str(e)}"

# Örnek kullanım
# print(get_weather("Istanbul"))