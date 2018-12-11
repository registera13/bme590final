import sys
from GUI.validation_functions import valid_email, validate_file_exists
from PyQt5 import QtWidgets
from GUI.main_window_design import Ui_MainWindow
from GUI.files_dialog import LoadDialog, SaveDialog
from GUI.view_images import run_image_viewer
from ClientFunctions.read_files import load_image_series
from ClientFunctions.write_files import save_images
from GUI.utils import save_email, load_email


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):

        super(MainWindow, self).__init__()

        # Set up main window
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Set up self fields
        self.save_dialog = ''
        self.load_dialog = ''

        # Callback for changing image selection via the ComboBox
        self.ui.comboBox.currentIndexChanged.connect(self.pullcombotext)

        # Callbacks for button presses
        self.ui.pushButtonApply.clicked.connect(self.apply_clicked)
        self.ui.pushButtonDonwload.clicked.connect(self.download_clicked)
        self.ui.toolButtonLoad.clicked.connect(self.load_image_dialog)
        self.ui.pushButtonEmail.clicked.connect(self.validate_email)
        self.ui.pushButtonImageViewer.clicked.connect(self.image_viewer)

        # Gray out options before loading a file
        self.process_flag = False
        self.save_flag = False
        self.load_flag = False
        self.disable_options()

        # Initialize dictionary for saving user inputs
        self.df = {}

        # Load previous data
        self.preload_email()

    def preload_email(self):
        """If a previous email has been used, upload it to the GUI and allow
        the user to access more options.

        Returns:

        """

        email = load_email()
        if email:
            # Update dictionary
            self.df['email'] = email

            # Update GUI field
            self.ui.lineEditEmail.setText(email)

            # Allow the user to access other options
            self.load_flag = True

            self.disable_options()

    def validate_email(self):
        """Determines that the input email address is valid (eg. is of the
        format '*@*.*')

        Returns:

        """

        # Get input email address from image path
        email = self.ui.lineEditEmail.text()

        # Validate the email address
        if valid_email(email):

            # Add email to the dictionary
            self.df['email'] = self.ui.lineEditEmail.text()
            print(self.df)

            # Update disabled options
            self.load_flag = True

            # Save valid email for future use
            save_email(self.df['email'])

        else:

            # Show error message
            error_dialog = QtWidgets.QErrorMessage(self)
            error_dialog.showMessage("Please enter a valid email address")

            self.load_flag = False

        self.disable_options()

    def disable_options(self):
        """This function prohibits a user from trying to access GUI commands
        before they are ready. For example, an image cannot be processed
        before a valid email has been entered or a file has been loaded.

        Returns:

        """

        # Disable loading images if there is not valid email address
        self.ui.toolButtonLoad.setEnabled(self.load_flag)

        # Disable Apply push button if no image is loaded
        self.ui.pushButtonApply.setEnabled(self.process_flag)

        # Disable Download push button if no image is loaded
        self.ui.pushButtonDonwload.setEnabled(self.save_flag)

    def load_image_dialog(self):
        """Calls files_dialog to create a window explorer in which a single
        or multiple files may be selected.

        Returns:

        """

        # Launch the load image dialog
        self.load_dialog = LoadDialog(self)
        self.df['load_filenames'] = self.load_dialog.files
        print(self.df)

        # Close dialog box
        self.load_dialog.close()

        # Update image path shown in GUI
        self.ui.lineEditLoad.setText(self.df['load_filenames'][0])

        # Add images to combobox to allow for viewing
        self.ui.comboBox.addItems(self.df['load_filenames'])

        # Check that the images exist
        if validate_file_exists(self.df['load_filenames']):

            # Load the images
            self.df['orig_im'] = load_image_series(self.df['load_filenames'])

            # Enable process flag
            self.process_flag = True

        else:
            # Show error message
            error_dialog = QtWidgets.QErrorMessage(self)
            error_dialog.showMessage("Please enter a valid email address")

            self.process_flag = False

        self.disable_options()

    def apply_clicked(self):
        """The "Apply Processing" button was clicked

        Returns:

        """

        # Load files
        self.df['orig_im'] = load_image_series(self.df['load_filenames'])

        # Get processing settings
        self.df['hist'] = self.ui.radioButtonHist.isChecked()
        self.df['cont'] = self.ui.radioButtonContrast.isChecked()
        self.df['log'] = self.ui.radioButtonLog.isChecked()
        self.df['rev'] = self.ui.radioButtonReverse.isChecked()
        self.df['median'] = self.ui.radioButtonMedian.isChecked()

        print(self.df)

        # Allow image saving
        self.save_flag = True
        self.disable_options()

        # TODO: Add call to communictation function

    def image_viewer(self):

        if self.ui.radioButtonShowBoth:

            # Show both images
            self.df['show1'] = True
            self.df['show2'] = True

        else:
            # Show only one image
            self.df['show1'] = self.ui.radioButtonShowinal
            self.df['show2'] = self.ui.radioButtonShowProcessed

        # Get histomgram request
        self.df['showHist'] = self.ui.checkBoxShowHist

        # Call image viewer
        run_image_viewer(self.df)

    def download_clicked(self):
        """The "Download" button was clicked

        This function grabs the selected GUI options and calls a function to
        save the processed images.

        Returns:

        """
        # TODO: add a check that the images have been processed
        # TODO: get processed image(s)

        # Get save settings
        self.df['JPEG'] = self.ui.radioButtonJPEG.isChecked()
        self.df['PNG'] = self.ui.radioButtonPNG.isChecked()
        self.df['TIFF'] = self.ui.radioButtonTIFF.isChecked()

        print(self.df)

        # Launch the save image dialog box
        self.save_dialog = SaveDialog(self, df=self.df)
        self.df['save_filename'] = self.save_dialog.filename
        print(self.df)

        # Close dialog box
        self.save_dialog.close()

        # Write images
        save_images(self.df)

    def pullcombotext(self, ind):

        self.df['imageInd'] = ind


if __name__ == "__main__":

    app = QtWidgets.QApplication([])
    application = MainWindow()
    application.show()
    sys.exit(app.exec())
