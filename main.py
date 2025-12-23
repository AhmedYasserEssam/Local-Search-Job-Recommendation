import sys
import os
import webbrowser
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFileDialog, QMessageBox, 
                             QGraphicsOpacityEffect, QStackedWidget, QFrame, 
                             QGridLayout, QScrollArea, QDialog, QHBoxLayout)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QPoint, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QCursor

# --- Your Project Imports ---
from src.cv_extraction import extract_cv_data
from src.wuzzuf_scraper import scrape_jobs
from src.search_space import JobSearchSpace
from src.search_algorithms import hill_climbing, simulated_annealing, local_beam_search, tabu_search
from src.job import Job

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
        self.setWindowTitle("Job Details")
        self.setFixedSize(450, 500)
        self.setStyleSheet("background-color: #1a1a2e; color: white;")
        
        layout = QVBoxLayout(self)
        
        # Details Header
        title = QLabel(job.title)
        title.setFont(QFont("Inter", 18, QFont.Weight.Bold))
        title.setWordWrap(True)
        
        company = QLabel(f"🏢 {job.company} | 📍 {job.city}, {job.country}")
        company.setStyleSheet("color: #a29bfe; font-size: 14px;")

        # Scrollable Info
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        
        details_text = f"""
        <b>Type:</b> {job.job_type}<br>
        <b>Salary:</b> {job.salary}<br>
        <b>Experience:</b> {job.experience_needed} years<br>
        <b>Career Level:</b> {job.career_level}<br><br>
        <b>Skills:</b><br>{", ".join(job.skills) if job.skills else "Not specified"}<br><br>
        <b>Requirements:</b><br>{job.requirements}
        """
        body = QLabel(details_text)
        body.setWordWrap(True)
        body.setStyleSheet("font-size: 13px; line-height: 1.5;")
        info_layout.addWidget(body)
        scroll.setWidget(info_widget)

        # Apply Button
        apply_btn = QPushButton("APPLY NOW")
        apply_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c5ce7; padding: 15px; 
                border-radius: 10px; font-weight: bold; font-size: 14px;
            }
            QPushButton:hover { background-color: #5b4cc4; }
        """)
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
        self.setWindowTitle("AI Career Portal")
        self.setFixedSize(500, 700)
        
        # Main Stacked Layout
        self.stack = QStackedWidget(self)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.stack)
        self.main_layout.setContentsMargins(0,0,0,0)

        self.setup_input_page()
        self.setup_loading_page()
        self.setup_results_page()

        self.setStyleSheet("background: #0f0c29;")

    def setup_input_page(self):
        self.input_page = QWidget()
        layout = QVBoxLayout(self.input_page)
        layout.setContentsMargins(50, 80, 50, 80)

        title = QLabel("Find your\nnext role.")
        title.setFont(QFont("Inter", 36, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")

        self.job_input = QLineEdit()
        self.job_input.setPlaceholderText("Enter dream job title...")
        self.job_input.setStyleSheet("padding: 15px; border-radius: 8px; background: #1a1a2e; color: white; border: 1px solid #302b63;")

        self.upload_btn = QPushButton("📎 ATTACH CV (PDF)")
        self.upload_btn.setStyleSheet("border: 2px solid #6c5ce7; color: #a29bfe; padding: 12px; border-radius: 8px; font-weight: bold; margin-top: 10px;")
        self.upload_btn.clicked.connect(self.open_file_dialog)

        self.submit_btn = QPushButton("FIND OPPORTUNITIES")
        self.submit_btn.setStyleSheet("background: #6c5ce7; color: white; padding: 18px; border-radius: 8px; font-weight: bold; margin-top: 40px;")
        self.submit_btn.clicked.connect(self.submit_data)

        layout.addWidget(title)
        layout.addSpacing(30)
        layout.addWidget(self.job_input)
        layout.addWidget(self.upload_btn)
        layout.addStretch()
        layout.addWidget(self.submit_btn)
        self.stack.addWidget(self.input_page)

    def setup_loading_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        l1 = QLabel("🔍")
        l1.setFont(QFont("Arial", 50))
        l1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.load_text = QLabel("Analyzing Search Space...")
        self.load_text.setFont(QFont("Inter", 16))
        self.load_text.setStyleSheet("color: white;")
        self.load_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        sub = QLabel("Running Hill Climbing & Tabu Search...")
        sub.setStyleSheet("color: #636e72;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()
        layout.addWidget(l1)
        layout.addWidget(self.load_text)
        layout.addWidget(sub)
        layout.addStretch()
        self.stack.addWidget(page)

    def setup_results_page(self):
        self.results_page = QWidget()
        self.res_layout = QVBoxLayout(self.results_page)
        self.res_layout.setContentsMargins(30, 50, 30, 50)
        
        header = QLabel("Top Picks For You")
        header.setFont(QFont("Inter", 22, QFont.Weight.Bold))
        header.setStyleSheet("color: white; margin-bottom: 20px;")
        
        self.grid = QGridLayout()
        self.grid.setSpacing(15)
        
        self.res_layout.addWidget(header)
        self.res_layout.addLayout(self.grid)
        self.res_layout.addStretch()
        
        back = QPushButton("← New Search")
        back.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        back.setStyleSheet("color: #636e72; background: transparent; border: none;")
        self.res_layout.addWidget(back)
        
        self.stack.addWidget(self.results_page)

    def open_file_dialog(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Select CV", "", "PDF (*.pdf)")
        if fname:
            self.cv_path = fname
            self.upload_btn.setText("✅ CV ATTACHED")

    def submit_data(self):
        if not self.job_input.text() or not self.cv_path:
            QMessageBox.warning(self, "Missing Info", "Please provide a job title and CV.")
            return
        
        self.stack.setCurrentIndex(1)
        self.worker = JobSearchWorker(self.job_input.text(), self.cv_path)
        self.worker.finished.connect(self.display_results)
        self.worker.start()

    def display_results(self, results):
        # Clear existing grid
        while self.grid.count():
            child = self.grid.takeAt(0)
            if child.widget(): child.widget().deleteLater()

        if not results:
            self.grid.addWidget(QLabel("No jobs found matching your criteria."), 0, 0)
        else:
            for i, job in enumerate(results):
                card = QFrame()
                card.setFixedSize(210, 160)
                card.setCursor(Qt.CursorShape.PointingHandCursor)
                card.setStyleSheet("""
                    QFrame { 
                        background: rgba(255, 255, 255, 0.05); 
                        border: 1px solid rgba(255, 255, 255, 0.1); 
                        border-radius: 12px; 
                    }
                    QFrame:hover { background: rgba(108, 92, 231, 0.2); border: 1px solid #6c5ce7; }
                """)
                
                c_layout = QVBoxLayout(card)
                t = QLabel(job.title)
                t.setWordWrap(True)
                t.setFont(QFont("Inter", 11, QFont.Weight.Bold))
                t.setStyleSheet("color: white; border: none; background: transparent;")
                
                c = QLabel(job.company)
                c.setStyleSheet("color: #a29bfe; font-size: 10px; border: none; background: transparent;")
                
                c_layout.addWidget(t)
                c_layout.addWidget(c)
                
                # Make clickable
                card.mousePressEvent = lambda e, j=job: self.show_details(j)
                
                self.grid.addWidget(card, i // 2, i % 2)

        self.stack.setCurrentIndex(2)

    def show_details(self, job):
        dialog = JobDetailDialog(job, self)
        dialog.exec()

if __name__ == '__main__':
    os.environ["QT_QPA_PLATFORM"] = "xcb"
    app = QApplication(sys.argv)
    window = CareerApp()
    window.show()
    sys.exit(app.exec())