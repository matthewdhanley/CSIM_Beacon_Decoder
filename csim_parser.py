"""Parse CSIM packet"""
__author__ = "James Paul Mason/Matthew Hanley"
__contact__ = "mattdhanley@gmail.com"

from numpy import uint8, int16, uint16
from find_sync_bytes import FindSyncBytes
from logger import Logger
import struct


class CsimParser:
    def __init__(self, csim_packet):
        self.csim_packet = csim_packet  # [bytearray]: Un-decoded data to be parsed
        self.log = Logger().create_log()
        # todo - make more elegant. For now, 400 works.
        self.expected_packet_length = 400

    def parse_packet(self):
        """
        Returns decoded telemetry as a dictionary
        """
        if not self.is_valid_packet():
            return None

        self.ensure_packet_starts_at_sync()
        telemetry = dict()

        # Note: The [n: n + 2] instead of [n: n + 1] is because python slicing cuts short
        # e.g., to get bytes at indices 3 and 4, you don't do minxss_packet[3:4], you have to do csim_packet[3:5]
        # todo - update all of this
        # The telem points that are commented out still need unique functions. The rest of them use 
        #the new general decode function. It hasn't been tested so mileage may vary. 
        telemetry['bct_adcs_mode'] = self.decode_spacecraft_mode(self.csim_packet[165])                    # [Unitless]
        # telemetry['tai_label'] = self.stuff
        # telemetry['time_valid_label'] = 
        #todo telemetry['bct_Q_BODY_WRT_ECI1'] = self.decode_general(self.csim_packet[115:119], 4, 'sn', conversion=5e-10)
        #todo telemetry['bct_Q_BODY_WRT_ECI2'] = self.decode_general(self.csim_packet[119:123], 4, 'sn', conversion=5e-10)
        #todo telemetry['bct_Q_BODY_WRT_ECI3'] = self.decode_general(self.csim_packet[123:127], 4, 'sn', conversion=5e-10)
        #todo telemetry['bct_Q_BODY_WRT_ECI4'] = self.decode_general(self.csim_packet[127:131], 4, 'sn', conversion=5e-10)
        #todo telemetry['attitude_valid_label'] = stuff
        telemetry['bct_filtered_speed_rpm1'] = self.decode_general(self.csim_packet[180:182], 2, 'sn', conversion=4e-1)
        telemetry['bct_filtered_speed_rpm2'] =self.decode_general(self.csim_packet[182:184], 2, 'sn', conversion=4e-1)
        telemetry['bct_filtered_speed_rpm3'] =self.decode_general(self.csim_packet[184:186], 2, 'sn', conversion=4e-1)
        #todo telemetry['bct_position_error1'] =self.decode_general(self.csim_packet[183:187], 4, 'sn', conversion=2e-9)
        #todo telemetry['bct_position_error2'] =self.decode_general(self.csim_packet[187:191], 4, 'sn', conversion=2e-9)
        #todo telemetry['bct_position_error3'] =self.decode_general(self.csim_packet[191:195], 4, 'sn', conversion=2e-9)
        telemetry['bct_box1_temp'] =self.decode_general(self.csim_packet[305:307], 2, 'sn', conversion=5e-3)
        telemetry['bct_bus_voltage'] =self.decode_general(self.csim_packet[315:317], 2,'sn', conversion=1e-3)
        telemetry['bct_voltage_12p0'] =self.decode_general(self.csim_packet[299], 1,'dn', conversion=1e-1)
        telemetry['bct_battery_voltage'] =self.decode_general(self.csim_packet[317:319], 2, 'sn', conversion=2e-3)
        telemetry['bct_battery_current'] =self.decode_general(self.csim_packet[319:321], 2, 'sn', conversion=2e-3)
        telemetry['bct_battery1_temp'] =self.decode_general(self.csim_packet[321:323], 2, 'sn', conversion=5e-3)
        telemetry['bct_battery1_temp'] =self.decode_general(self.csim_packet[323:325], 2, 'sn', conversion=5e-3)
        #todo telemetry['bct_gps_valid'] =self.decode_general(self.csim_packet[275:276], 1, 'dn')
        #todo telemetry['bct_sdr_temp'] =self.decode_general(self.csim_packet[299:300], 1, 'sn')
        telemetry['bct_mag_vector_body1'] =self.decode_general(self.csim_packet[244:246], 2, 'sn', conversion=5e-9)
        telemetry['bct_mag_vector_body2'] =self.decode_general(self.csim_packet[246:248], 2, 'sn', conversion=5e-9)
        telemetry['bct_mag_vector_body3'] =self.decode_general(self.csim_packet[248:250], 2, 'sn', conversion=5e-9)

        return telemetry

    def is_valid_packet(self):
        fsb = FindSyncBytes()
        sync_start_index = fsb.find_sync_start_index(self.csim_packet)

        if sync_start_index == -1:
            self.log.error('Invalid packet detected. No sync start pattern found. Returning.')
            return False
        return True

    def ensure_packet_starts_at_sync(self):
        fsb = FindSyncBytes()
        sync_offset = fsb.find_sync_start_index(self.csim_packet)
        self.csim_packet = self.csim_packet[sync_offset:len(self.csim_packet)]
    
    def decode_general(self, bytearray_temp, nbytes, dtype, conversion=1.0, endian='big'):
        if nbytes == 1:
            unpack_format = 'b'
        elif nbytes == 2:
            unpack_format = 'h'
        elif nbytes == 4:
            unpack_format = 'i'
        elif nbytes == 8:
            unpack_format = 'q'
        else:
            self.log.debug("Not an expected number of bytes.")
            return None

        if dtype == 'sn':
            unpack_format = unpack_format.upper()
        elif dtype == 'dn':
            unpack_format = unpack_format.lower()
        else:
            self.log.debug("Not an expected data format")
            return None

        if endian == 'big':
            unpack_format = '>' + unpack_format
        elif endian == 'little':
            unpack_format = '<' + unpack_format
        else:
            self.log.debug("Using system unpack format")

        raw_value = struct.unpack(unpack_format,bytearray_temp)[0]
        converted_value = raw_value * conversion

        return converted_value


