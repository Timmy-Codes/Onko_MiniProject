import numpy as np
import pydicom
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QGridLayout,
    QGroupBox,
    QDialog,
    QMessageBox,
)
from PySide6.QtGui import QPixmap, QImage
from PIL import Image
import os
from pydicom import errors


def dicom_image_opener(ds: pydicom.Dataset)-> QImage:
    """Returns an image to be displayed by PySide6"""
    pixels = ds.pixel_array
    pixels = pixels.astype(np.float32)
    pixels -= pixels.min()
    max_value = pixels.max()

    if max_value != 0:
        pixels /= max_value

    pixels *= 255
    pixels = pixels.astype(np.uint8)
    display_image = Image.fromarray(pixels)

    return QImage(display_image.tobytes(), display_image.width, display_image.height, QImage.Format.Format_Grayscale8)

class UserInterface(QDialog):
    """The class that contains the UI"""
    def __init__(self, database):
        super().__init__()
        self.database = database

        # create widgets and set layouts for user interface
        self.setWindowTitle("Mini Project UI")
        self.path = ""
        self.layout = QGridLayout()
        self.grid_group_box = QGroupBox("Patient Information")
        self.button = QPushButton("Open New File")
        self.path_label = QLabel("Path: ")
        self.text = QLabel()
        self.fname_label = QLabel("First Name:")
        self.lname_label = QLabel("Last Name:")
        self.fname = QLabel("First Name")
        self.lname = QLabel("Last Name")
        self.dob_label = QLabel("Date Of Birth:")
        self.dob = QLabel("Date Of Birth: ")
        self.patient_id_label = QLabel("patient ID:")
        self.patient_id = QLabel("Patient ID")
        self.sex_label = QLabel("Sex:")
        self.sex = QLabel("M/F")
        self.modality_label = QLabel("Modality:")
        self.modality = QLabel("Modality")

        self.layout.addWidget(self.path_label, 0, 0)
        self.layout.addWidget(self.text, 0, 1, 1, 4)
        self.layout.addWidget(self.fname_label, 1, 0)
        self.layout.addWidget(self.lname_label, 2, 0)
        self.layout.addWidget(self.dob_label, 3, 0)
        self.layout.addWidget(self.sex_label, 1, 3)
        self.layout.addWidget(self.patient_id_label, 2, 3)
        self.layout.addWidget(self.modality_label, 3, 3)
        self.layout.addWidget(self.fname, 1, 1)
        self.layout.addWidget(self.lname, 2, 1)
        self.layout.addWidget(self.dob, 3, 1)
        self.layout.addWidget(self.sex, 1, 4)
        self.layout.addWidget(self.patient_id, 2, 4)
        self.layout.addWidget(self.modality, 3, 4)
        self.layout.addWidget(self.button, 5, 4)
        self.layout.setColumnStretch(1, 20)
        self.grid_group_box.setLayout(self.layout)

        self.main_layout = QVBoxLayout()
        self.image_label = QLabel("No Image to Display")
        self.main_layout.addWidget(self.grid_group_box)
        self.main_layout.addWidget(self.image_label)
        self.setLayout(self.main_layout)

        # signal and slot for "Open New File" button
        self.button.clicked.connect(self.add_directory)

        # checks for last file opened
        self.get_default_directory()

    #popup to allow the user to open a directory checks if the user want to open or close the program
    def select_file_to_open(self):
        """Popup to allow the user to select a directory"""
        pop_up = QMessageBox()
        pop_up.setIcon(QMessageBox.Question)
        pop_up.setText("Please Select A DICOM File to Open")
        pop_up.setStandardButtons(QMessageBox.Close | QMessageBox.Open)
        anw = pop_up.exec()

        if anw == QMessageBox.Close:
            QApplication.exit()
        elif anw == QMessageBox.Open:
            self.add_directory()

    def file_cannot_be_opened_error(self, error):
        """Displays the file error open button"""
        error_message = QMessageBox()
        error_message.setIcon(QMessageBox.Warning)
        error_message.setText(f"File can not be opened: {error}")
        error_message.exec()


    def add_directory(self):
        """Function for the button click to select and open a .dcm file"""
        db_file_path = QFileDialog.getOpenFileName(self, "Select DICOM File",
                                                            filter="DICOM Files (*.dcm)")[0]
        # conditional handle user cancel
        if db_file_path != "":
            self.path = db_file_path
            self.open_dicom_file()

    #This also needs to be changed to reflect the MySQL
    def get_default_directory(self):
        """Checks if the file in the directory has been created"""
        if os.path.exists(self.database.db_file_path):
            # get the default directory
            default_dir = self.database.get_default_directory()
            if default_dir is not None:
                self.path = default_dir
                self.open_dicom_file()
        else:
            self.text.setText("Please open a DICOM file")
            self.select_file_to_open()

    def update_default_directory(self):
        """Saves the directory path to the database file"""
        self.database.update_default_directory(self.path)

    #opens the dicom file and sets all the data for the patient like DOB Sex ect
    def set_label(self, ds, field, label, default):
        """Function to use to set the labels for PatientID, dob, ID, modality"""
        value = ds.get(field, None)
        label.setText(str(value) if value else default)

    def set_patient_name(self,  ds, fname_label, lname_label):
        """Helper Function to set the labels of lname and fname"""
        if "PatientName" in ds:
            given = getattr(ds.PatientName, "given_name", None) or "No Name Available"
            family = getattr(ds.PatientName, "family_name", None) or "No Name Available"
        else:
            given,family = "No Name Available", "No Name Available"
        fname_label.setText(given)
        lname_label.setText(family)

    def open_dicom_file(self):
        """Opens a DICOM file and displays the image linked to that file, if available"""
        try:
            ds = pydicom.dcmread(self.path)
            self.update_default_directory()
        except (errors.InvalidDicomError, FileNotFoundError) as e:
            self.file_cannot_be_opened_error(e)
        except Exception as e:
            self.file_cannot_be_opened_error(e)

        self.text.setText(self.path)

        # Check for pixel data, and display it if available
        if 'PixelData' in ds:
            image = dicom_image_opener(ds)
            pixmap = QPixmap.fromImage(image)
            self.image_label.setPixmap(pixmap)
            self.image_label.setMinimumWidth(500)
            self.image_label.setScaledContents(True)
        else:
            self.image_label.setText("No Image Data Found")

        #A number of checks to see if there is data available to fill in
        self.set_patient_name(ds, self.fname, self.lname)
        self.set_label(ds, "PatientID", self.patient_id, "No ID Available")
        self.set_label(ds, "Modality", self.modality, "Modality Unknown")
        self.set_label(ds, "PatientSex", self.sex, "Sex Unknown")
        self.set_label(ds, "PatientBirthDate", self.dob, "DOB Unknown")
