import os
import shutil
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QSettings, pyqtSignal

class FolderMover(QWidget):
    def __init__(self):
        self.target_path_root = '/Volumes/16T_A/XSK'
        self.current_processing_path = ''
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('A片便捷移动器')

        self.target_path_display = QLineEdit('/Volumes/16T_A/XSK')

        self.folder_name_label = QLabel('片名')
        self.folder_name_display = QLineEdit()
        self.folder_name_display.setReadOnly(True)

        self.selected_name_label = QLabel('演员名')
        self.selected_name_display = QLineEdit()

        self.move_button = QPushButton('移动 (必要时创建演员文件夹)')
        self.move_without_create_dir_button = QPushButton('只移动')
        self.move_button.clicked.connect(self.move_folder)
        self.move_without_create_dir_button.clicked.connect(self.move_folder_no_creation)


        drop_widget = DragDropWidget()
        drop_widget.setFixedSize(500, 200)
        drop_widget.fileDropped.connect(self.process_files)

        layout = QVBoxLayout()
        layout.addWidget(self.target_path_display)
        layout.addWidget(drop_widget)
        layout.addWidget(self.folder_name_label)
        layout.addWidget(self.folder_name_display)
        layout.addWidget(self.selected_name_label)
        layout.addWidget(self.selected_name_display)
        layout.addWidget(self.move_button)
        layout.addWidget(self.move_without_create_dir_button)

        self.setLayout(layout)

    def process_files(self, filePaths):
        self.target_path_root = self.target_path_display.text()
        for folder_path in filePaths:
            if not os.path.isdir(folder_path):
                continue
            self.current_processing_path = folder_path
            folder_name = os.path.basename(folder_path.rstrip(os.sep)).strip()
            self.folder_name_display.setText(folder_name)
            maybe_actor_name = folder_name.split(' ')[-1]
            self.selected_name_display.setText(maybe_actor_name)

            # try to move folder automatically
            target_root_path = os.path.join(self.target_path_root, maybe_actor_name)

            if os.path.exists(target_root_path):
                target_folder_path = os.path.join(target_root_path, folder_name)
                if os.path.exists(target_folder_path):
                    print(f'file duplicated {target_folder_path}')
                else:
                    print(f'move folder {folder_name}')
                    shutil.move(folder_path, target_root_path)

    def move_folder(self):
        self.target_path_root = self.target_path_display.text()
        selected_name = self.selected_name_display.text().strip()
        target_path = os.path.join(self.target_path_root, selected_name)
        if not os.path.exists(target_path):
            os.makedirs(target_path)
        folder_name = self.folder_name_display.text()
        target_folder_path = os.path.join(target_path, folder_name)
        if os.path.exists(target_folder_path):
            print(f'file duplicated {target_folder_path}')
        else:
            shutil.move(self.current_processing_path, target_path)

    def move_folder_no_creation(self):
        self.target_path_root = self.target_path_display.text()
        selected_name = self.selected_name_display.text().strip()
        target_path = os.path.join(self.target_path_root, selected_name)
        if not os.path.exists(target_path):
            print('no existing folder, no move')
            return
        folder_name = self.folder_name_display.text()
        target_folder_path = os.path.join(target_path, folder_name)
        if os.path.exists(target_folder_path):
            print(f'file duplicated {target_folder_path}')
        else:
            shutil.move(self.current_processing_path, target_path)


class DragDropWidget(QLabel):
    fileDropped = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("文件夹拖放至此")
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("QLabel { background-color : grey; }")
        self.setAcceptDrops(True)
        self.isVideoPriority = True

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            filePaths = [url.toLocalFile() for url in urls]
            self.fileDropped.emit(filePaths)


if __name__ == '__main__':
    app = QApplication([])
    window = FolderMover()
    window.show()
    app.exec_()
