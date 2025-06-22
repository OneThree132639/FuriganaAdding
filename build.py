import subprocess
import sys
import shutil
import os
import glob
import platform

APP_NAME = "FuriganaAdding"
SRC_DIR = "src"
DATA_DIR = "data"
RESOURCE_DIR = "resource"
MAIN_SCRIPT = "{}/main.py".format(SRC_DIR)
VENV_DIR = "venv"
DIST_DIR = "dist"
BUILD_DIR = "build"

OS = platform.system()
if OS=="Darwin":
	OS_TYPE = "MACOS"
elif OS.startswith("MINGW") or OS=="Windows":
	OS_TYPE = "WINDOWS"
else:
	OS_TYPE = "LINUX"

if OS_TYPE=="MACOS":
	ICON_FILE = os.path.join(RESOURCE_DIR, "myicon.icns")
elif OS_TYPE=="WINDOWS":
	ICON_FILE = os.path.join(RESOURCE_DIR, "favicon.ico")
else:
	ICON_FILE = os.path.join(RESOURCE_DIR, "icon.png")

PYINSTALLER_OPTS = [
	"--name", APP_NAME,
	"--paths", SRC_DIR,
	"--add-data", "{}{}data".format(DATA_DIR, os.pathsep),
	"--hidden-import=pandas.core.strings",
	"--hidden-import=pandas.core.dtypes.generic",
	"--hidden-import=pandas.io.excel._openpyxl",
]

VENV_SITE_PACKAGES = None

def get_venv_site_packages():
	global VENV_SITE_PACKAGES
	if VENV_SITE_PACKAGES is not None:
		return VENV_SITE_PACKAGES
	
	if OS_TYPE=="WINDOWS":
		VENV_SITE_PACKAGES = os.path.join(VENV_DIR, "Lib", "site-packages")
	else:
		venv_python = os.path.join(VENV_DIR, "bin", "python")
		cmd = [
			venv_python,
			"-c",
			"import site; print(site.getsitepackages()[0])"
		]
		result = subprocess.run(cmd, capture_output=True, text=True, check=True)
		VENV_SITE_PACKAGES = result.stdout.strip()

	return VENV_SITE_PACKAGES

def run(cmd):
	print("Running: {}".format(" ".join(cmd)))
	subprocess.run(cmd, check=True)

def detect_pyinstaller():
	if OS_TYPE=="WINDOWS":
		return os.path.join(VENV_DIR, "Scripts", "pyinstaller.exe")
	else:
		return os.path.join(VENV_DIR, "bin", "pyinstaller")
	
def detect_pyqt5_plugins():
	site_packages = get_venv_site_packages()
	return os.path.join(site_packages, "PyQt5", "Qt5", "plugins")

def detect_python():
	if OS_TYPE=="WINDOWS":
		return os.path.join(VENV_DIR, "Scripts", "python.exe")
	else:
		return os.path.join(VENV_DIR, "bin", "python")
	
def generate():
	print("Generating icons...")
	python = detect_python()
	if OS_TYPE=="MACOS":
		run([python, os.path.join(RESOURCE_DIR, "generate_icons.py")])
		run(["iconutil", "-c", "icns", os.path.join(RESOURCE_DIR, "myicon.iconset")])
	elif OS_TYPE=="WINDOWS":
		run([python, os.path.join(RESOURCE_DIR, "generate_ico.py")])

def venv():
	print("Creating virtual environment...")
	run([sys.executable, "-m", "venv", VENV_DIR])
	pip_path = os.path.join(VENV_DIR, "Scripts" if OS_TYPE=="WINDOWS" else "bin",
						 "pip.exe" if OS_TYPE=="WINDOWS" else "pip")
	run([pip_path, "install", "-r", "requirements.txt"])

def build():
	print("Building application with Pyinstaller...")

	pyqt5_plugins = detect_pyqt5_plugins()
	PYINSTALLER_OPTS.extend([
		"--add-data", "{}{}PyQt5/Qt/plugins".format(pyqt5_plugins, os.pathsep)
	])

	if OS_TYPE in ["MACOS", "WINDOWS"]:
		PYINSTALLER_OPTS.append("--windowed")
	PYINSTALLER_OPTS.extend(["--icon", ICON_FILE])

	PYINSTALLER_OPTS.extend([
		"--distpath", DIST_DIR,
		"--workpath", BUILD_DIR,
		MAIN_SCRIPT
	])

	pyinstaller_exec = detect_pyinstaller()
	run([pyinstaller_exec]+PYINSTALLER_OPTS)

def run_app():
	output_file = None
	if OS_TYPE=="MACOS":
		output_file = os.path.join(DIST_DIR, "{}.app".format(APP_NAME))
		run(["open", output_file])
	elif OS_TYPE=="WINDOWS":
		output_file = os.path.join(DIST_DIR, "{}.exe".format(APP_NAME))
		os.startfile(output_file)
	else:
		output_file = os.path.join(DIST_DIR, APP_NAME)
		run([output_file])

def clean():
	print("Cleaning up...")
	for path in [DIST_DIR, BUILD_DIR, "*.log", "__pycache__", "*.pyc",
			  ".pytest_cache", "{}.spec".format(APP_NAME)]:
		for match in glob.glob(path):
			if os.path.isdir(match):
				shutil.rmtree(match, ignore_errors=True)
			elif os.path.isfile(match):
				os.remove(match)
	
	if os.path.exists(VENV_DIR):
		shutil.rmtree(VENV_DIR, ignore_errors=True)

def help():
	print("""
Available commands:
    generate      Generate icons (requires Pillow and iconutil or PIL scripts)
    venv          Create virtual environment and install dependencies
    build         Build the app using PyInstaller
    run           Run the built app
    clean         Clean all build artifacts and venv
""")
	
if __name__ == "__main__":
	args = sys.argv[1:]
	if not args:
		help()
		sys.exit(1)

	command = args[0]
	if command=="generate":
		generate()
	elif command=="venv":
		venv()
	elif command=="build":
		build()
	elif command=="run":
		run_app()
	elif command=="clean":
		clean()
	else:
		print("Unknown command: {}".format(command))
		help()
		sys.exit(1)