from PyQt5.QtWidgets import (QGroupBox, QHBoxLayout, QScrollArea, QCheckBox,
                             QWidget, QFormLayout, QComboBox,QPushButton, QLineEdit, QFileDialog,QMessageBox)
from PyQt5.QtCore import Qt,pyqtSignal, pyqtSlot,QThread
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QTabWidget, QVBoxLayout, QWidget

import numpy as np
from LightPipes import mm, Field, Intensity, Phase
import os
import re
from beamshapy_gui.utils import save_target_amplitude, save_inverse_fourier_field,normalize, discretize_array, translate
import numpy as np
import matplotlib as plt

class DisplayInverseFourierTargetField(QWidget):
    def __init__(self):
        super().__init__()

        # Create a tab widget to hold the plots
        self.tabWidget = QTabWidget(self)

        # Create figures and figure canvases for the plots
        self.IntensityFigure = Figure()
        self.IntensityCanvas = FigureCanvas(self.IntensityFigure)
        self.IntensityToolbar = NavigationToolbar(self.IntensityCanvas, self)

        # Create figures and figure canvases for the plots
        self.PhaseFigure = Figure()
        self.PhaseCanvas= FigureCanvas(self.PhaseFigure)
        self.PhaseToolbar = NavigationToolbar(self.PhaseCanvas, self)

        # Create figures and figure canvases for the plots
        self.ComparisonInputFieldFigure = Figure()
        self.ComparisonInputFieldCanvas = FigureCanvas(self.ComparisonInputFieldFigure)
        self.ComparisonInputFieldToolbar = NavigationToolbar(self.ComparisonInputFieldCanvas, self)


        # Create Widgets for each tab to hold the toolbar and the figure canvas
        self.IntensityWidget = QWidget()
        self.IntensityLayout = QVBoxLayout(self.IntensityWidget)
        self.IntensityLayout.addWidget(self.IntensityToolbar)
        self.IntensityLayout.addWidget(self.IntensityCanvas)

        # Create Widgets for each tab to hold the toolbar and the figure canvas
        self.PhaseWidget = QWidget()
        self.PhaseLayout = QVBoxLayout(self.PhaseWidget)
        self.PhaseLayout.addWidget(self.PhaseToolbar)
        self.PhaseLayout.addWidget(self.PhaseCanvas)

        # Create Widgets for each tab to hold the toolbar and the figure canvas
        self.ComparisonInputFieldWidget = QWidget()
        self.ComparisonInputFieldLayout = QVBoxLayout(self.ComparisonInputFieldWidget)
        self.ComparisonInputFieldLayout.addWidget(self.ComparisonInputFieldToolbar)
        self.ComparisonInputFieldLayout.addWidget(self.ComparisonInputFieldCanvas)


        # Add the Widgets to the tab widget
        self.tabWidget.addTab(self.IntensityWidget, "Intensity Map")
        self.tabWidget.addTab(self.PhaseWidget, "Phase Map")
        self.tabWidget.addTab(self.ComparisonInputFieldWidget, "Comparison Input Field")

        # Create a QVBoxLayout and add the tab widget to it
        layout = QVBoxLayout(self)
        layout.addWidget(self.tabWidget)

    def display_fourier_transform_target_field(self, x_array, field,input_field):
        # Plot the mask
        self.x_array_in = x_array/mm

        intensity_field = Intensity(field)
        self.IntensityFigure.clear()
        ax1 = self.IntensityFigure.add_subplot(111)
        im = ax1.imshow(intensity_field,extent=[self.x_array_in[0],self.x_array_in[-1], self.x_array_in[0],self.x_array_in[-1]])
        ax1.set_title('Target Intensity Map')
        ax1.set_xlabel('Position along X [in mm]')
        ax1.set_ylabel('Position along Y [in mm]')
        self.IntensityFigure.colorbar(im, ax=ax1,label='Intensity values [no units]')
        self.IntensityCanvas.draw()

        phase_field = Phase(field)
        self.PhaseFigure.clear()
        ax1 = self.PhaseFigure.add_subplot(111)
        im = ax1.imshow(phase_field,extent=[self.x_array_in[0],self.x_array_in[-1], self.x_array_in[0],self.x_array_in[-1]])
        ax1.set_title('Target Phase Map')
        ax1.set_xlabel('Position along X [in mm]')
        ax1.set_ylabel('Position along Y [in mm]')
        self.PhaseFigure.colorbar(im, ax=ax1,label='Phase values [in rad]')
        self.PhaseCanvas.draw()

        intensity_target_field = intensity_field
        intensity_input_field =Intensity(input_field)
        self.ComparisonInputFieldFigure.clear()
        ax1 = self.ComparisonInputFieldFigure.add_subplot(111)
        ax1.plot(self.x_array_in, intensity_target_field[intensity_target_field.shape[0]//2,:],label='Intensity Target')
        ax1.plot(self.x_array_in, intensity_input_field[intensity_input_field.shape[0]//2,:],label='Intensity Input')
        ax1.set_title('Comparison of Target and Input Intensity Field')
        ax1.set_xlabel('Position along X [in mm]')
        ax1.set_ylabel('Intensity values [no units]')
        ax1.legend()
        self.ComparisonInputFieldCanvas.draw()




class Worker(QThread):
    finished_calculation_inverse_fourier_transform = pyqtSignal(np.ndarray,Field,Field)

    def __init__(self,beam_shaper,complex_amplitude,logger):
        super().__init__()
        self.logger = logger
        self.beam_shaper = beam_shaper
        self.complex_amplitude = complex_amplitude

    def run(self):


        input_field = self.beam_shaper.input_beam
        inverse_fourier_target_field = self.beam_shaper.inverse_fourier_transform(self.complex_amplitude)

        inverse_fourier_target_field = self.beam_shaper. normalize_field_power(inverse_fourier_target_field,norm_value=self.beam_shaper.input_power)

        self.finished_calculation_inverse_fourier_transform.emit(self.beam_shaper.x_array_in,inverse_fourier_target_field,input_field)




class TargetAmplitudeParamsWidget(QWidget):

    target_amplitudeGenerated = pyqtSignal(np.ndarray,np.ndarray)
    def __init__(self,beam_shaper,target_amplitude_number):
        super().__init__()

        self.beam_shaper = beam_shaper
        self.target_amplitude_number = target_amplitude_number
        self.group_box = QGroupBox(f"A{target_amplitude_number}")
        self.inner_layout = QFormLayout(self.group_box)

        self.target_amplitude_type_selector = QComboBox()
        self.target_amplitude_type_selector.addItem("None")
        self.target_amplitude_type_selector.addItem("Rectangle")
        self.target_amplitude_type_selector.addItem("Wedge")
        self.target_amplitude_type_selector.addItem("Sinus")
        self.target_amplitude_type_selector.addItem("Cosinus")
        self.target_amplitude_type_selector.addItem("Custom h5 Amplitude")
        self.target_amplitude_type_selector.currentIndexChanged.connect(self.update_target_amplitude_params)



        self.inner_layout.addRow("Amplitude Type", self.target_amplitude_type_selector)

        self.generate_target_amplitude_button = QPushButton("Generate")
        self.generate_target_amplitude_button.clicked.connect(self.generate_target_amplitude)



        self.inner_layout.addRow(self.generate_target_amplitude_button)



        self.normalize_layout = QVBoxLayout()
        self.normalize_checkbox = QCheckBox("Normalize")
        self.normalize_checkbox.stateChanged.connect(self.handle_normalize_checked)
        self.normalize_layout.addWidget(self.normalize_checkbox)

        self.min_value_input = QLineEdit("0")
        self.min_group = QGroupBox("Min Value")
        self.min_group.setLayout(QHBoxLayout())
        self.min_group.layout().addWidget(self.min_value_input)
        self.normalize_layout.addWidget(self.min_group)

        self.max_value_input = QLineEdit("1")
        self.max_group = QGroupBox("Max Value")
        self.max_group.setLayout(QHBoxLayout())
        self.max_group.layout().addWidget(self.max_value_input)
        self.normalize_layout.addWidget(self.max_group)

        # Initially hide the min and max value inputs
        self.min_group.hide()
        self.max_group.hide()

        # Add normalize layout to a QWidget and then add the QWidget to the inner layout
        self.normalize_widget = QWidget()
        self.normalize_widget.setLayout(self.normalize_layout)
        self.inner_layout.addRow(self.normalize_widget)



        self.translate_layout = QVBoxLayout()
        self.translate_checkbox = QCheckBox("Translate")
        self.translate_checkbox.stateChanged.connect(self.handle_translate_checked)
        self.translate_layout.addWidget(self.translate_checkbox)

        self.translate_value = QLineEdit("0")
        self.translate_group = QGroupBox("Value")
        self.translate_group.setLayout(QHBoxLayout())
        self.translate_group.layout().addWidget(self.translate_value)
        self.translate_layout.addWidget(self.translate_group)

        # Initially hide the min and max value inputs
        self.translate_group.hide()

        # Add normalize layout to a QWidget and then add the QWidget to the inner layout
        self.translate_widget = QWidget()
        self.translate_widget.setLayout(self.translate_layout)
        self.inner_layout.addRow(self.translate_widget)





        self.layout = QVBoxLayout(self)  # This will set QVBoxLayout as the layout of this widget
        self.layout.addWidget(self.group_box)  # Now adding group_box to the QVBoxLayout

        self.group_box.setStyleSheet("""
            QGroupBox {
                border: 1px solid gray;
                border-radius: 5px;
                margin-top: 0.5em;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
        """)

    def handle_normalize_checked(self, state):
        # Show or hide the min and max value inputs based on the checkbox state
        if state == Qt.Checked:
            self.min_group.show()
            self.max_group.show()
        else:
            self.min_group.hide()
            self.max_group.hide()

    def handle_translate_checked(self, state):
        # Show or hide the min and max value inputs based on the checkbox state
        if state == Qt.Checked:
            self.translate_group.show()
        else:
            self.translate_group.hide()


    def enable_generate_target_amplitude_button(self):
        # Enable the "Generate Mask" button
        self.generate_target_amplitude_button.setEnabled(True)

    def generate_target_amplitude(self):
        # Get the mask type
        target_amplitude_type = self.target_amplitude_type_selector.currentText()

        # Generate the mask
        if target_amplitude_type == "Rectangle":
            target_amplitude = self.beam_shaper.amplitude_generator.generate_target_amplitude(amplitude_type=target_amplitude_type,
                                                                          angle = np.radians(float(self.angle.text())),
                                                                          width = float(self.width.text())*mm,
                                                                          height = float(self.height.text())*mm)
        elif target_amplitude_type == "Wedge":

            target_amplitude = self.beam_shaper.amplitude_generator.generate_target_amplitude(amplitude_type=target_amplitude_type,
                                                  position=float(self.position.text())*mm,
                                                  angle = np.radians(float(self.angle_wedge.text())))

        elif target_amplitude_type == "Sinus":

            target_amplitude = self.beam_shaper.amplitude_generator.generate_target_amplitude(amplitude_type=target_amplitude_type,
                                                                          period=float(self.period.text())*mm,
                                                                          angle = np.radians(float(self.angle.text())))

        elif target_amplitude_type == "Cosinus":

            target_amplitude = self.beam_shaper.amplitude_generator.generate_target_amplitude(amplitude_type=target_amplitude_type,
                                                                          period=float(self.period.text()) * mm,
                                                                          angle = np.radians(float(self.angle.text())))


        elif target_amplitude_type == "Custom h5 Amplitude":
            # Open a file dialog to select the mask
            file_path = self.file_path.text()
            scale_size = self.scale_size.text()
            target_amplitude = self.beam_shaper.amplitude_generator.generate_target_amplitude(amplitude_type=target_amplitude_type,
                                                                           amplitude_path=file_path,
                                                                            scale_factor=float(self.scale_size.text()))
        else :
            return

        if self.normalize_checkbox.isChecked():
            min_value = float(self.min_value_input.text())
            max_value = float(self.max_value_input.text())
            target_amplitude = normalize(target_amplitude, min_value, max_value)

        if self.translate_checkbox.isChecked():
            value = int(self.translate_value.text())
            target_amplitude = translate(target_amplitude, value)


        if target_amplitude is not None:
            self.generated_target_amplitude = target_amplitude
            self.generate_target_amplitude_button.setDisabled(True)
            self.target_amplitudeGenerated.emit(target_amplitude, self.beam_shaper.x_array_out)


    def update_target_amplitude_params(self):
        # Clear the previous parameters (if any) by removing the layout's rows, but keep the first 2 rows
        for i in range(self.inner_layout.rowCount() - 1, 3, -1):  # start from last row, stop at 2 (exclusive), step backwards
            # Remove row at index i from the layout
            self.inner_layout.removeRow(i)

        self.target_amplitude_type_selector.currentIndexChanged.connect(self.enable_generate_target_amplitude_button)
        self.translate_value.textChanged.connect(self.enable_generate_target_amplitude_button)
        # Circular Mask parameters: radius, intensity

        if self.target_amplitude_type_selector.currentText() == "Rectangle":
            self.angle = QLineEdit()
            self.angle.setText(str(0))
            self.width = QLineEdit()
            self.width.setText(str(0.2))
            self.height = QLineEdit()
            self.height.setText(str(0.3))
            self.inner_layout.addRow("angle [in °]", self.angle)
            self.inner_layout.addRow("width [in mm]", self.width)
            self.inner_layout.addRow("height [in mm]", self.height)

            # Connect the textChanged signal for these parameters
            self.width.textChanged.connect(self.enable_generate_target_amplitude_button)
            self.height.textChanged.connect(self.enable_generate_target_amplitude_button)
            self.angle.textChanged.connect(self.enable_generate_target_amplitude_button)

        elif self.target_amplitude_type_selector.currentText() == "Wedge":
            self.position = QLineEdit()
            self.position.setText(str(5))
            self.angle_wedge = QLineEdit()
            self.angle_wedge.setText(str(0))
            self.inner_layout.addRow("position [in mm]", self.position)
            self.inner_layout.addRow("angle [in °]", self.angle_wedge)

            # Connect the textChanged signal for these parameters
            self.position.textChanged.connect(self.enable_generate_target_amplitude_button)
            self.angle_wedge.textChanged.connect(self.enable_generate_target_amplitude_button)

        elif self.target_amplitude_type_selector.currentText() == "Sinus":
            self.period = QLineEdit()
            self.period.setText(str(0.5))
            self.angle = QLineEdit()
            self.angle.setText(str(0))
            self.inner_layout.addRow("period [in mm]", self.period)
            self.inner_layout.addRow("angle [in °]", self.angle)

            # Connect the textChanged signal for these parameters
            self.period.textChanged.connect(self.enable_generate_target_amplitude_button)
            self.angle.textChanged.connect(self.enable_generate_target_amplitude_button)


            # Connect the textChanged signal for these parameters
            self.period.textChanged.connect(self.enable_generate_target_amplitude_button)

        elif self.target_amplitude_type_selector.currentText() == "Cosinus":
            self.period = QLineEdit()
            self.period.setText(str(0.5))
            self.angle = QLineEdit()
            self.angle.setText(str(0))
            self.inner_layout.addRow("period [in mm]", self.period)
            self.inner_layout.addRow("angle [in °]", self.angle)

            # Connect the textChanged signal for these parameters
            self.period.textChanged.connect(self.enable_generate_target_amplitude_button)
            self.angle.textChanged.connect(self.enable_generate_target_amplitude_button)


        # Custom h5 Amplitude parameters: file path
        elif self.target_amplitude_type_selector.currentText() == "Custom h5 Amplitude":
            self.file_path = QLineEdit()
            self.scale_size = QLineEdit()
            self.scale_size.setText(str(1))

            self.browse_button = QPushButton("Browse")
            self.browse_button.clicked.connect(self.browse_file)

            self.inner_layout.addRow("File Path", self.file_path)
            self.inner_layout.addRow("", self.browse_button)
            self.inner_layout.addRow("Scale Size", self.scale_size)

            # Connect the textChanged signal for these parameters
            self.scale_size.textChanged.connect(self.enable_generate_target_amplitude_button)
            self.file_path.textChanged.connect(self.enable_generate_target_amplitude_button)
            
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select h5 file", "", "H5 Files (*.h5)")
        if file_path:
            self.file_path.setText(file_path)



class DisplayWidget(QWidget):
    def __init__(self,beam_shaper):
        super().__init__()

        self.beam_shaper = beam_shaper
        # Create a tab widget to hold the plots
        self.tabWidget = QTabWidget(self)

        # Create figures and figure canvases for the plots
        self.amplitudeFigure = Figure()
        self.target_amplitudeCanvas = FigureCanvas(self.amplitudeFigure)
        self.target_amplitudeCanvas.mpl_connect('button_press_event', self.onclick)
        self.target_amplitudeToolbar = NavigationToolbar(self.target_amplitudeCanvas, self)

        self.cutXFigure = Figure()
        self.cutXCanvas = FigureCanvas(self.cutXFigure)
        self.cutXToolbar = NavigationToolbar(self.cutXCanvas, self)

        self.cutYFigure = Figure()
        self.cutYCanvas = FigureCanvas(self.cutYFigure)
        self.cutYToolbar = NavigationToolbar(self.cutYCanvas, self)

        # Create Widgets for each tab to hold the toolbar and the figure canvas
        self.target_amplitudeWidget = QWidget()
        self.target_amplitudelayout = QVBoxLayout(self.target_amplitudeWidget)
        self.target_amplitudelayout.addWidget(self.target_amplitudeToolbar)
        self.target_amplitudelayout.addWidget(self.target_amplitudeCanvas)


        self.cutXWidget = QWidget()
        self.cutXLayout = QVBoxLayout(self.cutXWidget)
        self.cutXLayout.addWidget(self.cutXToolbar)
        self.cutXLayout.addWidget(self.cutXCanvas)

        self.cutYWidget = QWidget()
        self.cutYLayout = QVBoxLayout(self.cutYWidget)
        self.cutYLayout.addWidget(self.cutYToolbar)
        self.cutYLayout.addWidget(self.cutYCanvas)

        # Add the Widgets to the tab widget
        self.tabWidget.addTab(self.target_amplitudeWidget, "Image Map")
        self.tabWidget.addTab(self.cutXWidget, "Cut X")
        self.tabWidget.addTab(self.cutYWidget, "Cut Y")



        # Create a QVBoxLayout and add the tab widget to it

        layout = QVBoxLayout(self)

        layout.addWidget(self.tabWidget)

    @pyqtSlot(np.ndarray,np.ndarray)
    def displaytarget_amplitude(self, amplitude,x_array):
        # Plot the mask
        self.x_array_in = x_array/mm
        self.amplitude = amplitude
        self.amplitudeFigure.clear()
        ax1 = self.amplitudeFigure.add_subplot(111)
        self.vline = ax1.axvline(self.x_array_in[0], color='r')  # initial position of vertical line
        self.hline = ax1.axhline(self.x_array_in[0], color='r')  # initial position of horizontal line
        im = ax1.imshow(amplitude,extent=[self.x_array_in[0],self.x_array_in[-1], self.x_array_in[0],self.x_array_in[-1]])
        ax1.set_title('Target Amplitude Map')
        ax1.set_xlabel('Position along X [in mm]')
        ax1.set_ylabel('Position along Y [in mm]')
        self.amplitudeFigure.colorbar(im, ax=ax1,label='Amplitude values [no units]')
        self.target_amplitudeCanvas.draw()

        # Plot the cut along X
        self.cutXFigure.clear()
        ax2 = self.cutXFigure.add_subplot(111)
        self.cutXLine, = ax2.plot(self.x_array_in,amplitude[amplitude.shape[0] // 2, :])
        ax2.set_title('Cut along X')
        ax2.set_xlabel('Position along X [in mm]')
        ax2.set_ylabel('Amplitude values [no units]')
        self.cutXCanvas.draw()

        # Plot the cut along Y
        self.cutYFigure.clear()
        ax3 = self.cutYFigure.add_subplot(111)
        self.cutYLine, = ax3.plot(self.x_array_in,amplitude[:, amplitude.shape[1] // 2])
        ax3.set_title('Cut along Y')
        ax3.set_xlabel('Position along Y [in mm]')
        ax3.set_ylabel('Amplitude values [no units]')
        self.cutYCanvas.draw()

    def onclick(self, event):
        ix, iy = event.xdata, event.ydata

        # Convert click coordinates to array indices
        x_index = np.argmin(np.abs(self.x_array_in - ix))
        y_index = np.argmin(np.abs(self.x_array_in - iy))

        # Move the vertical and horizontal lines to the clicked position
        self.vline.set_xdata(ix)
        self.hline.set_ydata(iy)
        self.target_amplitudeCanvas.draw()

        # Update the cut along X plot
        self.cutXLine.set_ydata(self.amplitude[y_index, :])
        self.cutXCanvas.draw()

        # Update the cut along Y plot
        self.cutYLine.set_ydata(self.amplitude[:, x_index])
        self.cutYCanvas.draw()


class TargetFieldDesignWidget(QWidget):
    def __init__(self, beam_shaper, infos_editor, simulation_editor, target_target_amplitude_config_path=None,logger=None):

        super().__init__()

        self.logger = logger

        self.beam_shaper = beam_shaper
        self.infos_editor = infos_editor
        self.simulation_editor = simulation_editor
        self.target_target_amplitude_config_path = target_target_amplitude_config_path
        self.result_tab_index = None

        # Create the result display widget (tab widget in this case)
        self.result_display_widget = QTabWidget()

        # Create a QVBoxLayout for the left side (mask parameters and buttons)
        self.left_layout = QVBoxLayout()
        self.left_layout_target_amplitudes = QVBoxLayout()

        self.new_target_amplitude_button = QPushButton("Add Amplitude")
        self.new_target_amplitude_button.clicked.connect(self.new_target_amplitude)
        self.left_layout_target_amplitudes.addWidget(self.new_target_amplitude_button)

        self.delete_target_amplitude_button = QPushButton("Delete Last Amplitude")
        self.delete_target_amplitude_button.clicked.connect(self.delete_target_amplitude)
        self.left_layout_target_amplitudes.addWidget(self.delete_target_amplitude_button)

        # Create QLineEdit for user input
        self.operation_input = QLineEdit(self)
        self.operation_input.setPlaceholderText("ex: wrap ( A1 + A2 ) * A3")

        self.discretize_checkbox = QCheckBox("Discretize")

        # Add a button to evaluate the user input
        self.evaluate_button = QPushButton("Generate Target Amplitude", self)
        self.evaluate_button.clicked.connect(self.evaluate_operation)

        self.inverse_transform_button = QPushButton("Inverse Fourier Transform", self)
        self.inverse_transform_button.clicked.connect(self.run_inverse_fourier_transform)
        self.is_resulting_amplitude_exist = False

        self.save_target_amplitude_button = QPushButton("Save Target Amplitude in Fourier plane")
        self.save_target_amplitude_button.setDisabled(True)
        self.save_target_amplitude_button.clicked.connect(self.on_resulting_target_amplitude_save)

        self.save_inverse_fourier_transform_button = QPushButton("Save Inverse Fourier Transform Amplitude in SLM plane")
        self.save_inverse_fourier_transform_button.setDisabled(True)
        self.save_inverse_fourier_transform_button.clicked.connect(self.on_resulting_inverse_fourier_amplitude_save)


        # List to store references to the mask widgets
        self.target_amplitude_params_widgets = []

        # List to store references to the masks data
        self.target_amplitudes_dict = dict()

        self.target_amplitude_area = QScrollArea()
        self.target_amplitude_area.setWidgetResizable(True)
        self.target_amplitude_layout = QVBoxLayout()
        self.target_amplitude_area_widget = QWidget()
        self.target_amplitude_area_widget.setLayout(self.target_amplitude_layout)
        self.target_amplitude_area.setWidget(self.target_amplitude_area_widget)
        self.target_amplitude_area.setStyleSheet("QScrollArea { border: none; }")
        self.left_layout_target_amplitudes.addWidget(self.target_amplitude_area)

        # Create a QVBoxLayout for the operation input and button
        self.group_box = QGroupBox(f"Operations on target_amplitudes")
        self.operation_layout = QFormLayout(self.group_box)

        self.operation_layout.addRow(self.operation_input)
        self.operation_layout.addRow(self.discretize_checkbox)
        self.operation_layout.addRow(self.evaluate_button)
        self.operation_layout.addRow(self.inverse_transform_button)

        self.left_layout_target_amplitudes.addWidget(self.group_box)

        # Create a QVBoxLayout for the save button and result display
        self.result_layout = QVBoxLayout()
        self.result_layout.addWidget(self.save_target_amplitude_button)
        self.result_layout.addWidget(self.save_inverse_fourier_transform_button)
        self.result_layout.addWidget(self.result_display_widget)

        # Create a QHBoxLayout for the whole widget
        self.layout = QHBoxLayout(self)
        self.layout.addLayout(self.left_layout_target_amplitudes)  # Add the left layout (mask parameters and buttons)
        self.layout.addLayout(self.result_layout)  # Add the save button and result display layout



        self.group_box.setStyleSheet("""
            QGroupBox {
                border: 1px solid;
                border-radius: 7px;
                margin-top: 0.5em;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
        """)

        self.layout.setStretchFactor(self.left_layout_target_amplitudes, 1)
        self.layout.setStretchFactor(self.result_layout, 2)



    def on_resulting_target_amplitude_save(self):
        # self.result_directory = initialize_directory(self.infos_editor.config)
        self.simulation_name = self.infos_editor.config['simulation name']
        self.results_directory = self.infos_editor.config['results directory']
        results_directory = os.path.join(self.results_directory, self.simulation_name)
        # Save the resulting mask
        save_target_amplitude(self.result_target_amplitude, results_directory)

        self.logger.info(f"...Target Amplitude saved in {results_directory}")
        self.save_target_amplitude_button.setDisabled(True)

    def on_resulting_inverse_fourier_amplitude_save(self):
        self.simulation_name = self.infos_editor.config['simulation name']
        self.results_directory = self.infos_editor.config['results directory']
        results_directory = os.path.join(self.results_directory, self.simulation_name)
        # Save the resulting mask
        save_inverse_fourier_field(self.beam_shaper,self.inverse_fourier_transform, results_directory)

        self.logger.info(f"...Inverse Fourier Transform Amplitude saved in {results_directory}")
        self.save_inverse_fourier_transform_button.setDisabled(True)

    def run_inverse_fourier_transform(self):

        self.logger.info( "=" * 30)
        self.logger.info("  Inverse Fourier Transform of the target Field")
        self.logger.info("=" * 30 )

        try:
            self.beam_shaper.input_beam
        except :
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("No Input Field Detected")
            msg.setInformativeText("Please create an input field before propagating.")
            msg.setWindowTitle("Error")
            msg.exec_()
            return

        try:
            self.result_target_amplitude
        except :
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("No Target Amplitude Detected")
            msg.setInformativeText("Please create a Target Amplitude before propagating.")
            msg.setWindowTitle("Error")
            msg.exec_()
            return

        self.save_inverse_fourier_transform_button.setDisabled(False)

        self.worker = Worker(self.beam_shaper, self.result_target_amplitude,self.logger)
        self.worker.finished_calculation_inverse_fourier_transform.connect(self.display_inverse_fourier_transform)
        self.worker.start()


    def evaluate_operation(self):



        self.logger.info( "=" * 30)
        self.logger.info("  Generate Target Amplitude")
        self.logger.info("=" * 30 )
        # Get the operation from the QLineEdit
        operation = self.operation_input.text()

        try:
            self.target_amplitudes_dict["A1"]
        except :
            self.logger.info("  Evaluate Operation : No Target Amplitude Detected ..✘")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("No Target Amplitude Detected")
            msg.setInformativeText("Please create a Target Amplitude before propagating.")
            return

        # Define the allowed operations and amplitudes
        allowed_ops = {"+", "-", "*", "/", "(", ")", "wrap"}  # Add your custom operation name here
        allowed_target_amplitudes = set(self.target_amplitudes_dict.keys())  # Dynamically get the list of current amplitudes

        # Custom operations dictionary
        operations = {
            "wrap": lambda x: np.angle(np.exp(1j * x))  # define your wrap function here
        }

        # Define the regex pattern to split operation into parts
        pattern = f"({'|'.join(re.escape(op) for op in allowed_ops)}|{'|'.join(re.escape(amplitude) for amplitude in allowed_target_amplitudes)}|[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?|\w+)"

        # Split the operation into parts using regex
        parts = re.findall(pattern, operation)

        # Check each part of the operation
        for part in parts:
            if part not in allowed_ops and part not in allowed_target_amplitudes:
                try:
                    # If the part can be converted to a float, it's a number and valid
                    float(part)
                except ValueError:
                    # If it can't be converted to a float, it's invalid
                    self.logger.error(f"  Evaluate Operation : Invalid operation: {part}")
                    return

        # Replace mask names with their numpy array representation
        for target_amplitude_name in allowed_target_amplitudes:
            operation = operation.replace(target_amplitude_name, f"self.target_amplitudes_dict['{target_amplitude_name}']")

        # Replace custom operation names with their callable function string representation
        for op_name in operations:
            operation = operation.replace(op_name, f"operations['{op_name}']")

        try :
            self.result_target_amplitude
            if len(self.result_display_widget) == len(self.target_amplitude_params_widgets)+1:
                self.result_display_widget.removeTab(self.result_display_widget.count()-1)
            if len(self.result_display_widget) == len(self.target_amplitude_params_widgets)+2:
                self.result_display_widget.removeTab(self.result_display_widget.count() - 1)
                self.result_display_widget.removeTab(self.result_display_widget.count() - 1)
        except:
            self.logger.info("  Evaluate Operation : No Target Amplitude Detected ..✘")
            pass

        # Initialize the resulting mask as an empty mask
        self.result_target_amplitude = np.zeros_like(next(iter(self.target_amplitudes_dict.values())))

        print(self.target_amplitudes_dict)

        # Evaluate the operation
        if operation != "":
            try:
                self.result_target_amplitude = eval(operation)
                self.beam_shaper.target_amplitude = self.result_target_amplitude
            except Exception as e:
                self.logger.error(f"  Evaluate Operation : Invalid operation: {e} ..✘")
                return

        if operation == "" and len(self.target_amplitudes_dict) >0:
            self.result_target_amplitude = self.target_amplitudes_dict["A1"]
            self.beam_shaper.target_amplitude = self.result_target_amplitude

        if self.discretize_checkbox.isChecked():
            self.result_target_amplitude = discretize_array(self.result_target_amplitude)
            self.beam_shaper.target_amplitude = self.result_target_amplitude

        # Create a new widget for the display
        result_display = DisplayWidget(self.beam_shaper)  # replace with your actual Display Widget here
        result_display.displaytarget_amplitude(self.result_target_amplitude,self.beam_shaper.x_array_out)  # Display the result mask
        # Add the result display as a new tab to the result_display_widget and store its index

        self.result_tab_index = self.result_display_widget.addTab(result_display, "Resulting Amplitude")


        self.target_amplitudes_dict[
            f"resulting_A"] = self.result_target_amplitude

        self.save_target_amplitude_button.setDisabled(False)

        self.is_resulting_amplitude_exist = True

        self.logger.info(" ... evaluation of the operation on target amplitudes  : target amplitude generation  ✔")

    @pyqtSlot(np.ndarray, int)
    def update_target_amplitudes_dict(self, target_amplitude, target_amplitude_number):
        self.target_amplitudes_dict[f"A{target_amplitude_number}"] = target_amplitude


    @pyqtSlot(np.ndarray, Field, Field)
    def display_inverse_fourier_transform(self, x_array_in,inverse_fourier_transform,input_field):

        self.logger.info("  Step 1: generation of the inverse fourier transform... ✔")
        self.logger.info("  Step 2: normalize the inverse fourier transform by max input field intensity value... ✔")

        # Create a new widget for the display
        inverse_fourier_transform_display = DisplayInverseFourierTargetField()
        inverse_fourier_transform_display.display_fourier_transform_target_field(x_array_in,inverse_fourier_transform,input_field)

        # Add the new display as a new tab to the result_display_widget
        #
        # print(len(self.target_amplitude_params_widgets),len(self.result_display_widget))
        if len(self.target_amplitude_params_widgets) == len(self.result_display_widget)  - 1:
            self.result_display_widget.addTab(inverse_fourier_transform_display, f"Inverse Fourier Transform")
        self.inverse_fourier_transform = inverse_fourier_transform

    def new_target_amplitude(self):
        target_amplitude_number = len(self.target_amplitude_params_widgets) + 1

        new_target_amplitude_params_widget = TargetAmplitudeParamsWidget(self.beam_shaper,target_amplitude_number)

        self.target_amplitude_params_widgets.append(new_target_amplitude_params_widget)
        self.target_amplitude_layout.addWidget(new_target_amplitude_params_widget)

        # Create a new widget for the display
        new_target_amplitude_display = DisplayWidget(self.beam_shaper)  # replace with your actual Display Widget here

        # Connect the target_amplitudeGenerated signal to the displaytarget_amplitude slot
        new_target_amplitude_params_widget.target_amplitudeGenerated.connect(new_target_amplitude_display.displaytarget_amplitude)
        new_target_amplitude_params_widget.target_amplitudeGenerated.connect(lambda target_amplitude: self.update_target_amplitudes_dict(target_amplitude, new_target_amplitude_params_widget.target_amplitude_number))

        # Add the new display as a new tab to the result_display_widget
        if len(self.target_amplitude_params_widgets) == len(self.result_display_widget) +1:
            self.result_display_widget.addTab(new_target_amplitude_display, f"Amplitude {target_amplitude_number} Display")
        elif len(self.target_amplitude_params_widgets) < len(self.result_display_widget) +1:
            self.result_display_widget.insertTab(self.result_display_widget.count()-1,new_target_amplitude_display, f"Amplitude {target_amplitude_number} Display")

        # Add the new mask to the dictionary of masks
        self.target_amplitudes_dict[
            f"A{target_amplitude_number}"] = ""

    def delete_target_amplitude(self):
        if self.target_amplitude_params_widgets:


            # Remove the last mask from the dictionary of masks
            target_amplitude_number = len(self.target_amplitude_params_widgets)

            try:
                self.inverse_fourier_transform
                del self.target_amplitudes_dict[f"A{target_amplitude_number}"]
                amplitude_to_remove = self.target_amplitude_params_widgets.pop()
                self.target_amplitude_layout.removeWidget(amplitude_to_remove)
                amplitude_to_remove.deleteLater()
                # Remove the last tab from result_display_widget
                self.result_display_widget.removeTab(self.result_display_widget.count() - 3)

                if len(self.target_amplitude_params_widgets) == 0:
                    self.result_display_widget.removeTab(self.result_display_widget.count() - 1)
                    self.result_display_widget.removeTab(self.result_display_widget.count() - 1)
                    del self.target_amplitudes_dict["resulting_A"]

            except :
        
                try :
                    self.target_amplitudes_dict["resulting_A"]
                    del self.target_amplitudes_dict[f"A{target_amplitude_number}"]
                    amplitude_to_remove = self.target_amplitude_params_widgets.pop()
                    self.target_amplitude_layout.removeWidget(amplitude_to_remove)
                    amplitude_to_remove.deleteLater()
                    # Remove the last tab from result_display_widget
                    self.result_display_widget.removeTab(self.result_display_widget.count() - 2)
    
                    if len(self.target_amplitude_params_widgets)==0:
                        self.result_display_widget.removeTab(self.result_display_widget.count() - 1)
                        del self.target_amplitudes_dict["resulting_A"]
    
                except KeyError:
                    del self.target_amplitudes_dict[f"A{target_amplitude_number}"]
                    # Remove the last mask widget from the target_amplitude_layout and the list
                    amplitude_to_remove = self.target_amplitude_params_widgets.pop()
                    self.target_amplitude_layout.removeWidget(amplitude_to_remove)
                    amplitude_to_remove.deleteLater()
                    # Remove the last tab from result_display_widget
                    self.result_display_widget.removeTab(self.result_display_widget.count() - 1)




