import pytest

from app.services.flight.crsf import _crc8_dvb_s2, encode_channels, pack_channels


def test_pack_channels_encodes_all_16_values() -> None:
    values = [172, 992, 1811, 0, 2047] + [992] * 11

    packed = pack_channels(values)

    assert len(packed) == 22
    unpacked: list[int] = []
    for channel in range(16):
        bit_offset = channel * 11
        value = 0
        for bit in range(11):
            absolute_bit = bit_offset + bit
            if packed[absolute_bit // 8] & (1 << (absolute_bit % 8)):
                value |= 1 << bit
        unpacked.append(value)
    assert unpacked == values


def test_channel_frame_has_valid_length_and_crc() -> None:
    frame = encode_channels([992] * 16)

    assert frame[:3] == bytes([0xC8, 24, 0x16])
    assert len(frame) == 26
    assert _crc8_dvb_s2(frame[2:-1]) == frame[-1]


def test_channel_values_reject_invalid_payload() -> None:
    with pytest.raises(ValueError, match="16 unsigned 11-bit"):
        pack_channels([992] * 15)
    with pytest.raises(ValueError, match="16 unsigned 11-bit"):
        pack_channels([2048] + [992] * 15)
