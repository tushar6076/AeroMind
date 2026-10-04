from __future__ import annotations

from pathlib import Path
import numpy as np


def export_to_dummy_tflite_bytes(weights_dict: dict) -> bytes:
    """Generates an embedded-ready flat byte buffer representing quantized parameters."""
    buffer = bytearray(b"TFL3_INT8_RESQ_AUTONOMY_PAYLOAD")
    for key, val in weights_dict.items():
        if hasattr(val, "cpu"):
            arr = val.cpu().numpy()
            q_arr = np.clip(np.round(arr * 127.0), -128, 127).astype(np.int8)
            buffer.extend(q_arr.tobytes())
    return bytes(buffer)