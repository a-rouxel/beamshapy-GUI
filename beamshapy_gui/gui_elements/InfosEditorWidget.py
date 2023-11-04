
from PyQt5.QtWidgets import (QLineEdit,QFormLayout, QGroupBox, QScrollArea,
                             QVBoxLayout, QWidget)
import yaml


class InfosEditorWidget(QWidget):
    def __init__(self, initial_infos_config_path=None,logger=None):
        super().__init__()
        self.logger = logger
        self.initial_config_file = initial_infos_config_path

        # Create a QScrollArea
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        # Create a widget for the scroll area
        scroll_widget = QWidget()

        # Create QLineEdit widgets for each of the config parameters you want to edit
        self.simulation_name = QLineEdit()
        self.results_directory = QLineEdit()
        # Add more fields as needed...

        # Create a form layout and add your QLineEdit widgets
        general_layout = QFormLayout()
        general_layout.addRow("Simulation Name", self.simulation_name)
        general_layout.addRow("Results Directory", self.results_directory)
        # Add more rows as needed...

        general_group = QGroupBox("Infos")
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

        # Load the initial configuration file if one was provided
        if self.initial_config_file is not None:
            self.load_config(self.initial_config_file)

    def load_config(self, file_name):
        with open(file_name, 'r') as file:
            self.config = yaml.safe_load(file)
        # Call a method to update the GUI with the loaded config
        self.update_config()

    def get_config(self):

        config = {
                "simulation name": int(self.simulation_name.text()),
                "results directory": float(self.results_directory.text()),
        }
        self.config = config

        return config

    def update_config(self):
        # This method should update your QLineEdit and QSpinBox widgets with the loaded config.

        self.simulation_name.setText(str(self.config['simulation name']))
        self.results_directory.setText(str(self.config['results directory']))
