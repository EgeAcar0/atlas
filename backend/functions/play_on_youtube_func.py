import webbrowser

def play_on_youtube(topic: str):
    """
    YouTube'da arama yapar ve sonuç sayfasını açar.
    """
    try:
        query = topic.replace(" ", "+")
        url = f"https://www.youtube.com/results?search_query={query}"
        webbrowser.open(url)
        return f"YouTube'da '{topic}' için sonuçlar açılıyor."
    except Exception as e:
        return f"YouTube hatası: {str(e)}"