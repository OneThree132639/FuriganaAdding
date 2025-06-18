APP_NAME=FuriganaAdding
SRC_DIR=src
DATA_DIR=data
RESOURCE_DIR=resource
MAIN_SCRIPT=$(SRC_DIR)/main.py
VENV=venv
DIST_DIR=dist
BUILD_DIR=build

ICON_FILE=$(RESOURCE_DIR)/myicon.icns

# Detect OS
UNAME_S:=$(shell uname -s)
ifeq ($(UNAME_S),Darwin)
	OS=MACOS
	PYINSTALLER=$(VENV)/bin/pyinstaller
	ICON_FILE=$(RESOURCE_DIR)/myicon.icns
	SITE_PACKAGES=$(shell $(VENV)/bin/python -c "import site; print(site.getsitepackages()[0])")
	PYQT5_PLUGINS=$(SITE_PACKAGES)/PyQt5/Qt5/plugins
	PYINSTALLER_OPTS+=--windowed --icon=$(ICON_FILE)
	APP_OUTPUT=$(DIST_DIR)/$(APP_NAME).app
else ifeq ($(findstring MINGW,$(UNAME_S)),MINGW)
	OS=WINDOWS
	PYINSTALLER=$(VENV)/Scripts/pyinstaller
	ICON_FILE=$(RESOURCE_DIR)/favicon.ico
	PYQT5_PLUGINS=$(VENV)/Lib/site-packages/PyQt5/Qt/plugins
	PYINSTALLER_OPTS+=--windowed --icon=$(ICON_FILE)
	APP_OUTPUT=$(DIST_DIR)/$(APP_NAME).exe
else
	OS=LINUX
	PYINSTALLER=$(VENV)/bin/pyinstaller
	ICON_FILE=$(RESOURCE_DIR)/icon.png
	SITE_PACKAGES=$(shell $(VENV)/bin/python -c "import site; print(site.getsitepackages()[0])")
	PYQT5_PLUGINS=$(SITE_PACKAGES)/PyQt5/Qt5/plugins
	APP_OUTPUT=$(DIST_DIR)/$(APP_NAME)
endif

PYINSTALLER_OPTS += \
	--name=$(APP_NAME) \
	--paths=$(SRC_DIR) \
	--add-data "$(DATA_DIR):data" \
	--add-data "$(PYQT5_PLUGINS):PyQt5/Qt/plugins" \
	--hidden-import=pandas.core.strings \
	--hidden-import=pandas.core.dtypes.generic \
	--hidden-import=pandas.io.excel._openpyxl \
	--distpath $(DIST_DIR) \
	--workpath $(BUILD_DIR) \

all: build

generate:
	if [ "$(OS)" = "MACOS" ]; then \
		python3 $(RESOURCE_DIR)/generate_icons.py; \
		iconutil -c icns $(RESOURCE_DIR)/myicon.iconset; \
	elif [ "$(OS)" = "WINDOWS" ]; then \
		python3 $(RESOURCE_DIR)/generate_ico.py; \
	fi

venv:
	python3 -m venv venv
	$(VENV)/bin/pip install -r requirements.txt

build:
	$(PYINSTALLER) $(PYINSTALLER_OPTS) $(MAIN_SCRIPT)

run:
	if [ "$(OS)" = "MACOS" ]; then \
		open "$(APP_OUTPUT)"; \
	elif [ "$(OS)" = "WINDOWS" ]; then \
		cmd /c start "" "$(APP_OUTPUT)"; \
	else \
		"./$(APP_OUTPUT)"; \
	fi

clean:
	rm -rf $(DIST_DIR) $(BUILD_DIR) *.log __pycache__ *.pyc .pytest_cache
	rm -f $(APP_NAME).spec
	if [ -d "$(VENV)" ]; then rm -rf $(VENV); fi

.PHONY: all venv build clean run