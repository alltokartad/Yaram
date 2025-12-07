import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QLineEdit, QPushButton, QLabel, QProgressBar, QTabWidget, QListWidget,
    QListWidgetItem, QMessageBox, QComboBox, QFileDialog, QDialog, QCheckBox,
    QAction
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt, QThread, pyqtSignal
import json
import subprocess
from pathlib import Path
import sys
import os
from PyQt5.QtGui import QIcon, QFont, QPixmap
import urllib.parse
from urllib.request import urlretrieve
import threading

__version__ = "1.0.0"


class DownloadThread(QThread):
    """Thread for handling downloads"""
    progress_signal = pyqtSignal(int)
    completed_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self, url, filename):
        super().__init__()
        self.url = url
        self.filename = filename

    def run(self):
        try:
            def progress_hook(blocknum, blocksize, totalsize):
                if totalsize > 0:
                    progress = int((blocknum * blocksize) / totalsize * 100)
                    self.progress_signal.emit(min(progress, 100))

            urlretrieve(self.url, self.filename, reporthook=progress_hook)
            self.completed_signal.emit(f"Downloaded: {os.path.basename(self.filename)}")
        except Exception as e:
            self.error_signal.emit(f"Download failed: {str(e)}")


class WelcomeDialog(QDialog):
    """A small dialog shown to new users offering to run the setup wizard."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Welcome to Yaram')
        self.setModal(True)
        self.setFixedSize(480, 200)

        layout = QVBoxLayout(self)
        msg = QLabel("Welcome to Yaram Browser!\n\nWould you like to run the setup wizard to finish installation and create shortcuts?\nYou can skip and run it later from the menu.")
        msg.setWordWrap(True)
        layout.addWidget(msg)

        self.checkbox = QCheckBox("Don't show this again")
        layout.addWidget(self.checkbox)

        btn_layout = QHBoxLayout()
        run_btn = QPushButton('Run Setup')
        skip_btn = QPushButton('Skip')
        run_btn.clicked.connect(self.accept)
        skip_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(run_btn)
        btn_layout.addWidget(skip_btn)
        layout.addLayout(btn_layout)

    def dont_show_again(self):
        return self.checkbox.isChecked()


class SettingsDialog(QDialog):
    """Settings dialog to change homepage and other preferences."""
    def __init__(self, parent=None, config=None):
        super().__init__(parent)
        self.setWindowTitle('Yaram Settings')
        self.setFixedSize(480, 260)
        self.config = config or {}

        layout = QVBoxLayout(self)

        # Homepage
        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel('Homepage:'))
        self.home_input = QLineEdit(self.config.get('homepage', 'https://www.google.com'))
        h_layout.addWidget(self.home_input)
        layout.addLayout(h_layout)

        # Default search engine selector
        s_layout = QHBoxLayout()
        s_layout.addWidget(QLabel('Default search engine:'))
        self.search_combo = QComboBox()
        self.search_combo.addItems(['Google', 'Bing', 'DuckDuckGo'])
        engine = self.config.get('search_engine', 'Google')
        try:
            idx = ['Google', 'Bing', 'DuckDuckGo'].index(engine)
        except Exception:
            idx = 0
        self.search_combo.setCurrentIndex(idx)
        s_layout.addWidget(self.search_combo)
        layout.addLayout(s_layout)

        # Clear browsing data on exit
        self.clear_on_exit = QCheckBox('Clear browsing history on exit')
        self.clear_on_exit.setChecked(bool(self.config.get('clear_on_exit', False)))
        layout.addWidget(self.clear_on_exit)

        # Auto-open homepage on new tab
        self.auto_open_home = QCheckBox('Auto-open homepage on new tab')
        self.auto_open_home.setChecked(bool(self.config.get('auto_open_homepage', False)))
        layout.addWidget(self.auto_open_home)

        # Auto-overwrite desktop launcher preference
        self.auto_overwrite_launcher = QCheckBox('Auto-overwrite Desktop launcher without prompting')
        self.auto_overwrite_launcher.setChecked(bool(self.config.get('auto_overwrite_launcher', False)))
        layout.addWidget(self.auto_overwrite_launcher)

        # Telemetry (opt-out)
        self.telemetry = QCheckBox('Enable telemetry / usage reporting')
        self.telemetry.setChecked(bool(self.config.get('telemetry', False)))
        layout.addWidget(self.telemetry)

        # Don't show welcome again control
        self.welcome_checkbox = QCheckBox("Don't show welcome on startup")
        self.welcome_checkbox.setChecked(self.config.get('welcome_shown', False))
        layout.addWidget(self.welcome_checkbox)

        # Buttons
        btn_layout = QHBoxLayout()
        ok = QPushButton('OK')
        cancel = QPushButton('Cancel')
        ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(ok)
        btn_layout.addWidget(cancel)
        layout.addLayout(btn_layout)

    def get_values(self):
        return {
            'homepage': self.home_input.text().strip() or 'https://www.google.com',
            'search_engine': self.search_combo.currentText(),
            'clear_on_exit': bool(self.clear_on_exit.isChecked()),
            'auto_open_homepage': bool(self.auto_open_home.isChecked()),
            'auto_overwrite_launcher': bool(self.auto_overwrite_launcher.isChecked()),
            'telemetry': bool(self.telemetry.isChecked()),
            'welcome_shown': bool(self.welcome_checkbox.isChecked())
        }


class HistoryDialog(QDialog):
    """Show browsing history and allow opening or clearing it."""
    def __init__(self, parent=None, history=None):
        super().__init__(parent)
        self.setWindowTitle('Browsing History')
        self.setFixedSize(600, 400)
        self.history = history or []

        layout = QVBoxLayout(self)
        self.listw = QListWidget()
        for u in reversed(self.history):
            self.listw.addItem(u)
        layout.addWidget(self.listw)

        btn_layout = QHBoxLayout()
        open_btn = QPushButton('Open')
        clear_btn = QPushButton('Clear History')
        close_btn = QPushButton('Close')
        open_btn.clicked.connect(self.open_selected)
        clear_btn.clicked.connect(self.clear_history)
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(open_btn)
        btn_layout.addWidget(clear_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def open_selected(self):
        item = self.listw.currentItem()
        if not item:
            QMessageBox.information(self, 'Open', 'Select an entry to open.')
            return
        url = item.text()
        # tell the parent to load it
        try:
            self.parent().load_url(url)
        except Exception:
            pass
        self.close()

    def clear_history(self):
        if QMessageBox.question(self, 'Clear History', 'Are you sure you want to clear browsing history?',
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            self.listw.clear()
            # inform parent to clear
            try:
                self.parent().history = []
                cfg = self.parent()._read_config()
                cfg['history'] = []
                self.parent()._write_config(cfg)
            except Exception:
                pass


class ReportBugDialog(QDialog):
    """Collect bug report details and open user's email client to send the report; also save locally."""
    def __init__(self, parent=None, recipient='aronkardos600@gmail.com'):
        super().__init__(parent)
        self.setWindowTitle('Report a Bug')
        self.setFixedSize(520, 360)
        self.recipient = recipient

        layout = QVBoxLayout(self)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('Full name')
        layout.addWidget(QLabel('Full name:'))
        layout.addWidget(self.name_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText('Your email')
        layout.addWidget(QLabel('Email:'))
        layout.addWidget(self.email_input)

        self.report_input = QTextEdit()
        self.report_input.setPlaceholderText('Describe the bug and steps to reproduce...')
        layout.addWidget(QLabel('Report:'))
        layout.addWidget(self.report_input, 1)

        btn_layout = QHBoxLayout()
        send_btn = QPushButton('Send')
        cancel_btn = QPushButton('Cancel')
        send_btn.clicked.connect(self.send_report)
        cancel_btn.clicked.connect(self.close)
        btn_layout.addStretch()
        btn_layout.addWidget(send_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def send_report(self):
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        report = self.report_input.toPlainText().strip()
        if not report:
            QMessageBox.warning(self, 'Report', 'Please enter the bug description before sending.')
            return

        # Build mailto link
        import urllib.parse, webbrowser, datetime
        subject = urllib.parse.quote('Yaram Browser Bug Report')
        body_lines = [f'Name: {name}', f'Email: {email}', '', 'Report:', report, '', f'App version: {__version__}']
        try:
            body_lines.append('OS: ' + os.name)
        except Exception:
            pass
        body = urllib.parse.quote('\n'.join(body_lines))
        mailto = f'mailto:{self.recipient}?subject={subject}&body={body}'

        # Open default mail client with prepared message
        try:
            webbrowser.open(mailto)
        except Exception:
            QMessageBox.information(self, 'Send', 'Could not open email client. Copy the report and email it to ' + self.recipient)

        # Append to local bug log
        try:
            log_dir = Path.home() / '.yaram_browser'
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / 'bug_reports.log'
            with open(str(log_file), 'a', encoding='utf-8') as f:
                f.write(f'---\n{datetime.datetime.utcnow().isoformat()}Z\nName: {name}\nEmail: {email}\nReport:\n{report}\n\n')
        except Exception:
            pass

        QMessageBox.information(self, 'Report', 'Report prepared in your email client and logged locally.')
        self.close()



class YaramBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.browser = None
        self.download_thread = None
        self.downloads = []
        self.history = []
        self.current_history_index = -1
        self.init_ui()
        self.setWindowTitle("Yaram Browser")
        self.setGeometry(100, 100, 1200, 800)
        # Check first-run welcome/setup
        try:
            self.check_first_run()
        except Exception:
            # Keep app functional even if welcome logic fails
            pass
        # load config (settings, history)
        try:
            cfg = self._read_config()
            # apply homepage preference if present
            self.config = cfg
            self.history = cfg.get('history', [])
            homepage = cfg.get('homepage')
            if homepage:
                # don't auto-load here; keep initial load but set address
                self.url_input.setText(homepage)
        except Exception:
            self.config = {}

    def init_ui(self):
        """Initialize the user interface"""
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Toolbar widget for fixed sizing
        toolbar_widget = QWidget()
        toolbar_widget.setMinimumHeight(50)
        toolbar_widget.setMaximumHeight(50)
        toolbar_layout = QHBoxLayout(toolbar_widget)
        toolbar_layout.setContentsMargins(5, 5, 5, 5)
        toolbar_layout.setSpacing(5)

        # Back button
        self.back_btn = QPushButton("← Back")
        self.back_btn.clicked.connect(self.go_back)
        self.back_btn.setToolTip("Go back to previous page")
        self.back_btn.setMaximumWidth(90)
        toolbar_layout.addWidget(self.back_btn)

        # Forward button
        self.forward_btn = QPushButton("Forward →")
        self.forward_btn.clicked.connect(self.go_forward)
        self.forward_btn.setToolTip("Go forward to next page")
        self.forward_btn.setMaximumWidth(90)
        toolbar_layout.addWidget(self.forward_btn)

        # Refresh button
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_page)
        self.refresh_btn.setToolTip("Refresh the current page")
        self.refresh_btn.setMaximumWidth(90)
        toolbar_layout.addWidget(self.refresh_btn)

        # Search label
        search_label = QLabel("Search:")
        search_label.setFont(QFont("Arial", 10))
        search_label.setMaximumWidth(50)
        toolbar_layout.addWidget(search_label)

        # URL/Search input field
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter URL or search query...")
        self.url_input.returnPressed.connect(self.navigate)
        self.url_input.setToolTip("Type URL or search term and press Enter")
        toolbar_layout.addWidget(self.url_input)

        # Search button
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.navigate)
        self.search_btn.setToolTip("Search or navigate to URL")
        self.search_btn.setMaximumWidth(70)
        toolbar_layout.addWidget(self.search_btn)

        # Download button
        self.download_btn = QPushButton("⬇️ Downloads")
        self.download_btn.clicked.connect(self.show_downloads)
        self.download_btn.setToolTip("Manage downloads")
        self.download_btn.setMaximumWidth(110)
        toolbar_layout.addWidget(self.download_btn)

        # Version label
        version_label = QLabel(f"v{__version__}")
        version_label.setFont(QFont("Arial", 8))
        version_label.setStyleSheet("color: gray; margin-right: 10px;")
        version_label.setMaximumWidth(40)
        toolbar_layout.addWidget(version_label)

        main_layout.addWidget(toolbar_widget)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumHeight(3)
        main_layout.addWidget(self.progress_bar)

        # Web engine view
        self.browser = QWebEngineView()
        self.browser.load(QUrl("https://www.google.com"))
        # Disable zoom with Ctrl+Wheel
        self.browser.wheelEvent = self.disable_zoom_wheel
        main_layout.addWidget(self.browser, 1)

        # Status bar
        self.statusBar().showMessage("Ready | Yaram Browser")

        # ===== MENU: Help -> Run Setup Wizard =====
        try:
            menubar = self.menuBar()
            help_menu = menubar.addMenu('Help')

            run_setup_action = QAction('Run Setup Wizard...', self)
            run_setup_action.setToolTip('Re-run the setup wizard')
            run_setup_action.setShortcut('Ctrl+Shift+S')

            def run_setup():
                try:
                    project_dir = os.path.dirname(os.path.abspath(__file__))
                    script_path = os.path.join(project_dir, 'setup_wizard.py')
                    if sys.platform.startswith('win'):
                        try:
                            creationflags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
                        except Exception:
                            creationflags = subprocess.CREATE_NEW_CONSOLE
                        subprocess.Popen(['py', script_path], cwd=project_dir, creationflags=creationflags)
                    else:
                        subprocess.Popen(['py', script_path], cwd=project_dir)
                    QMessageBox.information(self, 'Setup', 'Setup wizard started.')
                except Exception as e:
                    QMessageBox.warning(self, 'Setup', f'Could not start setup wizard: {e}')

            run_setup_action.triggered.connect(run_setup)
            help_menu.addAction(run_setup_action)
        except Exception:
            # Non-critical; ignore if menus are unavailable
            pass
        try:
            report_action = QAction('Report a Bug...', self)
            def run_report():
                try:
                    dlg = ReportBugDialog(self, recipient='aronkardos600@gmail.com')
                    dlg.exec_()
                except Exception as e:
                    QMessageBox.warning(self, 'Report', f'Could not open report dialog: {e}')
            report_action.triggered.connect(run_report)
            help_menu.addAction(report_action)
        except Exception:
            pass
        # Add Settings and History menus
        try:
            settings_menu = menubar.addMenu('Settings')
            settings_action = QAction('Settings...', self)
            def open_settings():
                try:
                    cfg = self._read_config()
                except Exception:
                    cfg = {}
                dlg = SettingsDialog(self, config=cfg)
                if dlg.exec_() == QDialog.Accepted:
                    vals = dlg.get_values()
                    cfg.update(vals)
                    # persist
                    try:
                        self._write_config(cfg)
                        self.config = cfg
                    except Exception:
                        pass
                    # apply theme (simple)
                    if cfg.get('theme') == 'Dark':
                        self.apply_dark_theme()
                    else:
                        self.apply_stylesheet()
            settings_action.triggered.connect(open_settings)
            settings_menu.addAction(settings_action)

            history_menu = menubar.addMenu('History')
            history_action = QAction('Show History', self)
            def open_history():
                try:
                    cfg = self._read_config()
                    hist = cfg.get('history', self.history)
                except Exception:
                    hist = self.history
                dlg = HistoryDialog(self, history=hist)
                dlg.exec_()
            history_action.triggered.connect(open_history)
            history_menu.addAction(history_action)
        except Exception:
            pass

        main_widget.setLayout(main_layout)

    def disable_zoom_wheel(self, event):
        """Disable zoom on mouse wheel"""
        if event.modifiers() == Qt.ControlModifier:
            event.ignore()
        else:
            QWebEngineView.wheelEvent(self.browser, event)

    def navigate(self):
        """Navigate to URL or search"""
        query = self.url_input.text().strip()

        if not query:
            return

        # Check if it's a URL
        if query.startswith("http://") or query.startswith("https://"):
            url = query
        elif "." in query and " " not in query:
            # Likely a domain
            url = f"https://{query}"
        else:
            # Treat as search query
            url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"

        self.load_url(url)

    def load_url(self, url):
        """Load URL and update history"""
        self.browser.load(QUrl(url))
        # Update history (in-memory and persisted)
        self.update_history(url)
        try:
            cfg = self._read_config()
            cfg['history'] = self.history[-200:]
            self._write_config(cfg)
        except Exception:
            pass
        self.statusBar().showMessage(f"Loading: {url}")

    def update_history(self, url):
        """Update navigation history"""
        # Remove forward history if we're not at the end
        if self.current_history_index < len(self.history) - 1:
            self.history = self.history[:self.current_history_index + 1]

        self.history.append(url)
        self.current_history_index += 1
        self.update_navigation_buttons()

    def go_back(self):
        """Go back in history"""
        if self.current_history_index > 0:
            self.current_history_index -= 1
            url = self.history[self.current_history_index]
            self.browser.load(QUrl(url))
            self.update_navigation_buttons()
            self.statusBar().showMessage(f"Back: {url}")

    def go_forward(self):
        """Go forward in history"""
        if self.current_history_index < len(self.history) - 1:
            self.current_history_index += 1
            url = self.history[self.current_history_index]
            self.browser.load(QUrl(url))
            self.update_navigation_buttons()
            self.statusBar().showMessage(f"Forward: {url}")

    def refresh_page(self):
        """Refresh the current page"""
        self.browser.reload()
        self.statusBar().showMessage("Refreshing page...")

    def update_navigation_buttons(self):
        """Enable/disable navigation buttons"""
        self.back_btn.setEnabled(self.current_history_index > 0)
        self.forward_btn.setEnabled(self.current_history_index < len(self.history) - 1)

    def show_downloads(self):
        """Show downloads dialog"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Downloads")
        msg.setIcon(QMessageBox.Information)

        if not self.downloads:
            msg.setText("No downloads yet.\n\nTo download files, right-click on links and select 'Save Link As'")
        else:
            download_text = "Downloads:\n\n" + "\n".join(self.downloads)
            msg.setText(download_text)

        msg.exec_()

    # ----- First run / welcome logic -----
    def _config_path(self):
        cfg_dir = Path.home() / '.yaram_browser'
        cfg_dir.mkdir(parents=True, exist_ok=True)
        return cfg_dir / 'config.json'

    def _read_config(self):
        p = self._config_path()
        if not p.exists():
            return {}
        try:
            return json.loads(p.read_text(encoding='utf-8'))
        except Exception:
            return {}

    def _write_config(self, data):
        p = self._config_path()
        p.write_text(json.dumps(data), encoding='utf-8')

    def check_first_run(self):
        cfg = self._read_config()
        if cfg.get('welcome_shown'):
            return

        dlg = WelcomeDialog(self)
        res = dlg.exec_()
        dont_show = dlg.dont_show_again()
        if res == QDialog.Accepted:
            # Run the setup wizard (external script) in a detached background process
            try:
                project_dir = os.path.dirname(os.path.abspath(__file__))
                script_path = os.path.join(project_dir, 'setup_wizard.py')
                if sys.platform.startswith('win'):
                    # Use detached process flags so the wizard doesn't keep handles that interfere
                    creationflags = 0
                    try:
                        creationflags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
                    except Exception:
                        # Some Python builds/platforms may not expose DETACHED_PROCESS; fall back
                        creationflags = subprocess.CREATE_NEW_CONSOLE
                    subprocess.Popen(['py', script_path], cwd=project_dir, creationflags=creationflags)
                else:
                    # On POSIX, start the process normally (it will be independent)
                    subprocess.Popen(['py', script_path], cwd=project_dir)
            except Exception as e:
                # Don't block the main UI if launching fails
                try:
                    QMessageBox.warning(self, 'Setup', f'Could not start setup wizard: {e}')
                except Exception:
                    pass

        if dont_show:
            cfg['welcome_shown'] = True
            self._write_config(cfg)

    def download_file(self, url, filename=None):
        """Download a file"""
        if not filename:
            filename = url.split("/")[-1] or "download"

        # Ask user for save location
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            filename,
            "All Files (*)"
        )

        if save_path:
            self.download_thread = DownloadThread(url, save_path)
            self.download_thread.progress_signal.connect(self.update_progress)
            self.download_thread.completed_signal.connect(self.download_completed)
            self.download_thread.error_signal.connect(self.download_error)
            self.download_thread.start()
            self.progress_bar.setVisible(True)

    def update_progress(self, progress):
        """Update download progress"""
        self.progress_bar.setValue(progress)

    def download_completed(self, message):
        """Handle download completion"""
        self.downloads.append(message)
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage(message)
        QMessageBox.information(self, "Download Complete", message)

    def download_error(self, error_msg):
        """Handle download error"""
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage(f"Error: {error_msg}")
        QMessageBox.critical(self, "Download Error", error_msg)


def main():
    app = QApplication(sys.argv)
    browser = YaramBrowser()
    browser.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
