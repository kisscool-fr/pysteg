import math
import zlib
from base64 import b64encode
from dataclasses import dataclass

from app.gui.controllers.actions import Hiding
from app.gui.controllers.actions import ImageInfo

# Below this pixel count the primes are counted exactly; above it a lower bound
# is used so the estimate never promises more room than the image really has.
_EXACT_PRIME_COUNT_LIMIT = 2_000_000

# Above the limit, Pierre Dusart (2010): pi(n) >= n / (ln n - 1) for n >= 5393.

# A JPEG APP1 segment holds at most 65_535 bytes, minus its length field,
# the "Exif\0\0" marker and the TIFF/IFD structures piexif writes around the
# message (measured at under 100 bytes; 128 keeps the estimate conservative).
EXIF_SEGMENT_LIMIT = 65_535 - 2 - 6 - 128

_BITS_PER_LSB_PIXEL = 3


@dataclass(frozen=True)
class Capacity:
    used: int
    available: int

    @property
    def fits(self) -> bool:
        return self.used <= self.available

    @property
    def ratio(self) -> float:
        if self.available <= 0:
            return 1.0
        return self.used / self.available


def count_primes_below(n: int) -> int:
    """Number of primes strictly below ``n`` (a lower bound for large ``n``)."""
    if n <= 2:  # noqa: PLR2004
        return 0
    if n <= _EXACT_PRIME_COUNT_LIMIT:
        sieve = bytearray([1]) * n
        sieve[0] = sieve[1] = 0
        for i in range(2, math.isqrt(n - 1) + 1):
            if sieve[i]:
                sieve[i * i :: i] = bytes(len(range(i * i, n, i)))
        return sum(sieve)
    return int(n / (math.log(n) - 1))


def lsb_capacity(width: int, height: int) -> int:
    """Largest message, in bytes, that ``lsb.hide`` with primes can store."""
    bits = count_primes_below(width * height) * _BITS_PER_LSB_PIXEL
    total_bytes = bits // 8
    # stegano prefixes the message with "<length>:".
    for digits in range(1, 12):
        room = total_bytes - digits - 1
        if room < 10**digits:
            return max(room, 0)
    return 0


def exif_capacity(existing_exif_size: int) -> int:
    return max(EXIF_SEGMENT_LIMIT - existing_exif_size, 0)


def available_bytes(info: ImageInfo) -> int:
    match info.technique:
        case Hiding.LSB:
            return lsb_capacity(info.width, info.height)
        case Hiding.EXIF:
            return exif_capacity(info.exif_size)
        case _:
            return 0


def payload_bytes(technique: Hiding | None, payload: str) -> int:
    """Bytes ``payload`` takes once written with ``technique``."""
    data = payload.encode("utf-8")
    if technique == Hiding.EXIF:
        # stegano stores compress(b64encode(message)) in ImageDescription.
        return len(zlib.compress(b64encode(data)))
    return len(data)


def measure(info: ImageInfo, payload: str) -> Capacity:
    return Capacity(
        used=payload_bytes(info.technique, payload),
        available=available_bytes(info),
    )
