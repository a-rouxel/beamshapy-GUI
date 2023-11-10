from PyQt5.QtWidgets import (QLineEdit,QFormLayout, QGroupBox, QScrollArea,
                             QVBoxLayout, QWidget)


class OpticalSystemEditorWidget(QWidget):

    # sampling_generated = pyqtSignal(int)

    def __init__(self, optical_system_config=None,logger=None):

        super().__init__()
        self.logger = logger
        self.config = optical_system_config

        # Create a QScrollArea
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        # Create a widget for the scroll area
        scroll_widget = QWidget()

        # Create QLineEdit widgets for each of the config parameters you want to edit
        self.focal_length = QLineEdit()

        # Create a form layout and add your QLineEdit widgets
        general_layout = QFormLayout()
        general_layout.addRow("focal length [in mm]", self.focal_length)

        general_group = QGroupBox("Optical System Settings")
        general_group.setLayout(general_layout)


        # Create main layout and add widgets
        main_layout = QVBoxLayout()
        main_layout.addWidget(general_group)

        # Set the layout of the widget within the scroll area
        scroll_widget.setLayout(main_layout)

        # Set the widget for the scroll area
        scroll.setWidget(scroll_widget)

        # Create a layout for the current widget and add the scroll area
        layout = QVBoxLayout(self)
        layout.addWidget(scroll)

        self.update_config()



    def get_config(self):

        config = {
                "focal length": float(self.focal_length.text()),
        }

        self.config = config
        return config

    def update_config(self):
        self.focal_length.setText(str(self.config['focal length']))


