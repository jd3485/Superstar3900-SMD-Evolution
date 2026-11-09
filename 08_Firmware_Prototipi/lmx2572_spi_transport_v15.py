"""LMX2572 24-bit frame construction ONLY, no complete PLL register image.

Data sheet SNAS740B section 7.5: [RW:1][ADDRESS:7][DATA:16], MSB first.
This module neither communicates with hardware nor provides a validated RF tune profile.
"""
from collections.abc import Mapping


def _validate_number(v: int, low: int, high: int, name: str):
    if type(v) is not int or not low <= v <= high:
        raise ValueError(f"{name} must be integer in {low}..{high}")


def build_frame(read: bool, register: int, data: int = 0) -> bytes:
    if type(read) is not bool:
        raise TypeError("read must be bool")
    _validate_number(register, 0, 125, "register")
    _validate_number(data, 0, 0xFFFF, "data")
    word = (int(read) << 23) | (register << 16) | data
    return word.to_bytes(3, "big")


def decode_request(frame: bytes) -> tuple[bool, int, int]:
    if not isinstance(frame, bytes) or len(frame) != 3:
        raise ValueError("exactly 3 bytes required")
    w = int.from_bytes(frame, "big")
    return bool(w & (1<<23)), (w >> 16) & 0x7F, w & 0xFFFF


def build_startup_register_frames(profile: Mapping[int,int], reset_r0: int, *, explicitly_validated: bool=False) -> tuple[bytes,...]:
    """Build TEST transaction sequence only from caller-validated 126-word image.

    Caller must prove all values/fields with TICS Pro and actual conditions; the
    reset word must contain the RESET bit as in the correct datasheet revision.
    This code intentionally does not guess RESET or field values.
    Power/CE/ref clock checks, >=500us wait, hardware timing: MCU responsibility.
    """
    if explicitly_validated is not True:
        raise ValueError("Missing explicit confirmation of external register profile validation")
    if not isinstance(profile, Mapping) or set(profile) != set(range(126)):
        raise ValueError("profile must contain each address 0..125 exactly once")
    for k,v in profile.items():
        _validate_number(k,0,125,"register")
        _validate_number(v,0,65535,"data")
    _validate_number(reset_r0,0,65535,"reset_r0")
    return (build_frame(False,0,reset_r0),) + tuple(build_frame(False,a,profile[a]) for a in range(125,-1,-1))
