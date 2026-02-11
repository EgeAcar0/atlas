import webbrowser
import psutil

def open_website(url: str):
    """
    Belirtilen URL'yi varsayılan tarayıcıda açar.
    """
    if not url.startswith("http"):
        url = "https://" + url
    
    try:
        webbrowser.open(url)
        return f"{url} açılıyor..."
    except Exception as e:
        return f"Site açılırken hata: {str(e)}"

def get_system_stats():
    """
    CPU ve RAM kullanım oranlarını döndürür.
    """
    try:
        cpu_usage = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()
        ram_usage = memory.percent
        
        return f"Sistem Durumu: CPU Kullanımı %{cpu_usage}, RAM Kullanımı %{ram_usage}"
    except Exception as e:
        return f"Sistem verileri alınamadı: {str(e)}"