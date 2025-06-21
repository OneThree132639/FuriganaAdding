import os
import sys
import pandas as pd
from PyQt5.QtWidgets import (
	QWidget, QPushButton, QGridLayout,
	QTableView, QLineEdit, QComboBox, QFileDialog
)
from PyQt5.QtGui import (
	QStandardItemModel, QStandardItem
)
from PyQt5.QtCore import Qt
import json

def BlankFunction():
	pass

class SettingJson:
	def __init__(self, appname):
		self.CONFIG_DIR = self.get_config_dir(appname)
		self.CONFIG_FILE = "setting.json"

	def save_settings(self, settings):
		config_file = os.path.join(self.CONFIG_DIR, self.CONFIG_FILE)
		with open(config_file, "w", encoding="utf-8") as f:
			json.dump(settings, f, ensure_ascii=False, indent=4)

	def load_settings(self):
		config_file = os.path.join(self.CONFIG_DIR, self.CONFIG_FILE)
		if os.path.exists(config_file):
			with open(config_file, "r", encoding="utf-8") as f:
				return json.load(f)
		return {}
	
	def get_config_dir(self, appname):
		if sys.platform == "darwin":
			config_dir = os.path.expanduser("~/Library/Application Support/{}".format(appname))
		elif sys.platform == "win32":
			config_dir = os.path.join(os.getenv("APPDATA"), appname)
		else:
			config_dir = os.path.expanduser("~/.{}".format(appname))

		os.makedirs(config_dir, exist_ok=True)
		return config_dir

class DataFrameViewer(QWidget):

	def __init__(self, parent=None):
		super().__init__(parent)
		self.model = QStandardItemModel()
		self.table_view = QTableView()
		self.table_view.setModel(self.model)

		layout = QGridLayout()
		layout.addWidget(self.table_view, 0, 0)
		self.setLayout(layout)

	def load_data(self, df: pd.DataFrame):
		self.model.setRowCount(0)
		self.model.setColumnCount(len(df.columns))
		self.model.setHorizontalHeaderLabels([str(col) for col in df.columns])

		for row in df.itertuples(index=False):
			items = [QStandardItem(str(field)) for field in row]
			self.model.appendRow(items)

class NavigableMixin:

	def __init__(self, row: int, col: int):
		self.row = row
		self.col = col

	def move_to(self, dx: int, dy: int):
		layout = self.parent().layout()
		if layout is None:
			return None
		
		new_row = self.row+dy
		new_col = self.col+dx

		for i in range(layout.count()):
			item = layout.itemAt(i)
			widget = item.widget()
			if (isinstance(widget, (CustomButton, CustomComboBox, CustomLineEdit)) and 
				hasattr(widget, "row") and hasattr(widget, "col")):
				if widget.row==new_row and widget.col==new_col:
					widget.setFocus()
					widget.setCursorToEdge(dx)
					break

	def setCursorToEdge(self, dx: int):
		pass
	
class CustomButton(NavigableMixin, QPushButton):
	def __init__(self, row: int, col: int, text: str="", parent=None):
		QPushButton.__init__(self, text, parent)
		NavigableMixin.__init__(self, row, col)
		self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

		self.defalut_style = self.styleSheet()
		self.focused_style = '''QPushButton {
		border: 0.2px solid white;
		border-radius: 5px;
		padding: 2px;
		background-color: #0060E4;
		color: white;
		}'''
		self.on_click = BlankFunction

	def keyPressEvent(self, event):
		if event.type()==event.KeyPress:
			if event.key()==Qt.Key.Key_Left:
				self.move_to(-1, 0)
			elif event.key()==Qt.Key.Key_Right:
				self.move_to(1, 0)
			elif event.key()==Qt.Key.Key_Up:
				self.move_to(0, -1)
			elif event.key()==Qt.Key.Key_Down:
				self.move_to(0, 1)
			elif event.key()==Qt.Key.Key_Return or event.key()==Qt.Key.Key_Enter:
				self.on_click_func()
			else:
				super().keyPressEvent(event)

	def setOnClick(self, func):
		self.on_click = func
		self.clicked.connect(self.on_click_func)

	def on_click_func(self):
		self.on_click()
		self.clearFocus()

	def setCursorToEdge(self, dx):
		pass

	def focusInEvent(self, event):
		self.setStyleSheet(self.focused_style)
		return super().focusInEvent(event)
	
	def focusOutEvent(self, event):
		self.setStyleSheet(self.defalut_style)
		return super().focusOutEvent(event)

class CustomLineEdit(NavigableMixin, QLineEdit):
	def __init__(self, row, col, placeholder, parent=None):
		QLineEdit.__init__(self, parent)
		NavigableMixin.__init__(self, row, col)
		self.setPlaceholderText(placeholder)

	def keyPressEvent(self, event):
		cursor_pos = self.cursorPosition()

		if event.key()==Qt.Key.Key_Left and cursor_pos==0:
			self.move_to(-1, 0)
		elif event.key()==Qt.Key.Key_Right and cursor_pos==len(self.text()):
			self.move_to(1, 0)
		elif event.key()==Qt.Key.Key_Up:
			self.move_to(0, -1)
		elif event.key()==Qt.Key.Key_Down:
			self.move_to(0, 1)
		else:
			super().keyPressEvent(event)

	def setCursorToEdge(self, dx):
		if dx<0:
			self.setCursorPosition(len(self.text()))
		else:
			self.setCursorPosition(0)

class CustomComboBox(NavigableMixin, QComboBox):
	def __init__(self, row, col, editable=False, placeholder="", parent=None):
		QComboBox.__init__(self, parent)
		NavigableMixin.__init__(self, row, col)
		self.setEditable(editable)

		self.user_selected = False

		if editable and self.lineEdit() is not None:
			self.lineEdit().setReadOnly(False)
			self.lineEdit().setPlaceholderText(placeholder)
			self.lineEdit().installEventFilter(self)
		else:
			self.setPlaceholderText(placeholder)

	def keyPressEvent(self, event):
		if event.type() == event.KeyPress:
			if event.key()==Qt.Key.Key_Left:
				if ((not self.isEditable()) or
					(self.isEditable() and self.lineEdit().cursorPosition()==0)):
					self.move_to(-1, 0)
				elif self.isEditable():
					self.lineEdit().setCursorPosition(self.lineEdit().cursorPosition()-1)
			elif event.key()==Qt.Key.Key_Right:
				if ((not self.isEditable()) or
					(self.isEditable() and self.lineEdit().cursorPosition()==len(self.currentText()))):
					self.move_to(1, 0)
				elif self.isEditable():
					self.lineEdit().setCursorPosition(self.lineEdit().cursorPosition()+1)
			elif event.key()==Qt.Key.Key_Up:
				if self.user_selected:
					self.setCurrentIndex(max(0, self.currentIndex()-1))
				else:
					self.move_to(0, -1)
			elif event.key()==Qt.Key.Key_Down:
				if self.user_selected:
					self.setCurrentIndex(min(self.currentIndex()+1, self.count()-1))
				else:
					self.move_to(0, 1)
			elif event.key()==Qt.Key.Key_Return or event.key()==Qt.Key.Key_Enter:
				if self.user_selected:
					self.user_selected = False
					self.hidePopup()
				else:
					self.user_selected = True
					self.showPopup()
			else:
				super().keyPressEvent(event)
		else:
			super().keyPressEvent(event)
	
	def setCursorToEdge(self, dx):
		if self.isEditable():
			self.lineEdit().selectAll()
			self.lineEdit().setFocus()
			if dx<0:
				self.lineEdit().setCursorPosition(len(self.currentText()))
			else:
				self.lineEdit().setCursorPosition(0)

	def focusInEvent(self, event):
		self.user_selected = False
		super().focusInEvent(event)
		self.hidePopup()

class FileType:
	alltype = "所有文件 (*)"
	text = "文本文件 (*.txt)"
	excel = "Excel 文件 (*.xlsx)"

class FilePicker(QWidget):
	def __init__(self, text="", filetype=FileType.alltype, parent=None):
		super().__init__(parent)
		layout = QGridLayout()
		self.button = QPushButton(text)
		self.line_edit = QLineEdit()
		self.line_edit.setReadOnly(True)
		self.filetype = filetype
		layout.addWidget(self.line_edit, 0, 0)
		layout.addWidget(self.button, 0, 1)

		self.button.clicked.connect(self.open_file_dialog)
		self.setLayout(layout)

	def open_file_dialog(self):
		options = QFileDialog.Options()
		file_name, _ = QFileDialog.getOpenFileName(
			self,
			"选择文件",
			os.path.expanduser("~/"),
			self.filetype,
			options=options
		)
		if file_name:
			self.process_file(file_name)

	def process_file(self, path):
		self.line_edit.setText(path)
		pass

	def get_path(self):
		return self.line_edit.text()
	
	def set_path(self, path):
		self.line_edit.setText(path)

class TextSaver(QWidget):
	def __init__(self, text="", filetype=FileType.text, parent=None):
		super().__init__(parent)
		layout = QGridLayout()
		self.button = QPushButton(text)
		self.filetype = filetype
		self.content_reader = BlankFunction
		layout.addWidget(self.button, 0, 0)

		self.button.clicked.connect(self.save_text)
		self.setLayout(layout)

	def set_content_reader(self, func):
		self.content_reader = func

	def save_text(self):
		content = self.content_reader()

		options = QFileDialog.Options()
		file_name, _ = QFileDialog.getSaveFileName(
			self,
			"保存文件",
			"",
			self.filetype,
			options=options
		)

		if file_name:
			try:
				if not file_name.endswith(".txt"):
					file_name += ".txt"

				with open(file_name, "w", encoding="utf-8") as f:
					f.write(content)
			except Exception as e:
				print("[TextSaver]: ", e)