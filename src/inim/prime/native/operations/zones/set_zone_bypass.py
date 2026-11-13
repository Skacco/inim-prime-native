from typing import Final

from inim.prime.native.const import Encoding, CommandOperation
from inim.prime.native.utils import encode_int
from inim.prime.native.wire.payload import CommandWithPinRequestPayload
from inim.prime.native.wire.protocol import Protocol

ENABLE_BYPASS_VALUE: Final[int] = 0
DISABLE_BYPASS_VALUE: Final[int] = 2

'''
The panel refuses the id of the second zone of a double-zone terminal in this
command (the response data is 05 00, as for a terminal that is not a zone).
The second zone is addressed with the terminal id and a different value.
Response data seen on a Prime060 5.00 and on a Prime120 4.07: 01 00 nothing to
change, 02 00 bypassed, 03 00 bypass removed, 05 00 refused.
'''
ENABLE_SECOND_ZONE_BYPASS_VALUE: Final[int] = 1
DISABLE_SECOND_ZONE_BYPASS_VALUE: Final[int] = 3

def assemble_data(
        zone_id: int,
        bypass: bool,
        second_zone_of_terminal: bool = False,
) -> bytes:
    """
    :param zone_id: Zone id, or the terminal id when second_zone_of_terminal is set.
    :param second_zone_of_terminal: Act on the second zone of the double-zone
                                    terminal zone_id.
    """
    zone_id_bytes = encode_int(zone_id, Encoding.UINT16_LE)

    if second_zone_of_terminal:
        enable_value, disable_value = ENABLE_SECOND_ZONE_BYPASS_VALUE, DISABLE_SECOND_ZONE_BYPASS_VALUE
    else:
        enable_value, disable_value = ENABLE_BYPASS_VALUE, DISABLE_BYPASS_VALUE

    if bypass:
        bypass_bytes = encode_int(enable_value, Encoding.UINT16_LE)
    else:
        bypass_bytes = encode_int(disable_value, Encoding.UINT16_LE)


    command_data = b"".join([zone_id_bytes, bypass_bytes])

    return command_data


def assemble_payload(
        zone_id: int,
        bypass: bool,
        pin: str | None = None,
        second_zone_of_terminal: bool = False,
) -> bytes:
    return CommandWithPinRequestPayload.assemble(
        CommandOperation.SET_ZONE_BYPASS,
        pin,
        assemble_data(zone_id, bypass, second_zone_of_terminal),
    )


async def set_zone_bypass(
        protocol: Protocol,
        zone_id: int,
        bypass: bool,
        pin: str | None = None,
        second_zone_of_terminal: bool = False,
) -> None:
    await protocol.execute_command_with_pin(
        operation = CommandOperation.SET_ZONE_BYPASS,
        data = assemble_data(zone_id, bypass, second_zone_of_terminal),
        pin = pin,
    )
