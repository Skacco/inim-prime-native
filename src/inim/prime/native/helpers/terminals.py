import asyncio

from inim.prime.native.models.outputs import Output
from inim.prime.native.models.terminals import Terminal, TerminalStatus, TerminalType
from inim.prime.native.models.zones import SingleZone, DoubleZone
from inim.prime.native.operations.outputs.get_output_labels import get_output_labels
from inim.prime.native.operations.terminals.get_terminal_statuses import get_terminal_statuses
from inim.prime.native.operations.zones.const import ZONE_1_ID_OFFSET, get_zone_ids_interval
from inim.prime.native.operations.zones.get_zone_labels import get_zone_labels
from inim.prime.native.operations.zones.get_zone_settings import get_zone_settings
from inim.prime.native.utils import Interval
from inim.prime.native.wire.protocol import Protocol


async def get_terminal_statuses_by_intervals(
    protocol: Protocol,
    intervals: list[Interval],
    pin: str | None = None,
) -> dict[int, TerminalStatus]:
    terminal_statuses: dict[int, TerminalStatus] = {}

    results = await asyncio.gather(
        *(get_terminal_statuses(protocol, interval, pin) for interval in intervals)
    )

    for result in results:
        terminal_statuses |= result

    return terminal_statuses


async def initialize_terminals(
        protocol: Protocol,
        pin: str | None = None,
        zone_1_id_offset: int = ZONE_1_ID_OFFSET,
) -> dict[int, Terminal]:
    """
    :param zone_1_id_offset: Offset of the second zone of a double-zone terminal,
                             it depends on the firmware (see get_zone_1_id_offset).
    """
    terminals: dict[int, Terminal] = {}
    zone_ids_interval = get_zone_ids_interval(zone_1_id_offset)

    terminal_statuses, zone_labels, zone_settings, output_labels = await asyncio.gather(
        get_terminal_statuses(protocol, pin = pin),
        get_zone_labels(protocol, zone_ids_interval),
        get_zone_settings(protocol, zone_ids_interval),
        get_output_labels(protocol)
    )

    for terminal_id, terminal_status in terminal_statuses.items():
        if terminal_status.type == TerminalType.SINGLE_ZONE:
            zone_id = terminal_id

            terminals[terminal_id] = SingleZone.decode(
                terminal_id = terminal_id,
                terminal_status = terminal_status,
                zone_id = zone_id,
                zone_label = zone_labels[zone_id],
                zone_setting = zone_settings[zone_id],
            )

        elif terminal_status.type == TerminalType.DOUBLE_ZONE:
            zone_0_id = terminal_id
            zone_1_id = terminal_id + zone_1_id_offset

            terminals[terminal_id] = DoubleZone.decode(
                terminal_id = terminal_id,
                terminal_status = terminal_status,
                zone_0_id = zone_0_id,
                zone_0_label = zone_labels[zone_0_id],
                zone_0_setting = zone_settings[zone_0_id],
                zone_1_id = zone_1_id,
                zone_1_label = zone_labels[zone_1_id],
                zone_1_setting = zone_settings[zone_1_id],
            )

        elif terminal_status.type == TerminalType.OUTPUT:
            terminals[terminal_id] = Output.decode(
                terminal_id = terminal_id,
                terminal_status = terminal_status,
                # The output label table only covers the on-board outputs.
                # A terminal of an expansion (or a virtual one) programmed as
                # output has its description in the terminal label table.
                label = output_labels.get(terminal_id, zone_labels.get(terminal_id, "")),
            )


    return terminals


async def update_terminal_statuses(
    protocol: Protocol,
    terminals: dict[int, Terminal],
    intervals: list[Interval],
    pin: str | None = None,
) -> dict[int, Terminal]:
    terminal_statuses = await get_terminal_statuses_by_intervals(
        protocol, intervals, pin
    )

    for terminal in terminals.values():
        terminal.update_status(terminal_statuses.get(terminal.terminal_id))

    return terminals
