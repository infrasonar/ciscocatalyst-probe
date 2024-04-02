from asyncsnmplib.mib.mib_index import MIB_INDEX
from libprobe.asset import Asset
from ..utils import get_data

QUERIES = (
    MIB_INDEX['CISCO-STACK-MIB']['chassisGrp'],
    MIB_INDEX['CISCO-ENTITY-SENSOR-MIB']['entSensorValueEntry'],
    MIB_INDEX['CISCO-IF-EXTENSION-MIB']['cieIfPacketStatsEntry'],
)


async def check_catalyst(
        asset: Asset,
        asset_config: dict,
        check_config: dict) -> dict:
    state = await get_data(asset, asset_config, check_config, QUERIES)
    return state
