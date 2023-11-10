from PyQt5.QtWidgets import (QLineEdit,QFormLayout, QGroupBox, QScrollArea,
                             QVBoxLayout, QWidget)
from PyQt5.QtCore import pyqtSignal, pyqtSlot


class SimulationConfigEditorWidget(QWidget):
    sampling_generated = pyqtSignal(int)
    def __init__(self, simulation_config=None,logger=None):

        super().__init__()
        self.logger = logger
        self.config = simulation_config

        # Create a QScrollArea
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        # Create a widget for the scroll area
        scroll_widget = QWidget()

        # Create QLineEdit widgets for each of the config parameters you want to edit
        self.grid_size = QLineEdit()
        self.grid_sampling = QLineEdit()
        self.nb_of_samples = QLineEdit()
        self.nb_of_samples.setReadOnly(True)  # The dimensions should be read-only
        # Add more fields as needed...

        # Create a form layout and add your QLineEdit widgets
        general_layout = QFormLayout()
        general_layout.addRow("Grid Size [in mm]", self.grid_size)
        general_layout.addRow("Grid Sampling [in um]", self.grid_sampling)
        general_layout.addRow("Nb of Samples along X and Y", self.nb_of_samples)
        # Add more rows as needed...

        self.sampling_generated.connect(self.update_nb_of_samples)


        general_group = QGroupBox("Simulation Settings")
        general_group.setLayout(general_layout)

        # # Load config button
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
                "grid sampling": float(self.grid_sampling.text()),
                "grid size": float(self.grid_size.text()),
        }

        self.config = config
        return config

    def update_config(self):
        # This method should update your QLineEdit and QSpinBox widgets with the loaded config.

        self.grid_sampling.setText(str(self.config['grid sampling']))
        self.grid_size.setText(str(self.config['grid size']))

    @pyqtSlot(int)
    def update_nb_of_samples(self, nb_of_samples):
        # Update the GUI in this slot function, which is called from the main thread
        self.nb_of_samples.setText(str(nb_of_samples))

