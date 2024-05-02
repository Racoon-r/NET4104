"""@ble docstring
Documentation for this module.

Implementation of functions to decode Bluetooth Low Energy data.

Copyright (c) 2018 Romain MOREAU
"""
import binascii
import sys

BLE_ACCESS_ADDR = b'8e89bed6'
BLE_CRC_LEN = 3
BLE_PREAMBLE = ['\xAA', '\x55']
BLE_PREAMBLE_LEN = 1
BLE_ADDR_LEN = 4
BLE_PDU_HDR_LEN = 2
BLE_PDU_TYPE_PRIMARY = {0b0000: 'ADV_IND', 0b0001: 'ADV_DIRECT_IND', 0b0010: 'ADV_NONCONN_IND', 0b0011: 'SCAN_REQ',
                        0b0100: 'SCAN_RSP', 0b0101: 'CONNECT_IND', 0b0110: 'ADV_SCAN_IND', 0b0111: 'ADV_EXT_IND'}


def swap_bytes(binary: bytes, bytes_pkt: int = 2):
    """
    Swap bytes. E.g: \xAE\xE2 -> \xE2\xAE (bytes pkt = 2)
    :param binary: Integer representing unicode string
    :param bytes_pkt: Packet of byte to swap (default 2)
    :return: Swapped bytes
    """
    index = len(binary)
    output = b""
    for i, bit in enumerate(binary):
        if i % bytes_pkt == 0:
            output += binary[index - bytes_pkt:index]
            index -= bytes_pkt
    return output


def whitening(data: bytes, channel: int):
    """
    (De)Whitening function, using LFSR. Feedback is set on 7 bits and register on 8 bits.
    The 5-bit value shall be extended with two MSBs of value 1.
    Position 0 is set to 1, position 1 to 6 are set to the channel index, starting by the MSB. E.g, for channel 37,
    feedback would be 0b1100101.

    Construction: On each byte and bit, if MSB of the feedback is set then Position 4 takes the XORed value of
    Position 3 and Position 7. Current data byte is also XORed with Position 7 (in fact, this operation always occurs
    when Pos.7 is set to 1. Byte will be XORed with current position a.k.a. pow(2,i)).
    In each case, feedback will be shifted by 1 and values are send to register.
    :param data: Data to white / de-white.
    :param channel: Channel of the rf transmission.
    :return: Register
    """
    feedback = 0b1000000 + (channel & 0b111111)
    register = b""
    length = 8

    for d in data:
        for i in range(length):
            if feedback & 0b1:
                feedback ^= 0b10001000
                d ^= pow(2, i)
            feedback >>= 1
        register += d.to_bytes(1, 'little')

    return register


def crc(data: bytes, crc_len: int):
    """
    Calculate CRC using LFSR. This function uses right shift on a 24-bit feedback.
    In Core v5.3, 0x555555 is used as seed (where msb is 0, and lsb is 1). However, msb is set on Position 24, which is
    the lsb of the current feedback. To match requirements, 0xAAAAAA will be used.
    Polynomial function used is x^24 + x^10 + x^9 + x^6 + x^4 + x^3 + x^1 + x^0.
    :param crc_len: Length of the CRC field to exclude
    :param data: Bytes to calculate CRC
    :return: Register in bytes.
    """
    feedback = 0xAAAAAA
    register = b""
    length = 8
    # Shift to the right.
    for d in data[:len(data) - crc_len]:
        for i in range(length):
            pos_23 = feedback & 0b1

            feedback >>= 1

            if pos_23 != (d & 0b1):
                feedback ^= 0b110110100110000000000000  # 0b11001011011  # Taps defined in Core v5.3.

            d >>= 1

    for j in range(3):
        register += chr((feedback >> j * length) & 0xff).encode("latin-1")
    return register


class BLEDecode:

    def __init__(self, file_input, ):
        with open(file_input, "rb") as buffer:
            self.file_input = buffer.read()
            self.file_input_str = self.file_input.decode("latin-1")
        self.packet = {}
        self.position_index = []

    def preamble(self):
        for position, byte in enumerate(self.file_input_str):
            if byte in BLE_PREAMBLE:
                self.position_index.append(position)

    def ble_core(self):
        packet = {}
        for pos in self.position_index:
            if len(self.file_input_str[pos:]) < (BLE_ADDR_LEN + BLE_PDU_HDR_LEN):
                continue
            pos += BLE_PREAMBLE_LEN
            ble_addr = binascii.hexlify(self.file_input[pos:pos + BLE_ADDR_LEN])
            # Check BLE Access Address. For advertising, it must be '\x8e\x89\xbe\xd6'.
            if swap_bytes(ble_addr) == BLE_ACCESS_ADDR:
                print(f"Access Address found: {swap_bytes(ble_addr)}")
            else:
                continue
            pos += BLE_ADDR_LEN
            packet.update({"Access Address": swap_bytes(ble_addr)})

            # Check BLE PDU.
            # ADVERTISING PHYSICAL CHANNEL PDU: Header (16 bits) + Payload (2-255 octets)

            # PDU HEADER: PDU Type | RFU | ChSel | TxAdd | RxAdd | Length
            pdu_header = whitening(self.file_input[pos:pos + BLE_PDU_HDR_LEN], 37)
            pdu = {"Type": 0, "RFU": 0, "ChSel": 0, "TxAdd": 0, "RxAdd": 0}
            for i, p in enumerate(pdu):
                pdu[p] = pdu_header[0] & (pow(2, 4 + i) - 1)
                if i > 0:
                    pdu[p] >>= (3 + i)
            if pdu["Type"] in BLE_PDU_TYPE_PRIMARY:
                pdu["Type"] = BLE_PDU_TYPE_PRIMARY[pdu["Type"]]
                print(f'PDU Type: {pdu["Type"]}')
            else:
                continue
            pdu.update({"Length": pdu_header[1]})

            # PDU PAYLOAD / CRC.
            pdu_payload_crc = whitening(self.file_input[pos:pos + BLE_PDU_HDR_LEN + pdu["Length"] + BLE_CRC_LEN], 37)
            if pdu_payload_crc[-BLE_CRC_LEN:] != crc(pdu_payload_crc, BLE_CRC_LEN):
                print("CRC not correct")
                continue
            print("CRC correct.")
            
            pdu.update({"Payload": pdu_payload_crc[BLE_PDU_HDR_LEN:BLE_PDU_HDR_LEN + pdu["Length"]],
                        "CRC": pdu_payload_crc[-BLE_CRC_LEN:]})
            # Get hardware address
            add_pdu = pdu["Payload"][:6]
            address = "0x"
            for l in range(len(add_pdu)):
                address += hex(add_pdu[len(add_pdu) - l - 1])[2:]
            pdu.update({"Address": address})
            packet.update(pdu)
            
            print(packet)
            print("\n#########\n")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Please specify a file.")
        exit(0)
    Ble = BLEDecode(sys.argv[1])
    Ble.preamble()
    Ble.ble_core()
