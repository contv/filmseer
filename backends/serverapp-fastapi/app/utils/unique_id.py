import array
import math
import random
import time
import uuid
from typing import Optional, Union

from app.core.config import settings


def _randint(a: int, b: int) -> int:
    try:
        return random.SystemRandom().randint(a, b)
    except NotImplementedError:
        return random.randint(a, b)


def _random_range_inf(
    start: int, stop: Optional[int] = None, step: Optional[int] = None
):
    # Set a default values the same way "range" does
    if stop is None:
        start, stop = 0, start
    if step is None:
        step = 1
    # Compute the number of numbers in this range
    maximum = (stop - start) // step
    # Seed range with a random integer
    value = _randint(0, maximum)
    #
    # Construct an offset, multiplier, and modulus for a linear
    # congruential generator. These generators are cyclic and
    # non-repeating when they maintain the properties:
    #
    #   1) "modulus" and "offset" are relatively prime
    #   2) ["multiplier" - 1] is divisible by all prime factors of "modulus"
    #   3) ["multiplier" - 1] is divisible by 4 if "modulus" is divisible by 4
    #
    offset = _randint(0, maximum) << 1 | 1  # Pick a random odd-valued offset
    multiplier = (
        maximum >> 2
    ) << 2 | 1  # Pick a multiplier 1 greater than a multiple of 4
    modulus = 2 << (
        int(math.ceil(math.log2(maximum))) - 1
    )  # Pick a modulus just big enough to generate all numbers (power of 2)
    # Track how many random numbers have been returned
    found = 0
    while True:
        # If this is a valid value, yield it in generator fashion
        if value < maximum:
            found += 1
            yield value * step + start  # convert into the desired range
        # Calculate the next value in the sequence
        value = (value * multiplier + offset) % modulus
        if found >= maximum:
            value = _randint(0, maximum)
            offset = _randint(0, maximum) << 1 + 1
            found = 0


_unique_id_clock_seq_generator = _random_range_inf(0x7FFFFFFF)

_machine_id_cache = None

_server_instance_name = settings.SERVER_INSTANCE_NAME


def id(machine_id: Optional[int] = None) -> int:
    """
    Generate an UUID-ish unique ID.

    The purpose of this is to have a roughly time-ordered id with a
    roughly unique machine id and without carefully arranging bytes.

    And it needs to be hard to guess, although it doesn't need to be
    cryptographically secure.

    Layout:
        64-bit signed positive timestamp:
            First bit is 0 - to make it a signed int128
            4 nanoseconds since Unix Epoch - no religious calendar
            Best-effort on precision -
              some platforms doesn't support nanoseconds
        32-bit signed clock sequence:
            A Linear Congruential Generator
            Range is 0 - 2147483647: easy for some math libs
            Reset with a new seed after an entire cycle
            Variables are stored in shared memory
        32-bit machine ID binary (unsigned):
            A hash truncated from a secure hash algorithm
            Usually we use SHA-512, but can be other algorithms
            The default is the first 20 bits of SHA-512 of MAC and
            12 bits of CRC32 of PID started at 5th bit, all from the left
    """
    if machine_id is None:
        global _machine_id_cache
        if _machine_id_cache:
            machine_id = _machine_id_cache
        else:
            import hashlib
            import os
            import zlib

            machine_id = (
                (
                    int.from_bytes(
                        hashlib.sha512(
                            (_server_instance_name or str(uuid.getnode())).encode(
                                "utf-8"
                            )
                        ).digest()[:3],
                        byteorder="big",
                    )
                    & 0xFFFFF0
                )
                >> 4
            ) << 12 | (
                zlib.crc32(os.getpid().to_bytes(4, byteorder="big")) & 0x0FFF0000
            ) >> 16
            _machine_id_cache = machine_id
    global _unique_id_clock_seq_generator
    timestamp = (time.time_ns() >> 2) & 0x7FFFFFFFFFFFFFFF
    clock_seq = next(_unique_id_clock_seq_generator) & 0x7FFFFFFF
    return (timestamp << 64) | (clock_seq << 32) | (machine_id & 0xFFFFFFFF)


#: Base32 character set. Excludes characters "I L O U"
ENCODING = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"

#: Array that maps encoded string char byte values to enable O(1) lookups
# fmt: off
DECODING = array.array(
    'B',
    (0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
     0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
     0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
     0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
     0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x01,
     0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0xFF, 0xFF,
     0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E,
     0x0F, 0x10, 0x11, 0x01, 0x12, 0x13, 0x01, 0x14, 0x15, 0x00,
     0x16, 0x17, 0x18, 0x19, 0x1A, 0xFF, 0x1B, 0x1C, 0x1D, 0x1E,
     0x1F, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x0A, 0x0B, 0x0C,
     0x0D, 0x0E, 0x0F, 0x10, 0x11, 0x01, 0x12, 0x13, 0x01, 0x14,
     0x15, 0x00, 0x16, 0x17, 0x18, 0x19, 0x1A, 0xFF, 0x1B, 0x1C,
     0x1D, 0x1E, 0x1F, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
     0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
     0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
     0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
     0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
     0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
     0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
     0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
     0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
     0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
     0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
     0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
     0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
     0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF)
)
# fmt: on


def to_uuid(
    from_value: Union[int, str, uuid.UUID, bytes, bytearray, memoryview]
) -> uuid.UUID:
    """
    Convert an ID to an UUID hyphen separated lower case string.
    """
    if isinstance(from_value, int):
        return str(uuid.UUID(int=from_value))
    if isinstance(from_value, str):
        return str(uuid.UUID(from_value))
    if isinstance(from_value, uuid.UUID):
        return str(from_value)
    return uuid.UUID(bytes=bytes(from_value))


def to_bytes(
    from_value: Union[int, str, uuid.UUID, bytes, bytearray, memoryview]
) -> bytes:
    """
    Convert an ID to 16 bytes.
    """
    if isinstance(from_value, int):
        return from_value.to_bytes(16, byteorder="big")
    if isinstance(from_value, uuid.UUID):
        return from_value.bytes
    if isinstance(from_value, str):
        value_s = str(from_value.strip())
        value_len = len(value_s)
        if value_len == 26:
            return from_str(value_s).to_bytes(16, byteorder="big")
        elif value_len == 36 or value_len == 32:
            return uuid.UUID(value_s).bytes
        else:
            raise ValueError("Unknown id length {}".format(len(from_value)))
    value = bytes(from_value)
    if len(value) != 16:
        raise ValueError("Expects 16 bytes, got {}".format(len(value)))
    return value


def to_base32(
    from_value: Union[int, str, uuid.UUID, bytes, bytearray, memoryview]
) -> str:
    """
    Convert an ID to a Crockford's Base32 upper case string.
    """
    value = to_bytes(from_value)
    encoding = ENCODING
    return (
        encoding[(value[0] & 0xE0) >> 5]
        + encoding[value[0] & 0x1F]
        + encoding[(value[1] & 0xF8) >> 3]
        + encoding[((value[1] & 0x07) << 2) | ((value[2] & 0xC0) >> 6)]
        + encoding[((value[2] & 0x3E) >> 1)]
        + encoding[((value[2] & 0x01) << 4) | ((value[3] & 0xF0) >> 4)]
        + encoding[((value[3] & 0x0F) << 1) | ((value[4] & 0x80) >> 7)]
        + encoding[(value[4] & 0x7C) >> 2]
        + encoding[((value[4] & 0x03) << 3) | ((value[5] & 0xE0) >> 5)]
        + encoding[value[5] & 0x1F]
        + encoding[(value[6] & 0xF8) >> 3]
        + encoding[((value[6] & 0x07) << 2) | ((value[7] & 0xC0) >> 6)]
        + encoding[(value[7] & 0x3E) >> 1]
        + encoding[((value[7] & 0x01) << 4) | ((value[8] & 0xF0) >> 4)]
        + encoding[((value[8] & 0x0F) << 1) | ((value[9] & 0x80) >> 7)]
        + encoding[(value[9] & 0x7C) >> 2]
        + encoding[((value[9] & 0x03) << 3) | ((value[10] & 0xE0) >> 5)]
        + encoding[value[10] & 0x1F]
        + encoding[(value[11] & 0xF8) >> 3]
        + encoding[((value[11] & 0x07) << 2) | ((value[12] & 0xC0) >> 6)]
        + encoding[(value[12] & 0x3E) >> 1]
        + encoding[((value[12] & 0x01) << 4) | ((value[13] & 0xF0) >> 4)]
        + encoding[((value[13] & 0x0F) << 1) | ((value[14] & 0x80) >> 7)]
        + encoding[(value[14] & 0x7C) >> 2]
        + encoding[((value[14] & 0x03) << 3) | ((value[15] & 0xE0) >> 5)]
        + encoding[value[15] & 0x1F]
    )


def from_str(id_value: str) -> int:
    """
    Convert an UUID formatted ID or a Crockford's Base32 ID back to int.
    """
    id_s = str(id_value).strip()
    id_b = b""
    id_len = len(id_s)
    if id_len == 36 or id_len == 32:
        id_b = to_base32(uuid.UUID(id_s).int).encode("ascii")
    elif id_len != 26:
        raise ValueError("Unknown id length {}".format(len(id_value)))
    else:
        id_b = id_s.upper().encode("ascii")
    lut = DECODING
    return int.from_bytes(
        bytes(
            (
                ((lut[id_b[0]] << 5) | lut[id_b[1]]) & 0xFF,
                ((lut[id_b[2]] << 3) | (lut[id_b[3]] >> 2)) & 0xFF,
                ((lut[id_b[3]] << 6) | (lut[id_b[4]] << 1) | (lut[id_b[5]] >> 4))
                & 0xFF,
                ((lut[id_b[5]] << 4) | (lut[id_b[6]] >> 1)) & 0xFF,
                ((lut[id_b[6]] << 7) | (lut[id_b[7]] << 2) | (lut[id_b[8]] >> 3))
                & 0xFF,
                ((lut[id_b[8]] << 5) | (lut[id_b[9]])) & 0xFF,
                ((lut[id_b[10]] << 3) | (lut[id_b[11]] >> 2)) & 0xFF,
                ((lut[id_b[11]] << 6) | (lut[id_b[12]] << 1) | (lut[id_b[13]] >> 4))
                & 0xFF,
                ((lut[id_b[13]] << 4) | (lut[id_b[14]] >> 1)) & 0xFF,
                ((lut[id_b[14]] << 7) | (lut[id_b[15]] << 2) | (lut[id_b[16]] >> 3))
                & 0xFF,
                ((lut[id_b[16]] << 5) | (lut[id_b[17]])) & 0xFF,
                ((lut[id_b[18]] << 3) | (lut[id_b[19]] >> 2)) & 0xFF,
                ((lut[id_b[19]] << 6) | (lut[id_b[20]] << 1) | (lut[id_b[21]] >> 4))
                & 0xFF,
                ((lut[id_b[21]] << 4) | (lut[id_b[22]] >> 1)) & 0xFF,
                ((lut[id_b[22]] << 7) | (lut[id_b[23]] << 2) | (lut[id_b[24]] >> 3))
                & 0xFF,
                ((lut[id_b[24]] << 5) | (lut[id_b[25]])) & 0xFF,
            )
        ),
        byteorder="big",
    )


__all__ = ["id", "to_uuid", "to_bytes", "to_base32", "from_str"]
