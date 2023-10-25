import sys
import os
import subprocess
import psutil
import shutil
from PyQt6.QtCore import Qt, QThread, pyqtSignal

# Installer task for both windows and linux/mac with progress and error handling
class InstallSpicetify(QThread):
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    def run(self):
        try:
            if sys.platform == 'win32':
                self.progress_signal.emit("Downloading Spicetify...")
                subprocess.run('powershell.exe -Command "iwr -useb https://raw.githubusercontent.com/spicetify/spicetify-cli/master/install.ps1 | iex"',check=True)
                self.progress_signal.emit("Cleaning up...")
                subprocess.run('spicetify clear -n -q',check=True)
                self.progress_signal.emit("Creating backup...")
                subprocess.run('spicetify backup -n -q',check=True)
                self.progress_signal.emit("Enabling devtools...")
                subprocess.run('spicetify enable-devtools -n -q',check=True)
                self.progress_signal.emit("Applying modification...")
                subprocess.run('spicetify apply -n -q',check=True)
                self.progress_signal.emit("Installing Marketplace...")
                subprocess.run('powershell.exe -Command "iwr -useb https://raw.githubusercontent.com/spicetify/spicetify-marketplace/main/resources/install.ps1 | iex"',check=True)
                self.progress_signal.emit("done")
        except Exception as e:
            print("Error detected!")
            print(e)
            self.progress_signal.emit("fail")

        self.finished_signal.emit()

# Update spicetify task
class UpdateSpicetify(QThread):
    finished_signal = pyqtSignal()
    def run(self):
        print("Update started")
        subprocess.run('spicetify upgrade -q')
        self.finished_signal.emit()

# Apply mods task
class ApplySpicetify(QThread):
    finished_signal = pyqtSignal()
    def run(self):
        print("Apply started")
        subprocess.check_output('spicetify apply -q')
        self.finished_signal.emit()

# Unisnatll spicetify task
class UninstallSpicetify(QThread):
    finished_signal = pyqtSignal()
    def run(self):
        subprocess.run('spicetify restore')
        if sys.platform == 'win32':
            subprocess.run('powershell.exe -Command "rmdir -r -fo $env:APPDATA\spicetify"',check=True)
            subprocess.run('powershell.exe -Command "rmdir -r -fo $env:LOCALAPPDATA\spicetify"',check=True)
        else:
            subprocess.run('rm -rf ~/.spicetify')
            subprocess.run('rm -rf ~/.config/spicetify')
        self.finished_signal.emit()
    
# Custom command task
class CustomCommand(QThread):
    def __init__(self, index):
        super().__init__()
        self.cmnumber = index

    finished_signal = pyqtSignal()
    def run(self):
        commandList = [
        'spicetify --version',
        'spicetify backup',
        'spicetify clear',
        'spicetify apply',
        'spicetify update',
        'spicetify upgrade',
        'spicetify enable-devtools',
        'spicetify restore',
        ]
        try:
            subprocess.run(commandList[self.cmnumber])
        except:
            print("Error while running custom command!")

    
#Checks if spicetify is installed by checking appdata folder
def checkInstalled():
    folder_path = os.path.join(os.path.join( os.path.expanduser('~'), 'AppData','Local'), 'spicetify')
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        return True
    else:
        return False

#Checks if spicetify is applied by checking appdata folder of spotify
def checkApplied():
    folder_path = os.path.join( os.path.expanduser('~'), 'AppData','Roaming/Spotify/Apps/xpui')
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        return True
    else:
        return False
    
#Checks if spicetify is running using a tasksearch
def checkSpotifyRunning():
    for process in psutil.process_iter(attrs=['pid', 'name']):
        if 'Spotify.exe' in process.info['name']:
            return True
    return False

#Try blocking spotify updates by changing permissions (Windows only) 
def blockSpotifyUpdate(active):
    if active:
        try:
            #Check for existance before deleting update path and making it
            if os.path.exists(os.path.join(os.environ['LOCALAPPDATA'], "Spotify", "Update")):
                shutil.rmtree(os.path.join(os.environ['LOCALAPPDATA'], "Spotify", "Update"))
            os.makedirs(os.path.join(os.environ['LOCALAPPDATA'], "Spotify", "Update"))

            subprocess.run(f'cmd /c icacls %localappdata%\\Spotify\\Update /deny %username%:D', shell=True, check=True)
            subprocess.run(f'cmd /c icacls %localappdata%\\Spotify\\Update /deny %username%:R', shell=True, check=True)
            return
        except subprocess.CalledProcessError as e:
            print(f'Error: {e.returncode}. patcher failed.')
            return e.returncode
    else:
        try:
            subprocess.run(f'cmd /c icacls %localappdata%\\Spotify\\Update /reset', shell=True)
            if os.path.exists(os.path.join(os.environ['LOCALAPPDATA'], "Spotify", "Update")):
                shutil.rmtree(os.path.join(os.environ['LOCALAPPDATA'], "Spotify", "Update"))
            return
        except subprocess.CalledProcessError as e:
            print(f'Error: {e.returncode}. patcher failed.')
            return e.returncode

# Checks if spotify updates are blocked !WIP!
def checkUpdateSupression():
    if not os.path.exists(os.path.join(os.environ['LOCALAPPDATA'], "Spotify", "Update")):
        return False
    else:
        return True


