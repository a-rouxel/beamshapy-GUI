from PyQt5.QtWidgets import (QLineEdit, QComboBox,QFormLayout, QGroupBox, QScrollArea,
                             QVBoxLayout, QCheckBox, QSpinBox, QWidget)

class InputBeamEditorWidget(QWidget):
    def __init__(self,input_beam_config=None,logger=None):
        super().__init__()
        self.logger = logger

        self.config = input_beam_config
        # Create a QScrollArea
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        # Create a widget for the scroll area
        scroll_widget = QWidget()

        self.simulation_grid_size = QLineEdit()
        self.simulation_sampling = QLineEdit()

        self.beam_type = QComboBox()
        self.beam_type.addItems(["Plane","Gaussian"])
        self.beam_waist = QLineEdit()
        self.beam_wavelength = QLineEdit()

        self.beam_LG = QCheckBox()
        self.beam_n = QSpinBox()
        self.beam_m = QSpinBox()

        general_layout = QFormLayout()
        general_layout.addRow("beam type", self.beam_type)
        general_layout.addRow("waist [in mm]", self.beam_waist)
        general_layout.addRow("wavelength [in nm]", self.beam_wavelength)
        general_layout.addRow("LG", self.beam_LG)
        general_layout.addRow("n", self.beam_n)
        general_layout.addRow("m", self.beam_m)

        general_group = QGroupBox("Input Beam Settings")
        general_group.setLayout(general_layout)


        # Load config button
        # self.load_config_button = QPushButton("Load Config")
        # self.load_config_button.clicked.connect(self.on_load_config_clicked)
        # self.save_config_button = QPushButton("Save Config")
        # self.save_config_button.clicked.connect(self.save_config)

        # Create main layout and add widgets
        main_layout = QVBoxLayout()
        main_layout.addWidget(general_group)
        # main_layout.addWidget(self.load_config_button)
        # main_layout.addWidget(self.save_config_button)

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
            "beam": {
                "type": self.beam_type.currentText(),
                "waist": float(self.beam_waist.text()),
                "wavelength": float(self.beam_wavelength.text()),
                "LG": bool(self.beam_LG.isChecked()),
                "n": int(self.beam_n.text()),
                "m": int(self.beam_m.text()),
            },
        }

        self.config = config

        return config

    def update_config(self):
        # This method should update your QLineEdit and QSpinBox widgets with the loaded config.

        self.beam_type.setCurrentText(self.config['beam']['type'])
        self.beam_waist.setText(str(self.config['beam']['waist']))
        self.beam_wavelength.setText(str(self.config['beam']['wavelength']))
        self.beam_LG.setChecked(self.config['beam']['LG'])
        self.beam_n.setValue(self.config['beam']['n'])
        self.beam_m.setValue(self.config['beam']['m'])