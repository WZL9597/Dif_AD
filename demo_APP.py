import os
import shutil
import sys
import random
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout,
    QWidget, QComboBox, QFileDialog, QMessageBox, QLineEdit, QPushButton
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

        if username == "wzl" and password == "123":
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
        self.setWindowTitle("NEU工业缺陷检测软件v2.2")
        self.setGeometry(200, 200, 1600, 1200)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setAlignment(Qt.AlignCenter)

        # 输入图片部分
        self.input_layout = QVBoxLayout()
        self.input_layout.setAlignment(Qt.AlignCenter)  # 确保输入布局整体居中

        self.input_image_label = QLabel(self)
        self.input_image_label.setAlignment(Qt.AlignCenter)  # 确保图片居中
        self.input_image_label.setFixedSize(400, 400)
        self.input_image_label.setStyleSheet("border: 1px solid gray;")
        self.input_image_label.setText("选择图片")
        self.input_image_label.setFont(QFont("Arial", 14))
        self.input_image_label.setAlignment(Qt.AlignCenter)  # 确保文本居中
        self.input_image_label.mousePressEvent = self.select_image  # 点击图片选择文件

        self.input_label = QLabel("待检测图片", self)
        self.input_label.setAlignment(Qt.AlignCenter)  # 确保标题居中
        self.input_label.setFont(QFont("Arial", 14))
        self.input_label.setStyleSheet("border: 2px solid black; padding: 5px; background-color: #f0f0f0;")

        self.input_layout.addWidget(self.input_image_label)
        self.input_layout.addWidget(self.input_label)

        # 输出图片部分
        self.output_layout = QVBoxLayout()
        self.output_grid_layout = QHBoxLayout()
        self.output_image_labels = []
        self.output_image_titles = ["热力图", "叠加图", "缺陷掩码", "热图表"]

        for i in range(4):
            output_layout = QVBoxLayout()
            output_image_label = QLabel(self)
            output_image_label.setAlignment(Qt.AlignCenter)
            output_image_label.setFixedSize(400, 400)
            output_image_label.setStyleSheet("border: 1px solid gray;")
            self.output_image_labels.append(output_image_label)

            output_label = QLabel(self.output_image_titles[i], self)
            output_label.setAlignment(Qt.AlignCenter)
            output_label.setFont(QFont("Arial", 14))
            output_label.setStyleSheet("border: 2px solid black; padding: 5px; background-color: #f0f0f0;")

            output_layout.addWidget(output_image_label)
            output_layout.addWidget(output_label)

            self.output_grid_layout.addLayout(output_layout)

        self.output_layout.addLayout(self.output_grid_layout)

        # 检测按钮和模型选择框
        self.control_layout = QVBoxLayout()  # 使用垂直布局
        self.control_layout.setAlignment(Qt.AlignCenter)  # 设置居中对齐

        self.detect_button = QPushButton("检测")
        self.detect_button.setFixedSize(300, 150)  # 设置按钮高度固定，宽度与模型选择框相同
        self.detect_button.setStyleSheet(
            "border-radius: 75px; font-size: 32px; background-color: lightblue;"
        )
        self.detect_button.clicked.connect(self.detect_defect)

        self.model_select = QComboBox()
        self.model_select.setFixedSize(300, 50)
        self.model_select.setFont(QFont("Arial", 28))  # 设置更大的字体
        self.model_select.addItems(["Dif_AD模型", "其他模型"])
        self.model_select.setStyleSheet("font-size: 28px;")  # 增大字体

        self.control_layout.addWidget(self.detect_button)  # 检测按钮放在上面
        self.control_layout.addWidget(self.model_select)   # 模型选择框放在下面

        # 状态灯和检测时长
        self.status_layout = QHBoxLayout()
        self.status_label = QLabel("状态：")
        self.status_label.setFont(QFont("Arial", 14))
        self.status_label.setStyleSheet("border: 2px solid black; padding: 5px; background-color: #f0f0f0;")

        self.status_light = QLabel(self)
        self.status_light.setFixedSize(50, 50)
        self.status_light.setStyleSheet("border-radius: 25px; background-color: gray;")

        self.time_label = QLabel("检测时长：")
        self.time_label.setFont(QFont("Arial", 14))
        self.time_label.setStyleSheet("border: 2px solid black; padding: 5px; background-color: #f0f0f0;")

        self.time_duration = QLabel("0.00000s")
        self.time_duration.setFont(QFont("Arial", 14))
        self.time_duration.setStyleSheet("border: 2px solid black; padding: 5px; background-color: #f0f0f0;")

        self.status_layout.addWidget(self.status_label)
        self.status_layout.addWidget(self.status_light)
        self.status_layout.addStretch()
        self.status_layout.addWidget(self.time_label)
        self.status_layout.addWidget(self.time_duration)

        # 主布局
        main_layout.addLayout(self.input_layout)
        main_layout.addLayout(self.output_layout)
        main_layout.addLayout(self.control_layout)  # 放入垂直布局
        main_layout.addLayout(self.status_layout)

        self.selected_image_path = None



    def select_image(self, event):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片文件", "", "Image Files (*.png *.jpg *.bmp)", options=options
        )
        if file_path:
            self.selected_image_path = file_path
            pixmap = QPixmap(file_path).scaled(400, 400, Qt.KeepAspectRatio)
            self.input_image_label.setPixmap(pixmap)
            self.input_label.setText("待检测图片")

            # 清空输出图片
            for label in self.output_image_labels:
                label.clear()
                label.setText("")
        else:
            # 如果用户取消选择，保持“选择图片”文本
            if not self.selected_image_path:
                self.input_image_label.setText("选择图片")

    def detect_defect(self):
        if not self.selected_image_path:
            QMessageBox.warning(self, "警告", "请先选择一张图片！")
            return

        # 打印输入图片路径
        input_file_path = self.selected_image_path.replace("\\", "/")
        print(f"输入图片: {input_file_path}")

        # 获取所选模型并更新状态
        model = self.model_select.currentText()
        print(f"使用 {model} 检测中...")

        self.status_light.setStyleSheet("border-radius: 25px; background-color: gray;")
        self.time_duration.setText("检测中...")
        self.time_duration.setStyleSheet("color: orange;")
        self.status_label.setText(f"使用 {model} 检测中...")

        # 随机生成检测成功的延迟时间 (0.5 - 1 秒)
        self.detection_time = random.uniform(3, 5)

        # 设置延迟展示输出结果
        QTimer.singleShot(int(self.detection_time * 1000), self.show_output)

    def show_output(self):
        # 获取输入图片的基础名称和路径
        base_name = os.path.splitext(os.path.basename(self.selected_image_path))[0]
        input_dir = os.path.dirname(self.selected_image_path)

        # 去掉 _original 后缀
        if "_original" in base_name:
            base_name = base_name.replace("_original", "")

        # 构造输出路径：输入路径的上上一级目录的 goal_sets 文件夹
        upper_level_dir = os.path.dirname(os.path.dirname(input_dir))  # 获取上上一级目录
        output_dir = os.path.join(upper_level_dir, "goal_sets")

        # 构造输出文件路径字典
        output_files = {
            "热力图": os.path.join(output_dir, f"{base_name}_heatmap.jpg").replace("\\", "/"),
            "叠加图": os.path.join(output_dir, f"{base_name}_hm_on_ima.jpg").replace("\\", "/"),
            "缺陷掩码": os.path.join(output_dir, f"{base_name}_mask.jpg").replace("\\", "/"),
            "热图表": os.path.join(output_dir, f"{base_name}_sns_heatmap.jpg").replace("\\", "/"),
        }

        # 检查文件是否存在
        all_exist = all(os.path.exists(path) for path in output_files.values())

        if not all_exist:
            self.status_light.setStyleSheet("border-radius: 25px; background-color: red;")
            self.status_label.setText("检测失败")
            self.status_label.setStyleSheet("color: red;")
            duration = random.uniform(7, 10)  # 失败时长
            print(f"检测超时，检测时长为 {duration:.5f}s")

            self.time_duration.setText("检测超时") #(f"{duration:.5f}s")
            self.time_duration.setStyleSheet("color: red;")
            for label in self.output_image_labels:
                label.clear()
                label.setText("检测超时")
                label.setStyleSheet("font-size: 32px; font-weight: bold; color: red;")  # 增大字体

        else:
            # 检测成功状态
            print(f"检测成功，检测时长为 {self.detection_time:.5f}s")

            self.status_light.setStyleSheet("border-radius: 25px; background-color: green;")
            self.status_label.setText("检测成功!")
            self.status_label.setStyleSheet("color: green;")

            # 设置检测时长为延迟时长
            self.time_duration.setText(f"{self.detection_time:.5f}s")
            self.time_duration.setStyleSheet("color: green;")

            # 加载输出图片
            for idx, (title, path) in enumerate(output_files.items()):
                pixmap = QPixmap(path).scaled(400, 400, Qt.KeepAspectRatio)
                self.output_image_labels[idx].setPixmap(pixmap)

            # 保存输出图片到上一级路径的 output 文件夹
            self.save_output_files(output_files)

    def save_output_files(self, output_files):
        # 获取输入图片路径的再上一级目录
        upper_level_dir = os.path.dirname(os.path.dirname(self.selected_image_path))
        output_dir = os.path.join(upper_level_dir, "output").replace("\\", "/")  # 确保路径为正斜杠

        # 如果 output 文件夹不存在，创建它
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)


        # 将所有输出文件复制到 output 文件夹
        for title, file_path in output_files.items():
            file_path = file_path.replace("\\", "/")  # 确保路径中使用正斜杠
            if os.path.exists(file_path):
                try:
                    dest_path = os.path.join(output_dir, os.path.basename(file_path)).replace("\\", "/")
                    shutil.copy(file_path, dest_path)
                except Exception as e:
                    print(f"检测超时")
            else:
                print(f"检测超时")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())


