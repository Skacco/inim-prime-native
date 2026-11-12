from typing import Final

from inim.prime.native.utils import Interval

ZONE_TERMINAL_IDS_INTERVAL: Final[Interval] = Interval(0, 1004)
ZONE_IDS_INTERVAL: Final[Interval] = Interval(0, 2009)
ZONE_1_ID_OFFSET = 1005 # 2009 - 1004

'''
Firmware 5 added 500 zones to the zone tables (labels and settings), right after
the 1005 terminal zones: "Z. Video" 1005-1204, "Z. Radio" 1205-1454 and
"Zona and" 1455-1504. Everything that followed moved forward by 500, so the
second zone of a double-zone terminal is at <terminal id> + 1505 instead of
<terminal id> + 1005 (read on a Prime120 4.07 and on two Prime060 5.00).
'''
FIRMWARE_5_EXTRA_ZONES: Final[int] = 500
FIRMWARE_5_ZONE_1_ID_OFFSET: Final[int] = ZONE_1_ID_OFFSET + FIRMWARE_5_EXTRA_ZONES
FIRMWARE_5_MAJOR_VERSION: Final[int] = 5


def get_zone_1_id_offset(firmware: str) -> int:
    """
    Offset of the second zone of a double-zone terminal for a firmware version
    as returned by get_panel_info (e.g. "5.00").

    Falls back to the firmware 4 layout when the version cannot be read.
    """
    major_version, _, _ = firmware.strip().partition(".")
    if major_version.isdigit() and int(major_version) >= FIRMWARE_5_MAJOR_VERSION:
        return FIRMWARE_5_ZONE_1_ID_OFFSET
    return ZONE_1_ID_OFFSET


def get_zone_ids_interval(zone_1_id_offset: int = ZONE_1_ID_OFFSET) -> Interval:
    """Zone ids to read from the zone tables for a given second-zone offset."""
    return Interval(0, zone_1_id_offset + ZONE_TERMINAL_IDS_INTERVAL.end)
