from mcp.server.fastmcp import FastMCP # type: ignore

# Senin eski ve harika fonksiyonlarını içeri alıyoruz
from functions.weather_func import get_weather # type: ignore
from functions.open_app_func import open_app # type: ignore
from functions.general_func import open_website, get_system_stats # type: ignore
from functions.homework_func import add_homework, check_homework # type: ignore
from functions.play_on_youtube_func import play_on_youtube # type: ignore
from functions.search_wiki_func import search_wiki # type: ignore   

# 1. MCP Sunucumuzu oluşturuyoruz
mcp = FastMCP("AtlasTools")

# 2. Fonksiyonlarını Ollama'nın (Kimi) anlayacağı MCP araçlarına çeviriyoruz

@mcp.tool()
def hava_durumu_getir(sehir: str) -> str:
    """Belirtilen şehrin güncel hava durumunu getirir. (Örn: istanbul, ankara)"""
    return get_weather(sehir)

@mcp.tool()
def uygulama_ac(uygulama_adi: str) -> str:
    """Bilgisayarda bir uygulama açar. Geçerli adlar: hesap makinesi, not defteri, cmd, terminal, boya, paint, gezgin, dosyalar, steam, minecraft, spotify vb."""
    return open_app(uygulama_adi)

@mcp.tool()
def websitesi_ac(url: str) -> str:
    """Belirtilen URL'yi varsayılan tarayıcıda açar."""
    return open_website(url)

@mcp.tool()
def sistem_durumu() -> str:
    """Bilgisayarın anlık CPU ve RAM kullanım oranlarını gösterir."""
    return get_system_stats()

@mcp.tool()
def odev_ekle(tarih: str, ders: str, aciklama: str) -> str:
    """Belirtilen tarihe (YYYY-MM-DD formatında) yeni bir ödev kaydeder."""
    return add_homework(tarih, ders, aciklama)

@mcp.tool()
def odev_kontrol(tarih: str) -> str:
    """Belirtilen tarihteki (YYYY-MM-DD) ödevleri kontrol eder."""
    return check_homework(tarih)

@mcp.tool()
def youtube_video_ac(konu: str) -> str:
    """YouTube'da arama yapar ve istenilen videoyu/konuyu açar."""
    return play_on_youtube(konu)

@mcp.tool()
def wikipedia_arastir(konu: str) -> str:
    """Kullanıcı detaylı bilgi istediğinde Wikipedia'dan özet bilgi getirir."""
    return search_wiki(konu)

if __name__ == "__main__":
    mcp.run()