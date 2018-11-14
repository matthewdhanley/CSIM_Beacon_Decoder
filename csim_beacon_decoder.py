import sys
import os
import configparser
from PySide2 import QtGui, QtCore
from PySide2.QtWidgets import QMainWindow, QApplication
from PySide2.QtGui import QColor
from PySide2.QtCore import QFile
from ui_mainWindow import Ui_MainWindow
from logger import Logger
import connect_port_get_packet
import file_upload
import datetime
from serial.tools import list_ports  # This is pyserial, not plain serial
from csim_parser import CsimParser

"""Call the GUI and attach it to functions."""
__author__ = "James Paul Mason"
__contact__ = "jmason86@gmail.com"


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.green_color = None
        self.yellow_color = None
        self.red_color = None
        self.connected_port = None
        self.config_filename = None
        self.base_output_filename = None
        self.output_hex_filename = None
        self.output_binary_filename = None

        self.log = Logger().create_log()
        self.log.info("Launched CSIM Beacon Decoder.")

        self.setup_colors()
        self.setupUi(self)
        self.setup_available_ports()
        self.connect_ui_to_functions()
        self.setup_last_used_settings()
        self.setup_output_files()
        self.port_read_thread = PortReadThread(self.read_port, self.stop_read)
        QApplication.instance().aboutToQuit.connect(self.prepare_to_exit)
        self.show()

    def setup_colors(self):
        green = QColor(55, 195, 58)
        palette_green = QtGui.QPalette()
        palette_green.setColor(QtGui.QPalette.Text, green)
        palette_green.setColor(QtGui.QPalette.Foreground, green)
        self.green_color = palette_green

        yellow = QColor(244, 212, 66)
        palette_yellow = QtGui.QPalette()
        palette_yellow.setColor(QtGui.QPalette.Text, yellow)
        palette_yellow.setColor(QtGui.QPalette.Foreground, yellow)
        self.yellow_color = palette_yellow

        red = QColor(242, 86, 77)
        palette_red = QtGui.QPalette()
        palette_red.setColor(QtGui.QPalette.Text, red)
        palette_red.setColor(QtGui.QPalette.Foreground, red)
        self.red_color = palette_red

    def setup_available_ports(self):
        """
        Determine what ports are available for serial reading and populate the combo box with these options
        """
        self.comboBox_serialPort.clear()
        list_port_info_objects = list_ports.comports()
        port_names = [x[0] for x in list_port_info_objects]
        self.comboBox_serialPort.addItems(port_names)

    def connect_ui_to_functions(self):
        self.actionConnect.triggered.connect(self.connect_clicked)
        self.checkBox_saveData.stateChanged.connect(self.save_data_toggled)
        self.checkBox_forwardData.stateChanged.connect(self.forward_data_toggled)
        self.checkBox_decodeKiss.stateChanged.connect(self.decode_kiss_toggled)
        self.lineEdit_callsign.editingFinished.connect(self.ground_station_config_changed)
        self.lineEdit_latitude.editingFinished.connect(self.ground_station_config_changed)
        self.lineEdit_longitude.editingFinished.connect(self.ground_station_config_changed)
        self.actionCompletePass.triggered.connect(self.complete_pass_clicked)

    def ground_station_config_changed(self):
        self.setup_output_files()
        self.write_gui_config_options_to_config_file()

    def setup_output_files(self):
        self.set_base_output_filename()
        self.setup_output_file_decoded_data_as_hex()
        self.setup_output_file_decoded_data_as_binary()

    def set_base_output_filename(self):
        callsign = self.lineEdit_callsign.text()
        latitude = self.lineEdit_latitude.text()
        longitude = self.lineEdit_longitude.text()
        self.base_output_filename = os.path.join(os.path.expanduser("~"), "CSIM_Beacon_Decoder", "output",
                                                 datetime.datetime.now().isoformat().replace(':',
                                                                                             '_')) + '_' + callsign + '_' + latitude + '_' + longitude

    def setup_output_file_decoded_data_as_hex(self):
        self.ensure_output_folder_exists()
        self.set_output_hex_filename()

        with open(self.output_hex_filename, 'w') as output_hex_file:
            self.log.info("Opening new .txt file to output decoded data as hex.")
            self.display_gui_output_hex_is_saving()
        output_hex_file.close()  # Will later append to file as needed

    @staticmethod
    def ensure_output_folder_exists():
        if not os.path.exists(os.path.join(os.path.expanduser("~"), "CSIM_Beacon_Decoder", "output")):
            os.makedirs(os.path.join(os.path.expanduser("~"), "CSIM_Beacon_Decoder", "output"))

    def set_output_hex_filename(self):
        self.output_hex_filename = self.base_output_filename + ".txt"

    def display_gui_output_hex_is_saving(self):
        self.textBrowser_savingDataToFile.setText("Saving data to files: {} and .dat.".format(self.output_hex_filename))
        self.textBrowser_savingDataToFile.setPalette(self.green_color)

    def setup_output_file_decoded_data_as_binary(self):
        self.ensure_output_folder_exists()
        self.set_output_binary_filename()

        with open(self.output_binary_filename, 'w') as buffer_output_binary_file:
            self.log.info("Opening new binary file to output decoded data.")
        buffer_output_binary_file.close()

    def set_output_binary_filename(self):
        self.output_binary_filename = self.base_output_filename + ".dat"

    def write_gui_config_options_to_config_file(self):
        config = configparser.ConfigParser()
        config.read(self.config_filename)
        config.set('input_properties', 'serial_port', self.comboBox_serialPort.currentText())
        config.set('input_properties', 'baud_rate', self.lineEdit_baudRate.text())
        config.set('input_properties', 'ip_address', self.lineEdit_ipAddress.text())
        config.set('input_properties', 'port', self.lineEdit_ipPort.text())
        config.set('input_properties', 'decode_kiss', str(self.checkBox_decodeKiss.isChecked()))
        config.set('input_properties', 'forward_data', str(self.checkBox_forwardData.isChecked()))
        config.set('input_properties', 'callsign', self.lineEdit_callsign.text())
        config.set('input_properties', 'latitude', self.lineEdit_latitude.text())
        config.set('input_properties', 'longitude', self.lineEdit_longitude.text())
        with open(os.path.join(os.path.expanduser("~"), "CSIM_Beacon_Decoder", "input_properties.cfg"), 'w') as configfile:
            config.write(configfile)
        self.log.info('Updated input_properties.cfg file with new settings.')

    def setup_last_used_settings(self):
        config = configparser.ConfigParser()
        self.config_filename = os.path.join(os.path.expanduser("~"), "CSIM_Beacon_Decoder", "input_properties.cfg")
        if self.need_new_config_file(config):
            self.log.info('No input_properties.cfg file found. Creating the default one.')
            self.write_default_config()

        config.read(self.config_filename)
        self.set_instance_variables_from_config(config)

    def need_new_config_file(self, config):
        if not os.path.isfile(self.config_filename):
            return True
        if os.stat(self.config_filename).st_size == 0:
            return True

        try:
            config.read(self.config_filename)
        except configparser.MissingSectionHeaderError:
            return True

        if not config.has_option('input_properties', 'serial_port'):
            return True
        if not config.has_option('input_properties', 'baud_rate'):
            return True
        if not config.has_option('input_properties', 'ip_address'):
            return True
        if not config.has_option('input_properties', 'port'):
            return True
        if not config.has_option('input_properties', 'decode_kiss'):
            return True
        if not config.has_option('input_properties', 'forward_data'):
            return True
        if not config.has_option('input_properties', 'callsign'):
            return True
        if not config.has_option('input_properties', 'latitude'):
            return True
        if not config.has_option('input_properties', 'longitude'):
            return True

    def write_default_config(self):
        with open(self.config_filename, "w") as config_file:
            print("[input_properties]", file=config_file)
            print("serial_port = 3", file=config_file)
            print("baud_rate = 19200", file=config_file)
            print("ip_address = localhost", file=config_file)
            print("port = 10000", file=config_file)
            print("decode_kiss = True", file=config_file)
            print("forward_data = True", file=config_file)
            print("callsign = SFJPM86", file=config_file)
            print("latitude = 40.240", file=config_file)
            print("longitude = -105.2353", file=config_file)

    def set_instance_variables_from_config(self, config):
        self.tabWidget_serialIp.setCurrentIndex(1)  # TODO: Make this an actual config parameter
        self.comboBox_serialPort.insertItem(0, config.get('input_properties', 'serial_port'))
        self.comboBox_serialPort.setCurrentIndex(0)
        self.lineEdit_baudRate.setText(config.get('input_properties', 'baud_rate'))
        self.lineEdit_ipAddress.setText(config.get('input_properties', 'ip_address'))
        self.lineEdit_ipPort.setText(config.get('input_properties', 'port'))
        self.lineEdit_callsign.setText(config.get('input_properties', 'callsign'))
        self.lineEdit_latitude.setText(config.get('input_properties', 'latitude'))
        self.lineEdit_longitude.setText(config.get('input_properties', 'longitude'))
        self.checkBox_decodeKiss.setChecked(self.str2bool(config.get('input_properties', 'decode_kiss')))
        self.checkBox_forwardData.setChecked(self.str2bool(config.get('input_properties', 'forward_data')))
        # Intentionally don't do saveData -- always defaults to on to avoid frustration of lost data

    @staticmethod
    def str2bool(bool_string):
        if bool_string == 'True':
            return True
        if bool_string == 'False':
            return False
        raise ValueError('Can only accept exact strings "True" or "False". Was passed {}'.format(bool_string))

    def connect_clicked(self):
        self.write_gui_config_options_to_config_file()

        connect_button_text = str(self.actionConnect.iconText())
        if connect_button_text == "Connect":
            self.connect_to_port()
        else:
            self.disconnect_from_port()

    def connect_to_port(self):
        self.log.info("Attempting to connect to port.")

        self.toggle_connect_button(is_currently_connect=True)

        if self.user_chose_serial_port():
            self.connected_port, port_readable = self.connect_to_serial_port()
        else:  # user chose TCP/IP socket
            self.connected_port, port_readable = self.connect_to_socket_port()

        if port_readable:
            self.port_read_thread.start()
            self.display_gui_reading()
        else:
            self.display_gui_read_failed()

    def toggle_connect_button(self, is_currently_connect):
        if is_currently_connect:
            connect_button_text = 'Disconnect'
        else:
            connect_button_text = 'Connect'
        self.actionConnect.setText(QApplication.translate("MainWindow", connect_button_text, None, -1))

    def user_chose_serial_port(self):
        if self.tabWidget_serialIp.currentIndex() == self.tabWidget_serialIp.indexOf(self.serial):
            return True
        else:
            return False  # implying user chose TCP/IP socket

    def connect_to_serial_port(self):
        port = self.comboBox_serialPort.currentText()
        baud_rate = self.lineEdit_baudRate.text()

        connect_serial = connect_port_get_packet.ConnectSerial(port, baud_rate, self.log)
        connected_port = connect_serial.connect_to_port()
        port_readable = connected_port.port_readable

        return connected_port, port_readable

    def connect_to_socket_port(self):
        ip_address = self.lineEdit_ipAddress.text()
        port = self.lineEdit_ipPort.text()

        connect_socket = connect_port_get_packet.ConnectSocket(ip_address, port)
        connected_port = connect_socket.connect_to_port()
        port_readable = connect_socket.port_readable

        return connected_port, port_readable

    def display_gui_reading(self):
        reading = QApplication.translate("MainWindow", "Reading", None, -1)
        if self.user_chose_serial_port():
            self.label_serialStatus.setText(reading)
            self.label_serialStatus.setPalette(self.green_color)
        else:
            self.label_socketStatus.setText(reading)
            self.label_socketStatus.setPalette(self.green_color)

    def display_gui_read_failed(self):
        read_failed = QApplication.translate("MainWindow", "Read failed", None, -1)
        if self.user_chose_serial_port:
            self.label_serialStatus.setText(read_failed)
            self.label_serialStatus.setPalette(self.red_color)
        else:
            self.label_socketStatus.setText(read_failed)
            self.label_socketStatus.setPalette(self.red_color)

    def disconnect_from_port(self):
        self.log.info("Attempting to disconnect from port.")

        self.toggle_connect_button(is_currently_connect=False)
        self.display_gui_port_closed()

        self.stop_read()

    def display_gui_port_closed(self):
        port_closed = QApplication.translate("MainWindow", "Port closed", None, -1)
        if self.user_chose_serial_port():
            self.label_serialStatus.setText(port_closed)
            self.label_serialStatus.setPalette(self.red_color)
        else:
            self.label_socketStatus.setText(port_closed)
            self.label_socketStatus.setPalette(self.red_color)

    def complete_pass_clicked(self):
        self.upload_data()

    def upload_data(self):
        if self.do_forward_data():
            self.display_gui_uploading()
            file_upload.upload(self.output_binary_filename)
            self.display_gui_upload_complete()

    def do_forward_data(self):
        return self.checkBox_forwardData.isChecked()

    def display_gui_uploading(self):
        self.label_uploadStatus.setText("Upload status: Uploading")

    def display_gui_upload_complete(self):
        self.label_uploadStatus.setText("Upload status: Complete")

    def read_port(self):
        while True:
            buffer_data = self.connected_port.read_packet()
            if len(buffer_data) == 0:
                continue

            buffer_data = self.decode_kiss(buffer_data)

            buffer_data_hex_string = self.convert_buffer_data_to_hex_string(buffer_data)
            self.display_gui_hex(buffer_data_hex_string)

            self.save_data_to_disk(buffer_data_hex_string, buffer_data)

            csim_parser = CsimParser(buffer_data)
            telemetry = csim_parser.parse_packet()
            self.display_gui_telemetry(telemetry)

    def decode_kiss(self, buffer_data):
        if self.do_decode_kiss():
            # C0 is a special KISS character that get replaced; unreplace it
            buffer_data = buffer_data.replace(bytearray([0xdb, 0xdc]), bytearray([0xc0]))
            # DB is a special KISS character that get replaced; unreplace it
            buffer_data = buffer_data.replace(bytearray([0xdb, 0xdd]), bytearray([0xdb]))
        return buffer_data

    def do_decode_kiss(self):
        return self.checkBox_decodeKiss.isChecked()

    @staticmethod
    def convert_buffer_data_to_hex_string(buffer_data):
        return ' '.join('0x{:02x}'.format(x) for x in buffer_data)

    def display_gui_hex(self, buffer_data_hex_string):
        self.textBrowser_serialOutput.append(buffer_data_hex_string)
        scroll_to_bottom = self.textBrowser_serialOutput.verticalScrollBar().maximum()
        self.textBrowser_serialOutput.verticalScrollBar().setValue(scroll_to_bottom)

    def save_data_to_disk(self, buffer_data_hex_string, buffer_data):
        if self.do_save_data():
            output_hex_file = open(self.output_hex_filename, 'a')
            output_hex_file.write(buffer_data_hex_string)
            output_hex_file.close()

            output_binary_file = open(self.output_binary_filename, 'ab')
            output_binary_file.write(buffer_data)
            output_binary_file.close()

    def do_save_data(self):
        return self.checkBox_saveData.isChecked()

    def display_gui_telemetry(self, telemetry):
        if not telemetry:
            return

        self.label_lastPacketTime.setText(
            "Last packet at: {} local    /    {} UTC".format(self.get_local_time(), self.get_utc_time()))

        self.display_gui_telemetry_attitude(telemetry)
        self.display_gui_telemetry_power(telemetry)
        self.display_gui_telemetry_temperature(telemetry)

        # self.acmode_label.setPalette(self.green_color)
        # self.color_code_telemetry(telemetry)

    @staticmethod
    def get_local_time():
        local_time = datetime.datetime.now().replace(microsecond=0).isoformat(' ')
        return local_time

    @staticmethod
    def get_utc_time():
        utc_time = datetime.datetime.utcnow().replace(microsecond=0).isoformat(' ')
        return utc_time

    # TODO this will have to be edited for CSIM Mode.
    def display_gui_adcs_mode(self, telemetry):
        if telemetry['bct_adcs_mode'] == 0:
            self.acmode_label.setText("Sun Point")
        elif telemetry['bct_adcs_mode'] == 1:
            self.acmode_label.setText("Fine Reference Point")
        elif telemetry['bct_adcs_mode'] == 2:
            self.acmode_label.setText("Search Init")
        elif telemetry['bct_adcs_mode'] == 3:
            self.acmode_label.setText("Searching")
        elif telemetry['bct_adcs_mode'] == 4:
            self.acmode_label.setText("Waiting")
        elif telemetry['bct_adcs_mode'] == 5:
            self.acmode_label.setText("Converging")
        elif telemetry['bct_adcs_mode'] == 6:
            self.acmode_label.setText("On Sun")
        elif telemetry['bct_adcs_mode'] == 7:
            self.acmode_label.setText("Not Active")
        else:
            self.acmode_label.setText("Unknown")

    def display_gui_telemetry_power(self, telemetry):
        self.bati_label.setText("{0:.2f}".format(round(telemetry['bct_battery_current'], 2)))
        self.batv_label.setText("{0:.2f}".format(round(telemetry['bct_battery_voltage'], 2)))
        self.busv_label.setText("{0:.2f}".format(round(telemetry['bct_bus_voltage'], 2)))

    def display_gui_telemetry_temperature(self, telemetry):
        # self.radio_temp_label.setText("{0:.2f}".format(round(telemetry['bct_sdr_temp'], 2)))
        self.case_temp_label.setText("{0:.2f}".format(round(telemetry['bct_box1_temp'], 2)))
        # self.batt1_temp_label.setText("{0:.2f}".format(round(telemetry['bct_battery1_temp'], 2)))
        # self.batt2_temp_label.setText("{0:.2f}".format(round(telemetry['bct_battery2_temp'], 2)))

    def display_gui_telemetry_attitude(self,telemetry):
        self.display_gui_adcs_mode(telemetry)
        self.quat1_label.setText("{0:.2f}".format(round(telemetry['bct_Q_BODY_WRT_ECI1'], 2)))
        self.quat2_label.setText("{0:.2f}".format(round(telemetry['bct_Q_BODY_WRT_ECI2'], 2)))
        self.quat3_label.setText("{0:.2f}".format(round(telemetry['bct_Q_BODY_WRT_ECI3'], 2)))
        self.quat4_label.setText("{0:.2f}".format(round(telemetry['bct_Q_BODY_WRT_ECI4'], 2)))
        # self.attitude_valid_label.setText("{0:.2f}".format(round(telemetry['bct_attitude_valid'], 2)))
        self.rw1sdir_label.setText("{0:.2f}".format(round(telemetry['bct_filtered_speed_rpm1'], 2)))
        self.rw2sdir_label.setText("{0:.2f}".format(round(telemetry['bct_filtered_speed_rpm2'], 2)))
        self.rw3sdir_label.setText("{0:.2f}".format(round(telemetry['bct_filtered_speed_rpm3'], 2)))
        self.atterr1_label.setText("{0:.2f}".format(round(telemetry['bct_position_error1'], 2)))
        self.atterr2_label.setText("{0:.2f}".format(round(telemetry['bct_position_error2'], 2)))
        self.atterr3_label.setText("{0:.2f}".format(round(telemetry['bct_position_error3'], 2)))

    def display_gui_telemetry_general(self,telemetry):
        self.tai_label.setText("{0:.2f}".format(round(telemetry['bct_tai_seconds'], 2)))
        self.time_valid_label.setText("{0:.2f}".format(round(telemetry['bct_time_valid'], 2)))
        self.gps_valid_label.setText("{0:.2f}".format(round(telemetry['bct_gps_valid'], 2)))

    def color_code_telemetry(self, telemetry):
        self.color_code_spacecraft_state(telemetry)
        self.color_code_solar_data(telemetry)
        self.color_code_power(telemetry)
        self.color_code_temperature(telemetry)

    def color_code_spacecraft_state(self, telemetry):
        if telemetry['SpacecraftMode'] == 0:
            self.acmode_label.setPalette(self.red_color)
        elif telemetry['SpacecraftMode'] == 1:
            self.acmode_label.setPalette(self.red_color)
        elif telemetry['SpacecraftMode'] == 2:
            self.acmode_label.setPalette(self.yellow_color)
        elif telemetry['SpacecraftMode'] == 4:
            self.acmode_label.setPalette(self.green_color)
        if telemetry['PointingMode'] == 0:
            self.label_pointingMode.setPalette(self.yellow_color)
        elif telemetry['PointingMode'] == 1:
            self.label_pointingMode.setPalette(self.green_color)

    def color_code_solar_data(self, telemetry):
        if abs(telemetry['SpsX']) <= 3.0:
            self.label_spsX.setPalette(self.green_color)
        else:
            self.label_spsX.setPalette(self.red_color)

        if abs(telemetry['SpsY']) <= 3.0:
            self.label_spsY.setPalette(self.green_color)
        else:
            self.label_spsY.setPalette(self.red_color)

        if 0 <= telemetry['Xp'] <= 24860.0:
            self.label_xp.setPalette(self.green_color)
        else:
            self.label_xp.setPalette(self.red_color)

    def color_code_power(self, telemetry):
        solar_panel_minus_y_power = telemetry['SolarPanelMinusYVoltage'] * telemetry['SolarPanelMinusYCurrent'] / 1e3
        solar_panel_plus_x_power = telemetry['SolarPanelPlusXVoltage'] * telemetry['SolarPanelPlusXCurrent'] / 1e3
        solar_panel_plus_y_power = telemetry['SolarPanelPlusYVoltage'] * telemetry['SolarPanelPlusYCurrent'] / 1e3
        battery_current = self.get_battery_current(telemetry)

        if -1.0 <= solar_panel_minus_y_power <= 10.4:
            self.label_solarPanelMinusYPower.setPalette(self.green_color)
        else:
            self.label_solarPanelMinusYPower.setPalette(self.red_color)
        if -1.0 <= solar_panel_plus_x_power <= 5.9:
            self.label_solarPanelPlusXPower.setPalette(self.green_color)
        else:
            self.label_solarPanelPlusXPower.setPalette(self.red_color)
        if -1.0 <= solar_panel_plus_y_power <= 10.4:
            self.label_solarPanelPlusYPower.setPalette(self.green_color)
        else:
            self.label_solarPanelPlusYPower.setPalette(self.red_color)
        if telemetry['BatteryVoltage'] >= 7.2:
            self.label_batteryVoltage.setPalette(self.green_color)
        elif telemetry['BatteryVoltage'] >= 6.6:
            self.label_batteryVoltage.setPalette(self.yellow_color)
        else:
            self.label_batteryVoltage.setPalette(self.red_color)
        if 0 <= battery_current <= 2.9:
            self.label_batteryCurrent.setPalette(self.green_color)
        else:
            self.label_batteryCurrent.setPalette(self.red_color)

    def color_code_temperature(self, telemetry):
        if -8.0 <= telemetry['CommBoardTemperature'] <= 60.0:
            self.label_commBoardTemperature.setPalette(self.green_color)
        else:
            self.label_commBoardTemperature.setPalette(self.red_color)

        if 5.0 <= telemetry['BatteryTemperature'] <= 25:
            self.label_batteryTemperature.setPalette(self.green_color)
        elif 2.0 <= telemetry['BatteryTemperature'] < 5.0 or telemetry['BatteryTemperature'] > 25.0:
            self.label_batteryTemperature.setPalette(self.yellow_color)
        else:
            self.label_batteryTemperature.setPalette(self.red_color)

        if -8.0 <= telemetry['EpsBoardTemperature'] <= 45.0:
            self.label_epsBoardTemperature.setPalette(self.green_color)
        else:
            self.label_epsBoardTemperature.setPalette(self.red_color)

        if -8.0 <= telemetry['CdhBoardTemperature'] <= 29.0:
            self.label_cdhTemperature.setPalette(self.green_color)
        else:
            self.label_cdhTemperature.setPalette(self.red_color)

        if -13.0 <= telemetry['MotherboardTemperature'] <= 28.0:
            self.label_motherboardTemperature.setPalette(self.green_color)
        else:
            self.label_motherboardTemperature.setPalette(self.red_color)

        if -75.0 <= telemetry['SolarPanelMinusYTemperature'] <= 85.0:
            self.label_solarPanelMinusYTemperature.setPalette(self.green_color)
        else:
            self.label_solarPanelMinusYTemperature.setPalette(self.red_color)

        if -75.0 <= telemetry['SolarPanelPlusXTemperature'] <= 85.0:
            self.label_solarPanelPlusXTemperature.setPalette(self.green_color)
        else:
            self.label_solarPanelPlusXTemperature.setPalette(self.red_color)

        if -75.0 <= telemetry['SolarPanelPlusYTemperature'] <= 85.0:
            self.label_solarPanelPlusYTemperature.setPalette(self.green_color)
        else:
            self.label_solarPanelPlusYTemperature.setPalette(self.red_color)

    def stop_read(self):
        self.connected_port.close()

    def save_data_toggled(self):
        if self.do_save_data():
            self.setup_output_files()
        else:
            self.display_gui_no_output_data()

    def display_gui_no_output_data(self):
        self.textBrowser_savingDataToFile.setText("Not saving data to file.")
        self.textBrowser_savingDataToFile.setPalette(self.red_color)

    def forward_data_toggled(self):
        if self.do_forward_data():
            self.display_gui_upload_idle()
        else:
            self.display_gui_upload_disabled()

        self.write_gui_config_options_to_config_file()

    def display_gui_upload_idle(self):
        self.label_uploadStatus.setText("Upload status: Idle")

    def display_gui_upload_disabled(self):
        self.label_uploadStatus.setText("Upload status: Disabled")

    def decode_kiss_toggled(self):
        self.write_gui_config_options_to_config_file()

    def prepare_to_exit(self):
        self.log.info("About to quit.")
        self.upload_data()  # Only occurs if forward data is toggled on
        self.log.info("Closing CSIM Beacon Decoder.")


class PortReadThread(QtCore.QThread):
    """
    Separate class/thread to read the port in an infinite loop so the main loop can still respond to user interaction
    Input:
        QtCore.QThread: The thread to run this task on
    """
    def __init__(self, target, slot_on_finished=None):
        super(PortReadThread, self).__init__()
        self.target = target
        if slot_on_finished:
            self.finished.connect(slot_on_finished)  # signal (finished) connected to slot (stop_reading)

    def run(self, *args, **kwargs):
        self.target(*args, **kwargs)


def main():
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    ret = app.exec_()
    sys.exit(ret)


if __name__ == '__main__':
    main()
