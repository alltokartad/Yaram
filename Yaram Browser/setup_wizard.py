import sys
import os
import subprocess
import threading
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QFileDialog, QMessageBox
)
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtCore import Qt

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
REQUIREMENTS = os.path.join(PROJECT_DIR, 'requirements.txt')
RUN_BAT = os.path.join(PROJECT_DIR, 'run.bat')
LAUNCHER_NAME = 'Run Yaram Browser.bat'


def run_cmd(cmd, capture_output=True):
    try:
        completed = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True)
        return completed.returncode, completed.stdout + completed.stderr
    except Exception as e:
        return 1, str(e)


class InstallThread(threading.Thread):
    def __init__(self, output_widget):
        super().__init__()
        self.output_widget = output_widget

    def run(self):
        if not os.path.exists(REQUIREMENTS):
            self.append('requirements.txt not found in project folder.')
            return
        cmd = 'py -m pip install -r "{}"'.format(REQUIREMENTS)
        self.append('Running: ' + cmd)
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in proc.stdout:
            self.append(line.rstrip())
        proc.wait()
        self.append(f'Install finished with exit code {proc.returncode}')

    def append(self, text):
        def do():
            self.output_widget.append(text)
        QApplication.instance().postEvent(self.output_widget, type('e',(object,),{'__call__':do})())


class SetupWizard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Yaram Browser — Setup Wizard')
        self.setFixedSize(640, 420)
        self.init_ui()
        self.check_environment()

    def init_ui(self):
        layout = QVBoxLayout()

        self.status_label = QLabel('Checking environment...')
        layout.addWidget(self.status_label)

        self.info_area = QTextEdit()
        self.info_area.setReadOnly(True)
        layout.addWidget(self.info_area)

        # Option to create/update desktop launcher automatically at finish
        self.desktop_checkbox = QCheckBox('Create/Update Desktop launcher on my Desktop')
        self.desktop_checkbox.setChecked(True)
        layout.addWidget(self.desktop_checkbox)

        # Option to auto-overwrite existing launcher (persisted)
        self.auto_overwrite_checkbox = QCheckBox('Auto-overwrite existing Desktop launcher without prompting')
        self.auto_overwrite_checkbox.setChecked(False)
        layout.addWidget(self.auto_overwrite_checkbox)

        btn_layout = QHBoxLayout()

        self.install_btn = QPushButton('Install dependencies')
        self.install_btn.clicked.connect(self.install_deps)
        btn_layout.addWidget(self.install_btn)

        self.create_runbtn = QPushButton('Create `run.bat`')
        self.create_runbtn.clicked.connect(self.create_run_bat)
        btn_layout.addWidget(self.create_runbtn)

        self.desktop_btn = QPushButton('Create Desktop Launcher')
        self.desktop_btn.clicked.connect(self.create_desktop_launcher)
        btn_layout.addWidget(self.desktop_btn)

        self.open_folder_btn = QPushButton('Open Project Folder')
        self.open_folder_btn.clicked.connect(self.open_project_folder)
        btn_layout.addWidget(self.open_folder_btn)

        layout.addLayout(btn_layout)

        close_layout = QHBoxLayout()
        self.finish_btn = QPushButton('Finish')
        self.finish_btn.clicked.connect(self.finish_setup)
        close_layout.addStretch()
        close_layout.addWidget(self.finish_btn)
        layout.addLayout(close_layout)

        self.setLayout(layout)

    def append(self, text):
        self.info_area.append(text)

    def check_environment(self):
        self.append('Checking Python (`py`) availability...')
        rc, out = run_cmd('py --version')
        if rc == 0:
            self.append('Python found: ' + out.strip())
        else:
            self.append('Python (py) not found. You can install from https://www.python.org/')

        self.append('\nChecking PyQt5 availability...')
        try:
            import PyQt5  # noqa: F401
            self.append('PyQt5 is installed.')
        except Exception as e:
            self.append('PyQt5 not importable: ' + str(e))
            self.append('You may install it via: `py -m pip install PyQt5 PyQtWebEngine`')

        if os.path.exists(REQUIREMENTS):
            self.append('\nrequirements.txt present.')
        else:
            self.append('\nNo requirements.txt found in project folder.')

        self.status_label.setText('Ready')

    def install_deps(self):
        if not os.path.exists(REQUIREMENTS):
            QMessageBox.warning(self, 'Missing file', 'requirements.txt not found in project folder.')
            return
        self.append('\nStarting dependency installation... (this will run pip)')
        thread = InstallThread(self.info_area)
        thread.start()

    def create_run_bat(self):
        content = f'@echo off\ncd /d "{PROJECT_DIR}"\npy yaram_browser.py\n'
        try:
            with open(RUN_BAT, 'w', encoding='utf-8') as f:
                f.write(content)
            self.append(f'Created `{RUN_BAT}`')
            QMessageBox.information(self, 'Created', f'Created `{RUN_BAT}`')
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def create_desktop_launcher(self, auto_overwrite=False):
        desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
        target = os.path.join(desktop, LAUNCHER_NAME)
        content = f'@echo off\ncd /d "{PROJECT_DIR}"\npy yaram_browser.py\n'
        try:
            # If target exists, confirm overwrite unless auto_overwrite is True
            if os.path.exists(target) and not auto_overwrite:
                answer = QMessageBox.question(self, 'Overwrite launcher?',
                                              f'A launcher already exists at:\n{target}\n\nOverwrite it?',
                                              QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if answer != QMessageBox.Yes:
                    self.append('Skipped creating launcher (user cancelled overwrite).')
                    return

            with open(target, 'w', encoding='utf-8') as f:
                f.write(content)
            self.append(f'Created desktop launcher: {target}')
            QMessageBox.information(self, 'Created', f'Created desktop launcher: {target}')
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def finish_setup(self):
        """Final step when user clicks Finish: create desktop launcher if requested."""
        # Persist auto-overwrite preference
        try:
            cfg_dir = os.path.join(os.path.expanduser('~'), '.yaram_browser')
            os.makedirs(cfg_dir, exist_ok=True)
            cfg_file = os.path.join(cfg_dir, 'config.json')
            cfg = {}
            if os.path.exists(cfg_file):
                try:
                    import json
                    with open(cfg_file, 'r', encoding='utf-8') as f:
                        cfg = json.load(f)
                except Exception:
                    cfg = {}
            cfg['auto_overwrite_launcher'] = bool(self.auto_overwrite_checkbox.isChecked())
            try:
                import json
                with open(cfg_file, 'w', encoding='utf-8') as f:
                    json.dump(cfg, f)
            except Exception:
                pass
        except Exception:
            pass

        if self.desktop_checkbox.isChecked():
            # Pass the auto_overwrite preference to create_desktop_launcher
            self.create_desktop_launcher(auto_overwrite=self.auto_overwrite_checkbox.isChecked())
        QMessageBox.information(self, 'Setup', 'Setup finished.')
        self.close()

    def open_project_folder(self):
        try:
            if sys.platform.startswith('win'):
                os.startfile(PROJECT_DIR)
            else:
                subprocess.Popen(['xdg-open', PROJECT_DIR])
        except Exception as e:
            QMessageBox.warning(self, 'Open folder', f'Could not open folder: {e}')


def main():
    app = QApplication(sys.argv)
    w = SetupWizard()
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
