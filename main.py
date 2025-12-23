import sys
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFileDialog, QMessageBox, 
                             QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QPoint
from PyQt6.QtGui import QFont, QColor

class AnimatedWelcomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.cv_path = ""
        self.initUI()
        
        # Trigger the entrance animations after a tiny delay
        QTimer.singleShot(100, self.start_entrance_animations)

    def initUI(self):
        self.setWindowTitle("Career Portal")
        self.setFixedSize(500, 650)
        
        # 1. Background Style (Dark Modern Gradient)
        self.setObjectName("MainWindow")
        self.setStyleSheet("""
            #MainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                                          stop:0 #0f0c29, stop:0.5 #302b63, stop:1 #24243e);
            }
            QLabel { color: white; }
        """)

        # Main Layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(60, 80, 60, 80)
        self.layout.setSpacing(10)

        # --- Creating Widgets ---
        
        # 2. Welcome Title
        self.welcome_label = QLabel("Welcome.")
        self.welcome_label.setFont(QFont("Inter", 38, QFont.Weight.Bold))
        self.welcome_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.sub_label = QLabel("Your future starts here.")
        self.sub_label.setFont(QFont("Inter", 14))
        self.sub_label.setStyleSheet("color: #a29bfe; margin-bottom: 30px;")

        # 3. Input Section
        self.job_title = QLabel("WHAT IS YOUR DREAM JOB?")
        self.job_title.setStyleSheet("font-size: 10px; font-weight: bold; color: #636e72; letter-spacing: 1px;")
        
        self.job_input = QLineEdit()
        self.job_input.setPlaceholderText("Enter job title...")
        self.job_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 15px;
                color: white;
                font-size: 16px;
            }
            QLineEdit:focus {
                border: 1px solid #6c5ce7;
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)

        # 4. Upload Section
        self.upload_btn = QPushButton("📎 ATTACH CV")
        self.upload_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 2px solid #6c5ce7;
                color: #a29bfe;
                border-radius: 8px;
                padding: 12px;
                font-weight: bold;
                margin-top: 20px;
            }
            QPushButton:hover {
                background-color: rgba(108, 92, 231, 0.1);
            }
        """)
        self.upload_btn.clicked.connect(self.open_file_dialog)

        self.file_status = QLabel("No file selected")
        self.file_status.setStyleSheet("color: #636e72; font-size: 11px;")
        self.file_status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 5. Submit Button
        self.submit_btn = QPushButton("SEND APPLICATION")
        self.submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c5ce7;
                color: white;
                border-radius: 8px;
                padding: 18px;
                font-size: 13px;
                font-weight: bold;
                margin-top: 30px;
            }
            QPushButton:hover { background-color: #5b4cc4; }
        """)
        self.submit_btn.clicked.connect(self.submit_data)

        # Adding widgets to layout
        self.widgets = [
            self.welcome_label, self.sub_label, 
            self.job_title, self.job_input, 
            self.upload_btn, self.file_status, 
            self.submit_btn
        ]

        for w in self.widgets:
            self.layout.addWidget(w)
            # Set initial opacity to 0 for all widgets
            op = QGraphicsOpacityEffect(w)
            op.setOpacity(0)
            w.setGraphicsEffect(op)

        self.layout.addStretch()

    def start_entrance_animations(self):
        """Staggered fade-in and slide-up animation for all widgets"""
        self.anim_group = []
        
        for i, widget in enumerate(self.widgets):
            # 1. Opacity Animation
            opacity_effect = widget.graphicsEffect()
            anim = QPropertyAnimation(opacity_effect, b"opacity")
            anim.setDuration(800)
            anim.setStartValue(0)
            anim.setEndValue(1)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            
            # Start animations with a delay for each widget (staggered)
            QTimer.singleShot(i * 150, anim.start)
            self.anim_group.append(anim) # Keep reference

            # 2. Subtle Slide Up
            pos_anim = QPropertyAnimation(widget, b"pos")
            pos_anim.setDuration(800)
            current_pos = widget.pos()
            pos_anim.setStartValue(QPoint(current_pos.x(), current_pos.y() + 20))
            pos_anim.setEndValue(current_pos)
            pos_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            
            QTimer.singleShot(i * 150, pos_anim.start)
            self.anim_group.append(pos_anim)

    def open_file_dialog(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Select CV", "", "PDF (*.pdf);;Word (*.docx)")
        if fname:
            self.cv_path = fname
            self.file_status.setText(f"SELECTED: {fname.split('/')[-1]}")
            self.file_status.setStyleSheet("color: #00b894; font-weight: bold;")

    def submit_data(self):
        if not self.job_input.text() or not self.cv_path:
            QMessageBox.critical(self, "Error", "Please fill in all fields.")
            return
        QMessageBox.information(self, "Done", "Information Received.")

if __name__ == '__main__':
    # WSL Compatibility
    os.environ["QT_QPA_PLATFORM"] = "xcb"
    
    app = QApplication(sys.argv)
    window = AnimatedWelcomePage()
    window.show()
    sys.exit(app.exec())