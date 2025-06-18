from softwareWithWindow import MainWindow
from PyQt5.QtWidgets import QApplication
import sys

def main():
	print("[Program Start]")
	try:
		app = QApplication(sys.argv)
		window = MainWindow()
		window.show()
		sys.exit(app.exec_())
	except Exception as e:
		import traceback
		print("[Unhandled exception]: ")
		traceback.print_exc()
		input("Press Enter to exit...")

if __name__ == "__main__":
	main()