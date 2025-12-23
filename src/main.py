import sys
import os
import webbrowser
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFileDialog, QMessageBox, 
                             QGraphicsOpacityEffect, QStackedWidget, QFrame, 
                             QGridLayout, QScrollArea, QDialog, QHBoxLayout, 
                             QGraphicsDropShadowEffect)
from PyQt6.QtCore import (Qt, QPropertyAnimation, QEasingCurve, QTimer, QPoint, 
                          QThread, pyqtSignal, QRectF)
from PyQt6.QtGui import QFont, QCursor, QColor, QPainter, QPen, QLinearGradient

# --- Your Project Imports ---
try:
    from cv_extraction import extract_cv_data
    from wuzzuf_scraper import scrape_jobs
    from search_space import JobSearchSpace
    from search_algorithms import hill_climbing, simulated_annealing, local_beam_search, tabu_search
    from job import Job
except ImportError:
    # Dummy Job class for UI testing if files are missing
    class Job:
        def __init__(self, title, company, city, country, link, salary, type, exp, level, skills, reqs):
            self.title = title
            self.company = company
            self.city = city
            self.country = country
            self.link = link
            self.salary = salary
            self.job_type = type
            self.experience_needed = exp
            self.career_level = level
            self.skills = skills
            self.requirements = reqs
    print("Warning: Backend modules not found. Running in UI Test Mode.")

# --- GLOBAL STYLES ---
STYLESHEET = """
    QWidget {
        background-color: #0b0e14;
        font-family: 'Segoe UI', 'Roboto', sans-serif;
    }
    QLineEdit {
        background-color: #151923;
        border: 2px solid #2d3436;
        border-radius: 12px;
        color: #00f3ff;
        padding: 15px;
        font-size: 14px;
        selection-background-color: #bc13fe;
    }
    QLineEdit:focus {
        border: 2px solid #00f3ff;
    }
    QScrollBar:vertical {
        border: none;
        background: #0b0e14;
        width: 8px;
        margin: 0px 0px 0px 0px;
    }
    QScrollBar::handle:vertical {
        background: #2d3436;
        min-height: 20px;
        border-radius: 4px;
    }
    QScrollBar::handle:vertical:hover {
        background: #00f3ff;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
"""

# --- CUSTOM WIDGETS ---

class NeonButton(QPushButton):
    """A Futuristic Button with Gradient and Hover Animation"""
    def __init__(self, text, color1="#00f3ff", color2="#bc13fe", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(55)
        self.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        
        # Base Style
        self.default_style = f"""
            QPushButton {{
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {color1}, stop:1 {color2});
                color: white;
                border-radius: 15px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {color2}, stop:1 {color1});
            }}
            QPushButton:pressed {{
                background-color: {color2};
            }}
        """
        self.setStyleSheet(self.default_style)
        
        # Shadow Effect
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(20)
        self.shadow.setColor(QColor(color1))
        self.shadow.setOffset(0, 0)
        self.setGraphicsEffect(self.shadow)

class LoadingSpinner(QWidget):
    """A Custom Painted Rotating Arc Spinner"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(100, 100)
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.timer.start(16)

    def rotate(self):
        if self.isVisible():
            self.angle = (self.angle + 5) % 360
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(10, 10, 80, 80)
        
        # Draw outer arc (Neon Cyan)
        pen = QPen(QColor("#00f3ff"))
        pen.setWidth(6)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawArc(rect, -self.angle * 16, 260 * 16)
        
        # Draw inner pulse (Neon Purple)
        pen.setColor(QColor("#bc13fe"))
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawArc(QRectF(25, 25, 50, 50), self.angle * 16, 200 * 16)

# --- 1. Background Worker ---
class JobSearchWorker(QThread):
    finished = pyqtSignal(list)

    def __init__(self, job_title, cv_path):
        super().__init__()
        self.job_title = job_title
        self.cv_path = cv_path

    def run(self):
        # Your specific backend logic
        scrapped_list = scrape_jobs(self.job_title, 2)
        extracted_cv = extract_cv_data(self.cv_path)
        search_space = JobSearchSpace(scrapped_list, extracted_cv)

        # Run all algorithms
        results = []
        results.extend(hill_climbing(search_space))
        results.extend(simulated_annealing(search_space))
        results.extend(local_beam_search(search_space))
        results.extend(tabu_search(search_space))

        # Filter unique results and return top 4
        unique_jobs = list({job.link: job for job in results if job.link != "N/A"}.values())
        self.finished.emit(unique_jobs[:4])

# --- 2. Detail Dialog ---
class JobDetailDialog(QDialog):
    def __init__(self, job: Job, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Job details")
        self.setFixedSize(450, 550)
        self.setStyleSheet("""
            QDialog { background-color: #0b0e14; border: 2px solid #bc13fe; border-radius: 10px; }
            QLabel { color: #ecf0f1; }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Details Header
        title = QLabel(job.title)
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #00f3ff;")
        title.setWordWrap(True)
        
        company = QLabel(f"🏢 {job.company} | 📍 {job.city}, {job.country}")
        company.setStyleSheet("color: #bc13fe; font-size: 14px; font-weight: bold;")

        # Scrollable Info
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        
        details_text = f"""
        <style>b {{ color: #00f3ff; }}</style>
        <p style="line-height: 1.6; font-size: 14px;">
        <b>Type:</b> {job.job_type}<br>
        <b>Salary:</b> {job.salary}<br>
        <b>Experience:</b> {job.experience_needed} years<br>
        <b>Level:</b> {job.career_level}<br><br>
        <b>Skills Detected:</b><br>{", ".join(job.skills) if job.skills else "Not specified"}<br><br>
        <b>System Requirements:</b><br>{job.requirements}
        </p>
        """
        body = QLabel(details_text)
        body.setWordWrap(True)
        body.setTextFormat(Qt.TextFormat.RichText)
        info_layout.addWidget(body)
        scroll.setWidget(info_widget)

        # Apply Button
        apply_btn = NeonButton("APPLY NOW", "#bc13fe", "#00f3ff")
        apply_btn.clicked.connect(lambda: webbrowser.open(job.link))

        layout.addWidget(title)
        layout.addWidget(company)
        layout.addWidget(scroll)
        layout.addWidget(apply_btn)

# --- 3. Main Application ---
class CareerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.cv_path = ""
        self.initUI()

    def initUI(self):
        self.setWindowTitle("AI Powered Job Finder")
        self.setFixedSize(500, 750)
        
        # Apply Global Styles
        self.setStyleSheet(STYLESHEET)
        
        # Main Stacked Layout
        self.stack = QStackedWidget(self)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.stack)
        self.main_layout.setContentsMargins(0,0,0,0)

        self.setup_input_page()
        self.setup_loading_page()
        self.setup_results_page()

    def setup_input_page(self):
        self.input_page = QWidget()
        layout = QVBoxLayout(self.input_page)
        layout.setContentsMargins(40, 60, 40, 60)
        layout.setSpacing(20)

        # Logo / Title
        title_top = QLabel("AI POWERED")
        title_top.setFont(QFont("Segoe UI", 14, QFont.Weight.Light))
        title_top.setStyleSheet("color: #bc13fe; letter-spacing: 5px;")
        
        title_main = QLabel("JOB\nFINDER")
        title_main.setFont(QFont("Segoe UI", 42, QFont.Weight.Bold))
        title_main.setStyleSheet("color: white; line-height: 0.9;")
        
        # Inputs
        input_container = QWidget()
        input_container.setStyleSheet("background: rgba(255,255,255,0.03); border-radius: 20px;")
        ic_layout = QVBoxLayout(input_container)
        ic_layout.setContentsMargins(20,30,20,30)
        
        self.job_input = QLineEdit()
        self.job_input.setPlaceholderText("Enter your Desired Job Title")
        
        self.upload_btn = QPushButton("📎 UPLOAD CV")
        self.upload_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 2px dashed #636e72;
                color: #b2bec3;
                border-radius: 12px;
                padding: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                border: 2px dashed #00f3ff;
                color: #00f3ff;
                background: rgba(0, 243, 255, 0.05);
            }
        """)
        self.upload_btn.clicked.connect(self.open_file_dialog)

        ic_layout.addWidget(self.job_input)
        ic_layout.addWidget(self.upload_btn)

        # Action Button
        self.submit_btn = NeonButton("FIND BEST JOBS")
        self.submit_btn.clicked.connect(self.submit_data)

        layout.addWidget(title_top)
        layout.addWidget(title_main)
        layout.addSpacing(20)
        layout.addWidget(input_container)
        layout.addStretch()
        layout.addWidget(self.submit_btn)
        
        self.stack.addWidget(self.input_page)

    def setup_loading_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(30)
        
        spinner = LoadingSpinner()
        
        self.load_text = QLabel("ANALYZING YOUR CV...")
        self.load_text.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.load_text.setStyleSheet("color: #00f3ff; letter-spacing: 2px;")
        self.load_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        sub = QLabel("RUNNING SEARCH ALGORITHMS...")
        sub.setFont(QFont("Segoe UI", 10))
        sub.setStyleSheet("color: #636e72;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()
        layout_center = QHBoxLayout()
        layout_center.addStretch()
        layout_center.addWidget(spinner)
        layout_center.addStretch()
        layout.addLayout(layout_center)
        
        layout.addWidget(self.load_text)
        layout.addWidget(sub)
        layout.addStretch()
        self.stack.addWidget(page)

    def setup_results_page(self):
        self.results_page = QWidget()
        self.res_layout = QVBoxLayout(self.results_page)
        self.res_layout.setContentsMargins(30, 50, 30, 30)
        
        # Header
        header_widget = QWidget()
        h_layout = QHBoxLayout(header_widget)
        h_layout.setContentsMargins(0,0,0,0)
        
        title = QLabel("BEST JOB MATCHES")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: white; border-bottom: 3px solid #bc13fe;")
        
        h_layout.addWidget(title)
        h_layout.addStretch()
        
        # Scroll Area for Grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        self.grid_container = QWidget()
        self.grid = QGridLayout(self.grid_container)
        self.grid.setSpacing(20)
        self.grid.setContentsMargins(10,10,10,10)
        
        scroll.setWidget(self.grid_container)
        
        # Back Button
        back_btn = QPushButton("SEARCH AGAIN")
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.setStyleSheet("color: #636e72; background: transparent; border: none; font-weight: bold;")
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        self.res_layout.addWidget(header_widget)
        self.res_layout.addWidget(scroll)
        self.res_layout.addWidget(back_btn)
        
        self.stack.addWidget(self.results_page)

    def open_file_dialog(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Select CV", "", "PDF (*.pdf)")
        if fname:
            self.cv_path = fname
            self.upload_btn.setText(f"✅ {os.path.basename(fname)} ATTACHED")
            self.upload_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(0, 243, 255, 0.1);
                    border: 2px solid #00f3ff;
                    color: #00f3ff;
                    border-radius: 12px;
                    padding: 15px;
                    font-weight: bold;
                }
            """)

    def submit_data(self):
        if not self.job_input.text() or not self.cv_path:
            QMessageBox.warning(self, "Input Error", "Data Incomplete. Please provide Job Title and CV.")
            return
        
        # Switch to Loading Page
        self.stack.setCurrentIndex(1)
        self.load_text.setText("ANALYZING YOUR CV...")
        
        # Initialize and start worker thread
        self.worker = JobSearchWorker(self.job_input.text(), self.cv_path)
        self.worker.finished.connect(self.display_results)
        self.worker.start()

    def display_results(self, results):
        while self.grid.count():
            child = self.grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not results:
            lbl = QLabel("No matches found. Try recalibrating.")
            lbl.setStyleSheet("color: #636e72; font-size: 16px;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid.addWidget(lbl, 0, 0)
        else:
            if not hasattr(self, "animations"):
                self.animations = []

            for i, job in enumerate(results):
                card = self.create_job_card(job)
                card.setVisible(False)
                self.grid.addWidget(card, i // 2, i % 2)

                effect = QGraphicsOpacityEffect(card)
                card.setGraphicsEffect(effect)

                anim = QPropertyAnimation(effect, b"opacity", self)
                anim.setDuration(500)
                anim.setStartValue(0)
                anim.setEndValue(1)

                self.animations.append(anim)

                QTimer.singleShot(
                    i * 150,
                    lambda c=card, a=anim: self.start_card_anim(c, a)
                )

        self.stack.setCurrentIndex(2)


    def start_card_anim(self, card, anim):
        card.setVisible(True)
        anim.start()

    def create_job_card(self, job):
        card = QFrame()
        card.setFixedSize(200, 180)
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setStyleSheet("""
            QFrame { 
                background-color: #151923;
                border: 1px solid #2d3436;
                border-radius: 16px;
            }
            QFrame:hover { 
                background-color: #1a1e29;
                border: 1px solid #00f3ff;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15,15,15,15)

        t = QLabel(job.title)
        t.setWordWrap(True)
        t.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        t.setStyleSheet("color: white; border: none; background: transparent;")
        
        c = QLabel(job.company)
        c.setStyleSheet("color: #bc13fe; font-size: 11px; border: none; background: transparent;")
        
        loc = QLabel(f"{job.city}")
        loc.setStyleSheet("color: #636e72; font-size: 10px; border: none; background: transparent;")
        
        layout.addWidget(t)
        layout.addWidget(c)
        layout.addWidget(loc)
        layout.addStretch()
        
        card.mousePressEvent = lambda e: self.show_details(job)
        
        # Add shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 5)
        card.setGraphicsEffect(shadow)
        
        return card

    def show_details(self, job):
        dialog = JobDetailDialog(job, self)
        dialog.exec()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CareerApp()
    window.show()
    sys.exit(app.exec())