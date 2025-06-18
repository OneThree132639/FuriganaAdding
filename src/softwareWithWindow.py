import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QLabel, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QMainWindow, QStackedWidget, QLineEdit,
    QTextEdit
)
import FuriganaAdditionPackaged as FAP
import CustomPyQt5 as CPQ

class TableWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.table = CPQ.DataFrameViewer()
        self.update_table()
        self.update_button = QPushButton("刷新表格")
        self.update_button.clicked.connect(self.update_table)

        layout.addWidget(self.update_button)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def update_table(self):
        dic = FAP.Dictionary()
        self.table.load_data(dic.outputdf())

    
class SearchWindow(QWidget):
    def __init__(self, PlaceHolderText, ButtonText, parent=None):
        super().__init__(parent)
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText(PlaceHolderText)
        self.button_search = CPQ.CustomButton(0, 2, ButtonText)
        self.index_input = CPQ.CustomLineEdit(1, 0, "请输入需要删除的行数")
        self.indexType_input = CPQ.CustomComboBox(1, 1)
        self.button_delete = CPQ.CustomButton(1, 2, "删除")
        self.informText = QLabel()

        self.indexType_input.addItems(["原索引", "子索引"])
        self.init_ui()

        self.search_df = pd.DataFrame()

    def init_ui(self):
        layout = QGridLayout()
        layout.addWidget(self.line_edit, 0, 0, 1, 2)
        layout.addWidget(self.button_search, 0, 2)
        layout.addWidget(self.index_input, 1, 0)
        layout.addWidget(self.indexType_input, 1, 1)
        layout.addWidget(self.button_delete, 1, 2)
        layout.addWidget(self.informText, 2, 0)

        self.viewer = CPQ.DataFrameViewer()

        layout.addWidget(self.viewer, 3, 0, 2, 3)

        self.button_search.setOnClick(self.search)
        self.button_delete.setOnClick(self.delete)
        self.line_edit.returnPressed.connect(self.search)

        self.setLayout(layout)


    def search(self):
        current_text = self.line_edit.text()
        dic = FAP.Dictionary()
        df = dic.outputdf()
        self.search_df = pd.DataFrame(columns=df.columns)
        for i in self.search_df.columns:
            self.search_df[i] = self.search_df[i].astype(str)
        
        data_list = []
        for index, row in df.iterrows():
            if current_text in FAP.simplify(row["Japanese"]) or current_text in FAP.simplify(row["Kana"]):
                tempDic = row.to_list()
                tempDic.append(index)
                tempDic.append(len(data_list))
                data_list.append(tempDic)
        self.search_df = pd.DataFrame(data_list, columns=list(df.columns)+["Original Index", "Subtable Index"])
        self.search_df = self.search_df[["Original Index", "Subtable Index", "Japanese", "Kana", "Division", "Type", "Priority"]]
        self.viewer.load_data(self.search_df)

    def delete(self):
        dic = FAP.Dictionary()
        df = dic.outputdf()
        index = self.index_input.text()
        try:
            index = int(index)
        except:
            self.informText.setText("索引输入需为整数!")
            self.index_input.setText("")
            self.index_input.setFocus()
            return
        match(self.indexType_input.currentText()):
            case "原索引":
                if 0<=index<df.shape[0]:
                    dic.delete(index)
                    main_window = self.window()

                    if isinstance(main_window, MainWindow):
                        setting_viewer = main_window.setting_viewer
                    try:
                        backup_dic = FAP.Dictionary(setting_viewer.backup_dic_path.line_edit.text())
                        backup_dic.savedf(df)
                    except:
                        pass

                    self.informText.setText("删除成功!")
                else:
                    self.informText.setText("索引超出原索引范围(0~{})!".format(df.shape[0]-1))
            case "子索引":
                subindex = int(self.search_df.at[index, "Original Index"])
                if 0<=index<self.search_df.shape[0]:
                    dic.delete(subindex)
                    self.informText.setText("删除成功!")
                else:
                    self.informText.setText("索引超出子索引范围(0~{})!".format(self.search_df.shape[0]-1))
        self.index_input.setText("")
        self.index_input.setFocus()
        return

class NewTermWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QGridLayout()

        self.init_ui()

        layout.addWidget(self.Japanese_input, 0, 0)
        layout.addWidget(self.Kana_input, 0, 1)
        layout.addWidget(self.Division_input, 0, 2)
        layout.addWidget(self.Type_input, 1, 0)
        layout.addWidget(self.Priority_input, 1, 1)
        layout.addWidget(self.button_reject, 1, 2)
        layout.addWidget(self.button_auto, 2, 0)
        layout.addWidget(self.button_addition, 2, 1)
        layout.addWidget(self.button_agree, 2, 2)
        layout.addWidget(self.InformText, 3, 0, 1, 3)

        self.setLayout(layout)

    def init_ui(self):
        self.Japanese_input = CPQ.CustomLineEdit(0, 0, "请输入日语单词")
        self.Kana_input = CPQ.CustomLineEdit(0, 1, "请输入单词对应的读音")
        self.Division_input = CPQ.CustomComboBox(0, 2, True, "请输入分割方式")
        self.Type_input = CPQ.CustomComboBox(1, 0, False, "请选择词性")
        self.Priority_input = CPQ.CustomComboBox(1, 1, False, "请选择优先级")
        self.button_reject = CPQ.CustomButton(1, 2, "取消")
        self.button_auto = CPQ.CustomButton(2, 0, "自动分割")
        self.button_addition = CPQ.CustomButton(2, 1, "添加")
        self.button_agree = CPQ.CustomButton(2, 2, "确认")
        self.InformText = QTextEdit()
        

        self.Division_input.addItems(["0", "0/-1", "0\\-1", "-1/0", "0/-1/0", "0/-1\\-1",
                                      "0/-1/0/-1", "-1/0/-1", "0/-1/0\\-1"])
        self.Type_input.addItems(["名詞", "五段", "上下", "形容", "サ行", "タ行"])
        self.Priority_input.addItems(["0", "1", "2"])

        self.button_addition.setOnClick(self.addition_click_on)

        self.InformText.setPlaceholderText("等待单词输入中...")
        self.InformText.setReadOnly(True)

        self.Agree_Reject_Availability = False
        self.button_agree.setOnClick(self.agree_click_on)
        self.button_reject.setOnClick(self.reject_click_on)
        self.button_auto.setOnClick(self.AutoDivision_click_on)

        self.term_list = [self.Japanese_input.text(), self.Kana_input.text(),
                          self.Division_input.currentText(), self.Type_input.currentText(),
                          self.Priority_input.currentText()]
        
    def update_list(self):
        self.term_list = [self.Japanese_input.text(), self.Kana_input.text(),
                          self.Division_input.currentText(), self.Type_input.currentText(),
                          self.Priority_input.currentText()]
    
    def addition_click_on(self):
        self.update_list()
        if FAP.Term(self.term_list).isLegal():
            dic = FAP.Dictionary()
            addition = FAP.Addition()
            if dic.isIndf(self.term_list):
                informText = "该输入已经存在!"
                self.InformText.setText(informText)
                self.Agree_Reject_Availability = False
            else:
                informText = "该输入合法,标准输出形式如下:\n"+addition.printform(self.term_list)
                self.InformText.setText(informText)
                self.Agree_Reject_Availability = True
                self.button_agree.setFocus()
        else:
            informtext = "该输入非法!"
            self.InformText.setText(informtext)
            self.Agree_Reject_Availability = False

    def agree_click_on(self):
        if self.Agree_Reject_Availability:
            informText = "添加成功!"
            self.InformText.setText(informText)
            dic = FAP.Dictionary()
            df = dic.dfappend(self.term_list)
            dic.savedf(df)

            main_window = self.window()
            if isinstance(main_window, MainWindow):
                setting_viewer = main_window.setting_viewer
            try:
                backup_dic = FAP.Dictionary(setting_viewer.backup_dic_path.line_edit.text())
                backup_dic.savedf(df)
            except:
                pass

            self.Agree_Reject_Availability = False
            self.Japanese_input.setText("")
            self.Kana_input.setText("")
            self.Japanese_input.setFocus()

    def reject_click_on(self):
        if self.Agree_Reject_Availability:
            informText = "已取消添加操作"
            self.InformText.setText(informText)
            self.Agree_Reject_Availability = False

    def AutoDivision_click_on(self):
        self.update_list()
        tempTerm = FAP.Term(self.term_list)
        try:
            tempTerm = tempTerm.AutoDivision()
        except:
            informText = "不合法的单词,假名和类型输入\n无法自动分割"
            self.InformText.setText(informText)
            return None
        self.Japanese_input.setText(tempTerm[0])
        self.Kana_input.setText(tempTerm[1])
        self.Division_input.setCurrentText(tempTerm[2])
        self.Type_input.setCurrentText(tempTerm[3])
        self.Priority_input.setCurrentText(tempTerm[4])
        self.button_addition.setFocus()
    
class InTextWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.button_operation = QPushButton("添加注音")
        self.text_edit = QTextEdit()
        intext = FAP.InText()
        self.text_edit.setText(intext.read_text())
        layout = QHBoxLayout()
        layout.addWidget(self.button_operation)
        layout.addWidget(self.text_edit)

        self.button_operation.clicked.connect(self.operation)

        self.setLayout(layout)

    def operation(self):
        intext = FAP.InText()
        intext.write_text(self.text_edit.toPlainText())
        addition = FAP.Addition()
        addition.operation()
        
        main_window = self.window()
        if isinstance(main_window, MainWindow):
            setting_viewer = main_window.setting_viewer
        try:
            backup_intext = FAP.InText(setting_viewer.backup_in_path.line_edit.text())
            backup_intext.write_text(intext.read_text())
        except:
            pass
        try:
            backup_outtext = FAP.OutText(setting_viewer.backup_out_path.line_edit.text())
            addition.operation(outtext=backup_outtext)
        except:
            pass


class OutTextWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.text_edit = QTextEdit()
        self.update_outtext()
        self.button_update = QPushButton("刷新输出文档")
        newtermwindow = NewTermWindow()
        layout = QHBoxLayout()
        layout.addWidget(self.button_update)
        layout.addWidget(self.text_edit)
        layout.addWidget(newtermwindow)

        self.button_update.clicked.connect(self.update_outtext)

        self.setLayout(layout)

    def update_outtext(self):
        addition = FAP.Addition()
        addition.operation()
        outtext = FAP.OutText()
        self.text_edit.setText(outtext.read_text())
        self.text_edit.setReadOnly(True)

        main_window = self.window()
        if isinstance(main_window, MainWindow):
            setting_viewer = main_window.setting_viewer
        try:
            backup_outtext = FAP.OutText(setting_viewer.backup_out_path.line_edit.text())
            addition.operation(outtext=backup_outtext)
        except:
            pass

class SettingWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        LastSetting = CPQ.SettingJson(FAP.APP_NAME)
        self.settings = LastSetting.load_settings()

        self.backup_dic_path = CPQ.FilePicker("选择备份表格", CPQ.FileType.excel)
        self.backup_in_path = CPQ.FilePicker("选择备份输入", CPQ.FileType.text)
        self.backup_out_path = CPQ.FilePicker("选择备份输出", CPQ.FileType.text)

        self.backup_dic_path.set_path(self.settings.get("backup_dic_path", ""))
        self.backup_in_path.set_path(self.settings.get("backup_in_path", ""))
        self.backup_out_path.set_path(self.settings.get("backup_out_path", ""))

        layout = QGridLayout()
        layout.addWidget(self.backup_dic_path, 0, 0)
        layout.addWidget(self.backup_in_path, 1, 0)
        layout.addWidget(self.backup_out_path, 2, 0)

        self.setLayout(layout)

    def get_paths(self):
        return {
            "backup_dic_path": self.backup_dic_path.get_path(),
            "backup_in_path": self.backup_in_path.get_path(),
            "backup_out_path": self.backup_out_path.get_path()
        }
    
    def closeEvent(self, event):
        paths = self.get_paths()
        settingjson = CPQ.SettingJson(FAP.APP_NAME)
        settingjson.save_settings(paths)
        super().closeEvent(event)
        
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FAP Software")
        self.resize(1000, 600)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QVBoxLayout(main_widget)
        self.button_layout = QHBoxLayout()
        self.stacked_widget = QStackedWidget()
        self.setting_viewer = SettingWindow()

        main_layout.addLayout(self.button_layout, 1)
        main_layout.addWidget(self.stacked_widget, 4)

        self.add_page("Dic", self.create_page_dic())
        self.add_page("In Text", self.create_page_in_text())
        self.add_page("Out Text", self.create_page_out_text())
        self.add_page("Setting", self.setting_viewer)

    def add_page(self, button_text, page_widget):
        btn = QPushButton(button_text)
        btn.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(page_widget))
        self.button_layout.addWidget(btn)
        self.stacked_widget.addWidget(page_widget)

    def create_page_dic(self):
        widget = QWidget()
        layout = QGridLayout()
        searchwindow = SearchWindow("请输入要查找的文本", "查找")       
        newtermwindow = NewTermWindow()
        table_viewer = TableWindow()

        layout.addWidget(table_viewer, 0, 0, 6, 1)
        layout.addWidget(searchwindow, 0, 1, 3, 1)
        layout.addWidget(newtermwindow, 3, 1, 3, 1)
        widget.setLayout(layout)
        return widget
    
    def create_page_in_text(self):
        intextwindow = InTextWindow()
        return intextwindow
    
    def create_page_out_text(self):
        outtextwindow = OutTextWindow()
        return outtextwindow
    
    def closeEvent(self, event):
        paths = self.setting_viewer.get_paths()
        settingjson = CPQ.SettingJson(FAP.APP_NAME)
        settingjson.save_settings(paths)
        return super().closeEvent(event)

if __name__ == "__main__":
    pass