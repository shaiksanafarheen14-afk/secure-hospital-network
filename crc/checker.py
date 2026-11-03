"""CRC checksum calculation and verification helpers."""

import binascii
from typing import Union


def _normalize_algorithm(algorithm: str) -> str:
    if not isinstance(algorithm, str):
        raise TypeError("algorithm must be a string")

    normalized = algorithm.strip().upper()
    if normalized in {"CRC-16", "CRC-16-CCITT"}:
        return "CRC-16"
    if normalized == "CRC-32":
        return normalized
    raise ValueError(f"unsupported CRC algorithm: {algorithm!r}")


def _validate_data(data: bytes) -> None:
    if not isinstance(data, bytes):
        raise TypeError("data must be bytes")


def calculate_crc(data: bytes, algorithm: str = "CRC-16") -> int:
    """Calculate CRC-16-CCITT or IEEE CRC-32 and return the checksum as an integer."""
    _validate_data(data)
    normalized_algorithm = _normalize_algorithm(algorithm)

    if normalized_algorithm == "CRC-32":
        return binascii.crc32(data) & 0xFFFFFFFF

    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc


def format_crc(checksum: int, algorithm: str = "CRC-16") -> str:
    """Format a CRC integer as an uppercase, zero-padded hexadecimal string."""
    normalized_algorithm = _normalize_algorithm(algorithm)
    if not isinstance(checksum, int) or isinstance(checksum, bool):
        raise TypeError("checksum must be an integer")

    width = 4 if normalized_algorithm == "CRC-16" else 8
    if not 0 <= checksum < (1 << (width * 4)):
        raise ValueError(f"checksum does not fit in {width * 4} bits")
    return f"0x{checksum:0{width}X}"


def verify_checksum(
    data: bytes, expected_checksum: Union[int, str], algorithm: str = "CRC-16"
) -> bool:
    """Return whether data produces the expected integer or hexadecimal CRC."""
    _validate_data(data)
    normalized_algorithm = _normalize_algorithm(algorithm)

    if isinstance(expected_checksum, str):
        value = expected_checksum.strip()
        if value.lower().startswith("0x"):
            value = value[2:]
        try:
            expected_value = int(value, 16)
        except ValueError as error:
            raise ValueError("expected_checksum must be a hexadecimal CRC") from error
    elif isinstance(expected_checksum, int) and not isinstance(expected_checksum, bool):
        expected_value = expected_checksum
    else:
        raise TypeError("expected_checksum must be an integer or hexadecimal string")

    width = 16 if normalized_algorithm == "CRC-16" else 32
    if not 0 <= expected_value < (1 << width):
        raise ValueError(f"expected_checksum does not fit in {width} bits")

    return calculate_crc(data, normalized_algorithm) == expected_value
