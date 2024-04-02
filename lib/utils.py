from asyncsnmplib.utils import snmp_queries
from libprobe.asset import Asset


async def get_data(
        asset: Asset,
        asset_config: dict,
        check_config: dict,
        queries: dict) -> dict:
    address = check_config.get('address')
    if address is None:
        address = asset.name

    state = await snmp_queries(address, asset_config, queries)
    return state
