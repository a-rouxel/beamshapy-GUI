import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QDockWidget,QTextEdit
from PyQt5.QtGui import QIcon
from gui_elements import InputBeamWidget
from gui_elements import TargetFieldDesignWidget
from gui_elements import InputBeamEditorWidget
from gui_elements import SimulationConfigEditorWidget
from gui_elements import SLMMaskWidget
from gui_elements import InfosEditorWidget
from gui_elements import FourierPlaneDetectionWidget

from beamshapy import *

import os
import logging

os.environ["QT_NO_FT_CACHE"] = "1"

class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QTextEdit(parent)
        self.widget.setReadOnly(True)
        # Set the background color to black and text color to white
        self.widget.setStyleSheet("QTextEdit { background-color: #000; color: #FFF; }")

    def emit(self, record):
        msg = self.format(record)
        self.widget.append(msg)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon('logo_beam_shaper.png'))  # Uncomment this line
        self.setWindowTitle('Beam Shaping FFT')

        # Create a QTextEditLogger
        logTextBox = QTextEditLogger(self)
        # You might want to format what is printed to QTextEdit
        logTextBox.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s •  %(message)s', "%Y-%m-%d %H:%M:%S"))
        handler = logTextBox


        # Create a logger for this MainWindow
        self.logger = logging.getLogger(type(self).__name__)
        self.logger.addHandler(handler)

        # You can control the logging level
        self.logger.setLevel(logging.INFO)


        self.infos_editor = InfosEditorWidget(initial_infos_config_path="../../beamshapy/beamshapy/config/infos.yml", logger=self.logger)
        self.input_beam_editor = InputBeamEditorWidget(initial_input_beam_config_path="../../beamshapy/beamshapy/config/input_beam.yml", logger=self.logger)
        self.simulation_editor = SimulationConfigEditorWidget(simulation_config_path="../../beamshapy/beamshapy/config/simulation.yml", logger=self.logger)


        self.BeamShaper = BeamShaper(self.simulation_editor.get_config(),
                                     self.input_beam_editor.get_config(),
                                     initial_config_file="../../beamshapy/beamshapy/config/optical_system.yml")

        self.input_beam_widget = InputBeamWidget(self.BeamShaper,
                                                 self.infos_editor,
                                                 self.simulation_editor,
                                                 self.input_beam_editor,logger=self.logger)
        self.input_beam_dock = QDockWidget("Input Beam")
        self.input_beam_dock.setWidget(self.input_beam_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.input_beam_dock)

        self.target_amplitude_widget = TargetFieldDesignWidget(self.BeamShaper,
                                                               self.infos_editor,
                                                               self.simulation_editor,
                                                               target_target_amplitude_config_path="beamshapy/beamshapy/config/target_amplitude.yml",
                                                               logger=self.logger)
        self.target_amplitude_dock = QDockWidget("Target Amplitude")
        self.target_amplitude_dock.setWidget(self.target_amplitude_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.target_amplitude_dock)

        self.SLM_mask_widget = SLMMaskWidget(self.BeamShaper,
                                             self.infos_editor,
                                             self.simulation_editor,
                                             slm_mask_config_path="beamshapy/beamshapy/config/slm_mask.yml",
                                             logger = self.logger)
        self.SLM_mask_dock = QDockWidget("SLM Masks")
        self.SLM_mask_dock.setWidget(self.SLM_mask_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.SLM_mask_dock)
        #
        self.fourier_plane_detection_widget = FourierPlaneDetectionWidget(self,self.BeamShaper,
                                                                          self.infos_editor,
                                                                         self.SLM_mask_widget,
                                                                         )
        self.fourier_plane_detection_dock = QDockWidget("Detection")
        self.fourier_plane_detection_dock.setWidget(self.fourier_plane_detection_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.fourier_plane_detection_dock)

        self.tabifyDockWidget(self.input_beam_dock, self.target_amplitude_dock)
        self.tabifyDockWidget(self.target_amplitude_dock, self.SLM_mask_dock)
        self.tabifyDockWidget(self.SLM_mask_dock, self.fourier_plane_detection_dock)

        self.input_beam_dock.raise_()

        # Add the new logging box widget to the layout
        self.log_dock = QDockWidget("Log Messages")
        self.log_dock.setWidget(logTextBox.widget)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.log_dock)
        self.setGeometry(100, 100, 1000, 900)




if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('logo_beam_shaper.png'))

    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec_())