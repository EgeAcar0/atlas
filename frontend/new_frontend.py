import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,  # type: ignore
                             QLabel, QTextEdit, QPushButton, QHBoxLayout, QGraphicsDropShadowEffect)
# DÜZELTME: pyqtSignal eklendi
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, QPointF, QRectF, pyqtSignal # type: ignore
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen, QFont, QLinearGradient, QRadialGradient

class PulsingMicWidget(QWidget):
    """
    Animasyonlu, nefes alan ve dalga yayan mikrofon butonu.
    """
    # DÜZELTME: Tıklama olayını yakalamak için özel bir sinyal tanımlandı
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent) # type: ignore
        self.setFixedSize(200, 200)
        self.is_listening = False
        self.ripple_radius = 0.0  # Float olarak başlattık
        self.ripple_opacity = 255.0
        
        # Animasyon zamanlayıcısı
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(20)  # 50 FPS

    def update_animation(self):
        # Dalga efekti hesaplaması
        self.ripple_radius += 1.5
        self.ripple_opacity -= 4.0
        
        if self.ripple_radius > 100 or self.ripple_opacity <= 0:
            self.ripple_radius = 50.0
            self.ripple_opacity = 200.0
            
        self.update() # Yeniden çiz

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Merkez noktası
        center = self.rect().center()

        # 1. Animasyonlu Dış Halka (Ripple Effect)
        if self.is_listening:
            color = QColor(0, 255, 255, int(max(0, self.ripple_opacity))) # Cyan # type: ignore
        else:
            color = QColor(80, 80, 80, int(max(0, self.ripple_opacity))) # Gri (Bekleme modu) # type: ignore

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(color))
        
        painter.drawEllipse(QPointF(center), self.ripple_radius, self.ripple_radius)

        # 2. Sabit İç Daire (Glow Efekti)
        gradient = QRadialGradient(QPointF(center), 50)
        if self.is_listening:
            gradient.setColorAt(0, QColor(0, 200, 255))
            gradient.setColorAt(1, QColor(0, 50, 100))
        else:
            gradient.setColorAt(0, QColor(60, 60, 60))
            gradient.setColorAt(1, QColor(30, 30, 30))

        painter.setBrush(QBrush(gradient))
        # Sabit daire için de QPointF kullanıyoruz
        painter.drawEllipse(QPointF(center), 50, 50)

        # 3. Mikrofon İkonu (Basit çizim veya Unicode)
        painter.setPen(QPen(QColor(255, 255, 255), 3))
        font = QFont("Segoe UI", 24, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "🎙️")

    def toggle_state(self):
        self.is_listening = not self.is_listening
        return self.is_listening

    # DÜZELTME: Widget'a tıklandığında Qt'nin yerleşik mousePressEvent metodunu eziyoruz (override)
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()  # Tıklandığında sinyali fırlat
        super().mousePressEvent(event)


class ModernAtlasWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("A.T.L.A.S.")
        self.resize(450, 700)
        
        # Çerçevesiz Pencere ve Transparanlık
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Ana Widget
        self.central_widget = QWidget()
        self.central_widget.setStyleSheet("""
            QWidget#MainContainer {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0f172a, stop:1 #020617);
                border-radius: 20px;
                border: 1px solid #1e293b;
            }
            QLabel { color: white; }
        """)
        self.central_widget.setObjectName("MainContainer")
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # --- ÜST BAR (Başlık ve Kapat Butonu) ---
        top_bar = QHBoxLayout()
        
        self.title_label = QLabel("A.T.L.A.S. SYSTEM")
        self.title_label.setFont(QFont("Orbitron", 14, QFont.Weight.Bold)) 
        self.title_label.setStyleSheet("color: #00d4ff; letter-spacing: 2px;")
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton { color: white; background: none; border: none; font-size: 16px; }
            QPushButton:hover { color: #ff4d4d; }
        """)
        close_btn.clicked.connect(self.close)

        top_bar.addWidget(self.title_label)
        top_bar.addStretch()
        top_bar.addWidget(close_btn)
        self.layout.addLayout(top_bar)

        # --- ORTA BÖLÜM (Animasyonlu Mikrofon) ---
        self.layout.addStretch()
        
        mic_container = QHBoxLayout()
        mic_container.addStretch()
        self.mic_widget = PulsingMicWidget()
        mic_container.addWidget(self.mic_widget)
        mic_container.addStretch()
        
        self.layout.addLayout(mic_container)
        
        self.status_label = QLabel("Uyandırılmayı bekliyor...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #94a3b8; font-size: 14px; margin-top: 10px;")
        self.layout.addWidget(self.status_label)
        
        self.layout.addStretch()

        # --- ALT BÖLÜM (Terminal Log) ---
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setFixedHeight(150)
        self.log_box.setStyleSheet("""
            QTextEdit {
                background-color: rgba(15, 23, 42, 0.8);
                color: #22c55e;
                border: 1px solid #334155;
                border-radius: 10px;
                font-family: 'Consolas', 'Courier New';
                padding: 10px;
                font-size: 12px;
            }
        """)
        self.add_log("Sistem: Hazır.")
        self.add_log("[BİLGİ] Eko engelleme sistemi aktif.")
        self.add_log("[AĞ] Neural sunuculara bağlanıldı.")
        
        self.layout.addWidget(self.log_box)

        # DÜZELTME: Mikrofona tıklanınca durumu değiştir (Sinyal ile bağlandı)
        self.mic_widget.clicked.connect(self.toggle_listening)

        # Pencere taşıma değişkenleri
        self.old_pos = None

    def add_log(self, text):
        self.log_box.append(f"> {text}")
        self.log_box.verticalScrollBar().setValue(self.log_box.verticalScrollBar().maximum())

    # DÜZELTME: event parametresi kaldırıldı çünkü artık sinyal tarafından tetikleniyor
    def toggle_listening(self):
        state = self.mic_widget.toggle_state()
        if state:
            self.status_label.setText("Dinliyor...")
            self.status_label.setStyleSheet("color: #00d4ff; font-weight: bold;")
            self.add_log("Kullanıcı dinleniyor...")
        else:
            self.status_label.setText("İşleniyor...")
            self.status_label.setStyleSheet("color: #94a3b8;")
            self.add_log("Ses girişi durduruldu.")

    # --- PENCERE TAŞIMA LOGİĞİ ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernAtlasWindow()
    window.show()
    sys.exit(app.exec())