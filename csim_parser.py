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
        self.expected_packet_length = 400

    def parse_packet(self):
        """
        Returns decoded telemetry as a dictionary
        """
        if not self.is_valid_packet():
            return None

        self.ensure_packet_starts_at_sync()
        self.csim_packet = self.csim_packet[:]

        for i,x in enumerate(self.csim_packet):
            print(str(i)+':0x{:02x}'.format(x))

        hex_str = ' '.join('0x{:02x}'.format(x) for x in self.csim_packet)

        print(hex_str)
        print('')

        telemetry = dict()

        # Note: The [n: n + 2] instead of [n: n + 1] is because python slicing cuts short
        # e.g., to get bytes at indices 3 and 4, you don't do minxss_packet[3:4], you have to do csim_packet[3:5]
        # todo - update all of this
        # The telem points that are commented out still need unique functions. The rest of them use 
        #the new general decode function. It hasn't been tested so mileage may vary. 
        telemetry['bct_adcs_mode'] = self.decode_spacecraft_mode(self.csim_packet[165])                    # [Unitless]
        # telemetry['tai_label'] = self.stuff
        # telemetry['time_valid_label'] = 
        telemetry['bct_Q_BODY_WRT_ECI1'] = self.decode_general(self.csim_packet[115:119], 4, 'sn', conversion=5e-10)
        telemetry['bct_Q_BODY_WRT_ECI2'] = self.decode_general(self.csim_packet[119:123], 4, 'sn', conversion=5e-10)
        telemetry['bct_Q_BODY_WRT_ECI3'] = self.decode_general(self.csim_packet[123:127], 4, 'sn', conversion=5e-10)
        telemetry['bct_Q_BODY_WRT_ECI4'] = self.decode_general(self.csim_packet[127:131], 4, 'sn', conversion=5e-10)
        #telemetry['attitude_valid_label'] = stuff
        telemetry['bct_filtered_speed_rpm1'] = self.decode_general(self.csim_packet[168:170], 2, 'sn', conversion=4e-1)
        telemetry['bct_filtered_speed_rpm2'] =self.decode_general(self.csim_packet[170:172], 2, 'sn', conversion=4e-1)
        telemetry['bct_filtered_speed_rpm3'] =self.decode_general(self.csim_packet[172:174], 2, 'sn', conversion=4e-1)
        telemetry['bct_position_error1'] =self.decode_general(self.csim_packet[183:187], 4, 'sn', conversion=2e-9)
        telemetry['bct_position_error2'] =self.decode_general(self.csim_packet[187:191], 4, 'sn', conversion=2e-9)
        telemetry['bct_position_error3'] =self.decode_general(self.csim_packet[191:195], 4, 'sn', conversion=2e-9)

        telemetry['bct_box1_temp'] =self.decode_general(self.csim_packet[305:307], 2, 'sn', conversion=5e-3)

        telemetry['bct_bus_voltage'] =self.decode_general(self.csim_packet[315:317], 2,'sn', conversion=1e-3)

        hex_str_busv = ' '.join('0x{:02x}'.format(x) for x in self.csim_packet[257:259])
        print(hex_str_busv)
        print('')



        telemetry['bct_battery_voltage'] =self.decode_general(self.csim_packet[317:319], 2, 'sn', conversion=2e-3)
        telemetry['bct_battery_current'] =self.decode_general(self.csim_packet[319:321], 2, 'sn', conversion=2e-3)
        # telemetry['bct_gps_valid'] =self.decode_general(self.csim_packet[275:276], 1, 1, 'dn')

        # telemetry['bct_sdr_temp'] =self.decode_general(self.csim_packet[299:300], 1, 1e0, 'sn')
        telemetry['bct_mag_vector_body1'] =self.decode_general(self.csim_packet[232:234], 2, 'sn', conversion=5e-9)
        telemetry['bct_mag_vector_body2'] =self.decode_general(self.csim_packet[234:236], 2, 'sn', conversion=5e-9)
        telemetry['bct_mag_vector_body3'] =self.decode_general(self.csim_packet[236:238], 2, 'sn',conversion=5e-9)

        #Old tlm points
        # telemetry['CommandAcceptCount'] = self.decode_command_accept_count(self.csim_packet[16:16 + 2])  # [#]
        # telemetry['SpacecraftMode'] = self.decode_spacecraft_mode(self.csim_packet[12])                  # [Unitless]
        # telemetry['PointingMode'] = self.decode_pointing_mode(self.csim_packet[13])                      # [Unitless]
        # telemetry['Eclipse'] = self.decode_eclipse(self.csim_packet[12])                                 # [Boolean]

        # telemetry['EnableX123'] = self.decode_enable_x123(self.csim_packet[88:88 + 2])  # [Boolean]
        # telemetry['EnableSps'] = self.decode_enable_sps(self.csim_packet[88:88 + 2])    # [Boolean]

        # telemetry['SpsX'] = self.decode_sps(self.csim_packet[204:204 + 2])  # [deg]
        # telemetry['SpsY'] = self.decode_sps(self.csim_packet[206:206 + 2])  # [deg]
        # telemetry['Xp'] = self.decode_xp(self.csim_packet[192:192 + 4])     # [DN]

        # telemetry['CdhBoardTemperature'] = self.decode_temperature(self.csim_packet[86:86 + 2])                        # [deg C]
        # telemetry['CommBoardTemperature'] = self.decode_temperature(self.csim_packet[122:122 + 2])                     # [deg C]
        # telemetry['MotherboardTemperature'] = self.decode_temperature(self.csim_packet[124:124 + 2])                   # [deg C]
        # telemetry['EpsBoardTemperature'] = self.decode_temperature(self.csim_packet[128:128 + 2])                      # [deg C]
        # telemetry['SolarPanelMinusYTemperature'] = self.decode_temperature_solar_panel(self.csim_packet[160:160 + 2])  # [deg C]
        # telemetry['SolarPanelPlusXTemperature'] = self.decode_temperature_solar_panel(self.csim_packet[162:162 + 2])   # [deg C]
        # telemetry['SolarPanelPlusYTemperature'] = self.decode_temperature_solar_panel(self.csim_packet[164:164 + 2])   # [deg C]
        # telemetry['BatteryTemperature'] = self.decode_temperature_battery(self.csim_packet[174:174 + 2])               # [deg C]

        # telemetry['BatteryVoltage'] = self.decode_battery_voltage(self.csim_packet[132:132 + 2])           # [V]
        # telemetry['BatteryChargeCurrent'] = self.decode_battery_current(self.csim_packet[168:168 + 2])     # [mA]
        # telemetry['BatteryDischargeCurrent'] = self.decode_battery_current(self.csim_packet[172:172 + 2])  # [mA]
        
        # telemetry['SolarPanelMinusYCurrent'] = self.decode_solar_array_current(self.csim_packet[136:136 + 2])  # [mA]
        # telemetry['SolarPanelPlusXCurrent'] = self.decode_solar_array_current(self.csim_packet[140:140 + 2])   # [mA]
        # telemetry['SolarPanelPlusYCurrent'] = self.decode_solar_array_current(self.csim_packet[144:144 + 2])   # [mA]
        
        # telemetry['SolarPanelMinusYVoltage'] = self.decode_solar_array_voltage(self.csim_packet[138:138 + 2])  # [V]
        # telemetry['SolarPanelPlusXVoltage'] = self.decode_solar_array_voltage(self.csim_packet[142:142 + 2])   # [V]
        # telemetry['SolarPanelPlusYVoltage'] = self.decode_solar_array_voltage(self.csim_packet[146:146 + 2])   # [V]
        self.log.info("From CSIM parser:")
        self.log.info(telemetry)
        return telemetry

    def is_valid_packet(self):
        fsb = FindSyncBytes()
        sync_start_index = fsb.find_sync_start_index(self.csim_packet)

        if sync_start_index == -1:
            self.log.error('Invalid packet detected. No sync start pattern found. Returning.')
            return False
        # if packet_length != self.expected_packet_length:
        #     self.log.error('Invalid packet detected. Packet length is {0} but expected to be {1}. Returning.'.format(packet_length, self.expected_packet_length))
        #     return False

        return True

    def ensure_packet_starts_at_sync(self):
        fsb = FindSyncBytes()
        sync_offset = fsb.find_sync_start_index(self.csim_packet)
        self.csim_packet = self.csim_packet[sync_offset:len(self.csim_packet)]

    # TODO - I think the following can be generalized using struct.unpack
    def decode_bytes(self, bytearray_temp, return_unsigned_int=False):
        """
        Combine several bytes corresponding to a single telemetry point to a single integer
        # Input:
        #   bytearray_temp [bytearray]: The bytes corresponding to the telemetry to decode.
        #                               Can accept any number of bytes but do not expect more than 4
        # Flags:
        #   return_unsigned_int: If set, return an unsigned integer instead of the default signed integer
        # Output:
        #   telemetry_point_raw [int]: The single integer for the telemetry point to be converted to human-readable by
                                       the calling function
        """
        if len(bytearray_temp) == 1:
            telemetry_point_raw = bytearray_temp
        elif len(bytearray_temp) == 2:
            telemetry_point_raw = struct.unpack('>H',bytearray_temp)[0]
        elif len(bytearray_temp) == 4:
            telemetry_point_raw = (uint8(bytearray_temp[3]) << 24) | (uint8(bytearray_temp[2] << 16)) | \
                                  (uint8(bytearray_temp[1] << 8)) | (uint8(bytearray_temp[0] << 0))
        else:
            self.log.debug("More bytes than expected")
            return None

        if return_unsigned_int:
            return uint16(telemetry_point_raw)
        else:
            return int16(telemetry_point_raw)

    @staticmethod
    def decode_flight_model(bytearray_temp):
        flight_model = (bytearray_temp & 0x07)  # [Unitless]

        # Fix mistaken flight model number in final flight software burn
        if flight_model == 0:
            flight_model = 2
        elif flight_model == 4:
            flight_model = 3  # This is the engineering test unit (AKA FlatSat)
        return flight_model
    
    def decode_general(self, bytearray_temp, nbytes, dtype, conversion=1, endian='big'):
        unpack_format = ''
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

    def decode_command_accept_count(self, bytearray_temp):
        return self.decode_bytes(bytearray_temp)  # [#]
    
    @staticmethod
    def decode_spacecraft_mode(bytearray_temp):
        return bytearray_temp & 0x07  # [Unitless]
    
    @staticmethod
    def decode_pointing_mode(bytearray_temp):
        return bytearray_temp & 0x01  # [Unitless]
    
    def decode_enable_x123(self, bytearray_temp):
        decoded_byte = self.decode_bytes(bytearray_temp)
        return (decoded_byte & 0x0002) >> 1  # [Boolean]
    
    def decode_enable_sps(self, bytearray_temp):
        decoded_byte = self.decode_bytes(bytearray_temp)
        return (decoded_byte & 0x0004) >> 2  # [Boolean]
    
    def decode_sps(self, bytearray_temp):
        return self.decode_bytes(bytearray_temp) / 1e4 * 3.0  # [deg]

    @staticmethod
    def decode_eclipse(bytearray_temp):
        return (bytearray_temp & 0x08) >> 3  # [Boolean]

    def decode_xp(self, bytearray_temp):
        return self.decode_bytes(bytearray_temp, return_unsigned_int=True)  # [DN]
    
    def decode_temperature(self, bytearray_temp):
        return self.decode_bytes(bytearray_temp) / 256.0  # [deg C]
    
    def decode_temperature_battery(self, bytearray_temp):
        return self.decode_bytes(bytearray_temp, return_unsigned_int=True) * 0.18766 - 250.2  # [deg C]
    
    def decode_temperature_solar_panel(self, bytearray_temp):
        return self.decode_bytes(bytearray_temp, return_unsigned_int=True) * 0.1744 - 216.0  # [deg C]
    
    def decode_battery_voltage(self, bytearray_temp):
        return self.decode_bytes(bytearray_temp, return_unsigned_int=True) / 6415.0  # [V]
    
    def decode_battery_current(self, bytearray_temp):
        return self.decode_bytes(bytearray_temp, return_unsigned_int=True) * 3.5568 - 61.6  # [mA]
    
    def decode_solar_array_current(self, bytearray_temp):
        return self.decode_bytes(bytearray_temp, return_unsigned_int=True) * 163.8 / 327.68  # [mA]
    
    def decode_solar_array_voltage(self, bytearray_temp):
        return self.decode_bytes(bytearray_temp, return_unsigned_int=True) * 32.76 / 32768.0  # [V]


