# secure-hospital-network

## CRC checksums

The `crc` package provides CRC-16-CCITT (polynomial `0x1021`, initial value
`0xFFFF`) and IEEE CRC-32 checksums. `calculate_crc` accepts `bytes` and
returns an integer checksum:

```python
from crc import calculate_crc, format_crc, verify_checksum

payload = b"patient data"
checksum = calculate_crc(payload)  # CRC-16 by default
crc32 = calculate_crc(payload, "CRC-32")
formatted = format_crc(checksum)
is_valid = verify_checksum(payload, formatted)
```

The `CRC-16-CCITT` name is also accepted as an alias for `CRC-16`. The same
calculation functions are available through `crc.checker` and `modules.crc`.
Run the focused tests from the repository root with
`python -m unittest discover -s tests -p "test_crc.py" -v`.
