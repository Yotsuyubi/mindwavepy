SYNC = b'\xaa'
EXCODE = b'\x55'

POOR_SIGNAL = b'\x02'
ATTENTION = b'\x04'
MEDITIATION = b'\x05'

RAW = b'\x80'
ASIC = b'\x83'
RAW_LANGTH = 2
ASIC_LENGTH = 24


class Parser(object):

    def __init__(self, mindwave):

        self.serial = mindwave

        self.PLENGTH = None
        self.PAYLOAD = []


    def __call__(self):

        self.PAYLOAD = self.get_payload()
        if self.PAYLOAD is None:
            return None

        result = self.parse_payload(self.PAYLOAD)
        if result is None:
            return None

        return result


    def parse_payload(self, payload):

        excode_count = 0

        for p in payload:
            if p != EXCODE:
                break
            excode_count = excode_count + 1
        
        payload = payload[excode_count:]

        code = payload[0]
        data = payload[1:]
        
        if code == RAW:
            return self.parse_RAW(data)

        if code == POOR_SIGNAL:
            return self.parse_ASIC(data)

        return None


    def parse_ASIC(self, data):

        poor_signal = int.from_bytes(data[0], 'big')

        delta_bytes = b''.join(data[3:6])
        theta_bytes = b''.join(data[6:9])
        low_alpha_bytes = b''.join(data[9:12])
        high_alpha_bytes = b''.join(data[12:15])
        low_beta_bytes = b''.join(data[15:18])
        high_beta_bytes = b''.join(data[18:21])
        low_gamma_bytes = b''.join(data[21:24])
        mid_gamma_bytes = b''.join(data[24:27])

        attention = int.from_bytes(data[28], 'big')
        meditiation = int.from_bytes(data[30], 'big')

        max_uint = int.from_bytes(b'\xff\xff\xff', 'big')

        return {
            "type": "ASIC",
            "poor": poor_signal / 100,
            "ASIC": {
                "delta": int.from_bytes(delta_bytes, 'big') / max_uint,
                "theta": int.from_bytes(theta_bytes, 'big') / max_uint,
                "low_aplha": int.from_bytes(low_alpha_bytes, 'big') / max_uint,
                "high_alpha": int.from_bytes(high_alpha_bytes, 'big') / max_uint,
                "low_beta": int.from_bytes(low_beta_bytes, 'big') / max_uint,
                "high_beta": int.from_bytes(high_beta_bytes, 'big') / max_uint,
                "low_gamma": int.from_bytes(low_gamma_bytes, 'big') / max_uint,
                "mid_gamma": int.from_bytes(mid_gamma_bytes, 'big') / max_uint
            },
            "attention": attention / 100,
            "meditiation": meditiation / 100
        }


    def parse_RAW(self, data):

        value = [
            int.from_bytes(data[1], 'big'), 
            int.from_bytes(data[2], 'big')
        ]
        raw = value[0]*256 + value[1]
        if raw >= 32768:
            raw = raw - 65536
        raw = raw / 32768

        return {
            "type": "RAW",
            "value": raw
        }


    def get_payload(self):

        # Read SYNC twice.
        if self.read_SYNC() != SYNC:
            return None
        if self.read_SYNC() != SYNC:
            return None

        self.PLENGTH = self.read_PLENGTH()
        if self.PLENGTH is None:
            return None

        payload = self.read_PAYLOAD()

        checksum = self.sum(payload)
        checksum = checksum & 0xff
        checksum = ~checksum & 0xff

        if self.read_CHKSUM() != bytes([checksum]):
            return None

        return payload

    
    def read_SYNC(self):
        byte = self.serial.read_byte()
        return byte


    def read_PLENGTH(self):

        byte = self.serial.read_byte()

        if byte == SYNC:
            return self.read_PLENGTH()

        if byte > SYNC:
            return None

        return byte


    def read_PAYLOAD(self):
        return [self.serial.read_byte() for i in range(int.from_bytes(self.PLENGTH, 'big'))]

    
    def read_CHKSUM(self):
        return self.serial.read_byte()

    def sum(self, bytearray):
        int_array = [int.from_bytes(b, 'big') for b in bytearray]
        summary = sum(int_array)
        return summary
