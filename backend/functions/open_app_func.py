import os

def open_app(app_name: str):
    """
    Temel Windows uygulamalarını açar.
    """
    apps = {
        "hesap makinesi": "calc",
        "not defteri": "notepad",
        "cmd": "cmd",
        "terminal": "cmd",
        "boya": "mspaint",
        "paint": "mspaint",
        "gezgin": "explorer",
        "dosyalar": "explorer",
        "steam": r"C:\Program Files (x86)\Steam\steam.exe",
        "minecraft": "minecraft:",
        "modlu minecraft": "curseforge:",
        "spotify": "spotify:"
    }
    
    cmd = apps.get(app_name.lower())
    
    if cmd:
        try:
            # Eğer bir URI protokolü ise (sonu : ile bitiyorsa)
            if cmd.endswith(":"):
                os.system(f"start {cmd}")
            else:
                # Normal dosya yolu ise boşluklara karşı tırnakla aç
                os.system(f'start "" "{cmd}"')
            return f"{app_name} başlatıldı."
            return f"{app_name} başlatıldı."
        except Exception as e:
            return f"Uygulama açma hatası: {str(e)}"
    else:
        return f"Tanımlı uygulama bulunamadı: {app_name}"
    