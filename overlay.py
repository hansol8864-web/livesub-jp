from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QLabel, QWidget

CLEAR_AFTER_MS = 8000


class SubtitleOverlay(QWidget):
    _update_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._drag_pos: QPoint | None = None
        self._clear_timer = QTimer(self)
        self._clear_timer.setSingleShot(True)
        self._clear_timer.timeout.connect(self._clear)
        self._setup_ui()
        self._update_signal.connect(self._set_text)

    def _setup_ui(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        screen = QApplication.primaryScreen().availableGeometry()
        w, h = 1100, 110
        x = (screen.width() - w) // 2
        y = screen.height() - h - 50
        self.setGeometry(x, y, w, h)

        self.label = QLabel("● 일본어 영상을 재생하면 자막이 표시됩니다", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setGeometry(0, 0, w, h)
        self.label.setStyleSheet(
            """
            QLabel {
                color: white;
                font-size: 20px;
                font-family: '맑은 고딕';
                font-weight: bold;
                background-color: rgba(0, 0, 0, 175);
                border-radius: 10px;
                padding: 12px 24px;
            }
        """
        )

    # thread-safe: call from any thread
    def update_text(self, text: str):
        self._update_signal.emit(text)

    def _set_text(self, text: str):
        if not text:
            return
        self.label.setText(text)
        self.show()
        self._clear_timer.start(CLEAR_AFTER_MS)

    def _clear(self):
        self.label.setText("")

    # draggable
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def mouseDoubleClickEvent(self, event):
        QApplication.quit()
