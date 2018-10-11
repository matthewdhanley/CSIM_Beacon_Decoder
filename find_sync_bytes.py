class FindSyncBytes:
    def __init__(self):
        self.log_sync_bytes = bytearray([0x08, 0x1D])  # Real time spacecraft messages to ignore
        self.start_sync_bytes = bytearray([0x08, 0x19])  # Beacon housekeeping data
        self.stop_sync_bytes = bytearray([0xa5, 0xa5])

    def find_log_sync_start_index(self, buffered_serial_data):
        return bytearray(buffered_serial_data).find(self.log_sync_bytes)

    def find_sync_start_index(self, buffered_serial_data):
        return bytearray(buffered_serial_data).find(self.start_sync_bytes)

    def find_sync_stop_index(self, buffered_serial_data):
        return bytearray(buffered_serial_data).find(self.stop_sync_bytes)
