import os
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QWidget, QComboBox, QFileDialog, QMessageBox, QLineEdit
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer


class LoginWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("用户登录")
        self.setGeometry(200, 200, 800, 400)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        self.username_label = QLabel("用户名:")
        self.username_input = QLineEdit()
        self.password_label = QLabel("密码:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("登录")
        self.login_button.setFixedSize(200, 80)
        self.login_button.clicked.connect(self.check_login)

        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def check_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if username == "abc" and password == "123":
            self.accept()
        else:
            QMessageBox.warning(self, "错误", "用户名或密码错误！")

    def accept(self):
        self.close()
        self.main_window = DefectDetectionApp()
        self.main_window.show()


class DefectDetectionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("工业缺陷检测可视化软件")
        self.setGeometry(200, 200, 1600, 1200)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setAlignment(Qt.AlignCenter)

        # 输入图片部分
        self.input_layout = QVBoxLayout()
        self.input_label = QLabel("输入图片", self)
        self.input_label.setAlignment(Qt.AlignCenter)
        self.input_image_label = QLabel("未选择图片", self)
        self.input_image_label.setAlignment(Qt.AlignCenter)
        self.input_image_label.setFixedSize(400, 400)
        self.input_image_label.setStyleSheet("border: 1px solid gray;")
        self.input_layout.addWidget(self.input_label)
        self.input_layout.addWidget(self.input_image_label)

        # 将“选择图片”按钮放置在输入框内
        self.select_button = QPushButton("选择图片")
        self.select_button.setFixedSize(200, 80)
        self.select_button.setStyleSheet("border-radius: 40px; font-size: 18px;")
        self.select_button.clicked.connect(self.select_image)
        self.input_layout.addWidget(self.select_button)

        # 输出图片部分
        self.output_layout = QHBoxLayout()
        self.output_image_labels = []
        for i in range(4):
            output_image_label = QLabel(f"输出图片 {i + 1}", self)
            output_image_label.setAlignment(Qt.AlignCenter)
            output_image_label.setFixedSize(400, 400)
            output_image_label.setStyleSheet("border: 1px solid gray;")
            self.output_image_labels.append(output_image_label)
            self.output_layout.addWidget(output_image_label)

        # 图片展示布局
        image_layout = QVBoxLayout()
        image_layout.addLayout(self.input_layout)
        image_layout.addLayout(self.output_layout)
        main_layout.addLayout(image_layout)

        # 检测按钮
        self.detect_button = QPushButton("检测")
        self.detect_button.setFixedSize(300, 150)
        self.detect_button.setStyleSheet(
            "border-radius: 75px; font-size: 24px; background-color: lightblue;"
        )
        self.detect_button.clicked.connect(self.detect_defect)
        main_layout.addWidget(self.detect_button)

        # 检测状态
        self.status_label = QLabel("", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.status_label.setStyleSheet("color: red;")
        main_layout.addWidget(self.status_label)

        self.selected_image_path = None

    def select_image(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片文件", "", "Image Files (*.png *.jpg *.bmp)", options=options
        )
        if file_path:
            self.selected_image_path = file_path
            pixmap = QPixmap(file_path).scaled(400, 400, Qt.KeepAspectRatio)
            self.input_image_label.setPixmap(pixmap)
            self.input_label.setText("输入图片")

            # 清空输出图片
            for label in self.output_image_labels:
                label.clear()
                label.setText("")

    def detect_defect(self):
        if not self.selected_image_path:
            QMessageBox.warning(self, "警告", "请先选择一张图片！")
            return

        model = "模型1"  # 假设只使用一个模型
        self.status_label.setText(f"正在检测，请稍候...")

        QTimer.singleShot(500, self.show_output)

    def show_output(self):
        if not self.selected_image_path:
            return

        input_dir = os.path.dirname(self.selected_image_path)
        input_name, ext = os.path.splitext(os.path.basename(self.selected_image_path))
        base_name = input_name.replace("_original", "")

        output_paths = {
            "heatmap": os.path.join(input_dir, f"{base_name}_heatmap{ext}"),
            "hm_on_ima": os.path.join(input_dir, f"{base_name}_hm_on_ima{ext}"),
            "mask": os.path.join(input_dir, f"{base_name}_mask{ext}"),
            "sns_heatmap": os.path.join(input_dir, f"{base_name}_sns_heatmap{ext}"),
        }

        all_success = True
        for idx, (key, path) in enumerate(output_paths.items()):
            if os.path.exists(path):
                pixmap = QPixmap(path).scaled(400, 400, Qt.KeepAspectRatio)
                self.output_image_labels[idx].setPixmap(pixmap)
            else:
                self.output_image_labels[idx].setText("检测超时")
                all_success = False

        self.status_label.setText("检测完成！" if all_success else "检测失败！")
        if not all_success:
            for label in self.output_image_labels:
                label.clear()
                label.setText("")
if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
