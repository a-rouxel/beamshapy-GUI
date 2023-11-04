from PyQt5.QtWidgets import (QTabWidget,QHBoxLayout, QPushButton, QFileDialog,
                             QLineEdit, QComboBox,QFormLayout, QGroupBox, QScrollArea,
                             QVBoxLayout, QCheckBox, QSpinBox, QWidget)
from PyQt5.QtCore import Qt,QThread, pyqtSignal, pyqtSlot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from LightPipes import Field, Phase, Intensity
from beamshapy import *


class InputBeamIntensityDisplay(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.figure_cam = plt.figure()
        self.canvas_cam = FigureCanvas(self.figure_cam)
        self.toolbar_cam = NavigationToolbar(self.canvas_cam, self)

        self.layout.addWidget(self.toolbar_cam)
        self.layout.addWidget(self.canvas_cam)

    def display_input_beam_intensity(self, intensity, x_range_mm, y_range_mm):

        self.figure_cam.clear()

        ax = self.figure_cam.add_subplot(111)
        imshow = ax.imshow(intensity, cmap='viridis', extent=[-x_range_mm/2, x_range_mm/2, -y_range_mm/2, y_range_mm/2])
        self.figure_cam.colorbar(imshow)
        # Set labels with LaTeX font.
        ax.set_xlabel(f'Position along X [mm]', fontsize=10)
        ax.set_ylabel(f'Position along Y [mm]', fontsize=10)
        ax.set_title(f'Intensity Map', fontsize=12)

        self.canvas_cam.draw()


class InputBeamPhaseDisplay(QWidget):
    def __init__(self):
        super().__init__()

        # Create a QVBoxLayout for the widget
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.figure_cam = plt.figure()
        self.canvas_cam = FigureCanvas(self.figure_cam)
        self.toolbar_cam = NavigationToolbar(self.canvas_cam, self)

        self.layout.addWidget(self.toolbar_cam)
        self.layout.addWidget(self.canvas_cam)


    def display_input_beam_phase(self, phase, x_range_mm, y_range_mm):
        """
        Display the phase map.
        """

        self.figure_cam.clear()

        ax = self.figure_cam.add_subplot(111)
        imshow = ax.imshow(phase, cmap='viridis', extent=[-x_range_mm/2, x_range_mm/2, -y_range_mm/2, y_range_mm/2])
        self.figure_cam.colorbar(imshow)
        # Set labels with LaTeX font.
        ax.set_xlabel(f'Position along X [mm]', fontsize=10)
        ax.set_ylabel(f'Position along Y [mm]', fontsize=10)
        ax.set_title(f'Phase Map', fontsize=12)

        self.canvas_cam.draw()


class Worker(QThread):
    finished_generate_input_beam = pyqtSignal(Field)
    finished_generate_sampling = pyqtSignal(bool)

    def __init__(self, input_beam_editor,simulation_editor,beam_shaper,logger=None):
        super().__init__()
        self.logger = logger
        self.input_beam_config = input_beam_editor.config
        self.simulation_editor = simulation_editor
        self.simulation_config = simulation_editor.config
        self.beam_shaper = beam_shaper

    def run(self):
        # Put your analysis here

        self.beam_shaper.generate_sampling(self.simulation_config,self.input_beam_config)
        self.finished_generate_sampling.emit(True)
        self.simulation_editor.update_nb_of_samples(self.beam_shaper.nb_of_samples)
        input_field = self.beam_shaper.generate_input_beam(self.input_beam_config)
        self.finished_generate_input_beam.emit(input_field)



class InputBeamWidget(QWidget):
    def __init__(self, beam_shaper, infos_editor,simulation_editor,input_beam_editor,logger=None):
        super().__init__()

        self.logger = logger

        # Create the dimensioning configuration editor
        self.beam_shaper = beam_shaper
        self.infos_editor = infos_editor
        self.simulation_editor = simulation_editor
        self.input_beam_editor = input_beam_editor

        # Create the result display widget (tab widget in this case)
        self.result_display_widget = QTabWidget()

        # Create the result displays and store them as attributes
        self.input_beam_intensity_display = InputBeamIntensityDisplay()
        self.input_beam_phase_display = InputBeamPhaseDisplay()

        # Add the result displays to the tab widget
        self.result_display_widget.addTab(self.input_beam_intensity_display, "Input Beam Intensity")
        self.result_display_widget.addTab(self.input_beam_phase_display, "Input Beam Phase")

        # Create the run button
        self.run_button = QPushButton('Generate Input Beam')
        # self.run_button.setStyleSheet('QPushButton {background-color: gray; color: white;}')        # Connect the button to the run_dimensioning method
        self.run_button.clicked.connect(self.run_beam_generation)

        self.save_input_beam_button = QPushButton("Save Intensity and Phase")
        self.save_input_beam_button.setDisabled(True)
        self.save_input_beam_button.clicked.connect(self.on_input_beam_saved)


        self.downsampling_horizontal_layout = QHBoxLayout()
        # Create checkbox for downsampling
        self.downsampling_checkbox = QCheckBox("Downsample for display")
        self.downsampling_checkbox.setChecked(True)

        # Create a QLineEdit for downsampling factor
        self.downsampling_factor_edit = QLineEdit()
        self.downsampling_factor_edit.setText("4")
        self.downsampling_factor_edit.setDisabled(True)
        # Enable/Disable QLineEdit depending on the state of the checkbox
        self.downsampling_checkbox.stateChanged.connect(self.enable_disable_factor_edit)

        self.downsampling_horizontal_layout.addWidget(self.downsampling_checkbox)
        self.downsampling_horizontal_layout.addWidget(self.downsampling_factor_edit)

        # Create a group box for the run button
        self.run_button_group_box = QGroupBox()
        run_button_group_layout = QVBoxLayout()
        run_button_group_layout.addWidget(self.run_button)
        run_button_group_layout.addWidget(self.save_input_beam_button)
        # Add the checkbox and QLineEdit to the layout
        run_button_group_layout.addLayout(self.downsampling_horizontal_layout)
        run_button_group_layout.addWidget(self.result_display_widget)
        self.run_button_group_box.setLayout(run_button_group_layout)
        # Create a QVBoxLayout for the editors
        self.editor_layout = QVBoxLayout()
        self.editor_layout.addWidget(self.infos_editor)
        self.editor_layout.addWidget(self.simulation_editor)
        self.editor_layout.addWidget(self.input_beam_editor)


        # Create a QHBoxLayout for the whole widget
        self.layout = QHBoxLayout()
        self.layout.addLayout(self.editor_layout)  # Add the editor layout
        self.layout.addWidget(self.run_button_group_box)
        self.layout.setStretchFactor(self.run_button_group_box, 1)
        self.layout.setStretchFactor(self.result_display_widget, 2)

        # Set the layout on the widget
        self.setLayout(self.layout)

    def on_input_beam_saved(self):
        # self.result_directory = initialize_directory(self.infos_editor.config)
        self.simulation_name = self.infos_editor.config['simulation name']
        self.results_directory = self.infos_editor.config['results directory']
        results_directory = os.path.join(self.results_directory, self.simulation_name)

        save_input_beam(results_directory, self.beam_shaper, self.last_generated_beam_field)

        self.save_input_beam_button.setDisabled(True)

    def enable_disable_factor_edit(self, state):
        if state == Qt.Checked:
            self.downsampling_factor_edit.setDisabled(False)
        else:
            self.downsampling_factor_edit.setDisabled(True)

    def run_beam_generation(self):
        # Get the configs from the editors
        self.logger.info( "=" * 30)
        self.logger.info("  Input Field Generation")
        self.logger.info("=" * 30 )
        self.logger.info("  Step 1: Updating input beam config... ✔")
        self.input_beam_editor.get_config()
        self.logger.info("  Step 2: Updating simulation config... ✔")
        self.simulation_editor.get_config()

        # Create the worker and connect the signals
        self.worker = Worker(self.input_beam_editor, self.simulation_editor, self.beam_shaper,self.logger)
        self.worker.finished_generate_sampling.connect(self.state_beam_shaper_sampling_generated)
        self.worker.finished_generate_input_beam.connect(self.display_input_beam_intensity)
        self.worker.finished_generate_input_beam.connect(self.display_input_beam_phase)
        self.worker.start()

    @pyqtSlot(bool)
    def state_beam_shaper_sampling_generated(self, state):
        if state:
            self.logger.info("  Step 3: Beam shaper - generating input & fourier fields sampling... ✔")


    @pyqtSlot(Field)
    def display_input_beam_intensity(self, input_beam):
        self.logger.info("  Step 4: Beam shaper - LightPipes - generating input field arrays ... ✔")

        self.save_input_beam_button.setDisabled(False)
        self.last_generated_beam_field = input_beam

        # Check if downsampling is enabled and get the factor
        if self.downsampling_checkbox.isChecked():
            downsample_factor = int(self.downsampling_factor_edit.text())
            intensity_input_beam = downsample(Intensity(input_beam), downsample_factor)
        else:
            intensity_input_beam = Intensity(input_beam)

        self.input_beam_intensity_display.display_input_beam_intensity(intensity_input_beam, self.simulation_editor.config['grid size'], self.simulation_editor.config['grid size'])

    @pyqtSlot(Field)
    def display_input_beam_phase(self, input_beam):


        # Check if downsampling is enabled and get the factor
        if self.downsampling_checkbox.isChecked():
            downsample_factor = int(self.downsampling_factor_edit.text())
            phase_input_beam = downsample(Phase(input_beam), downsample_factor)
        else:
            phase_input_beam = Phase(input_beam)

        self.input_beam_phase_display.display_input_beam_phase(phase_input_beam, self.simulation_editor.config['grid size'], self.simulation_editor.config['grid size'])

    def load_simulation_config(self, file_name):
        with open(file_name, 'r') as file:
            return yaml.safe_load(file)
