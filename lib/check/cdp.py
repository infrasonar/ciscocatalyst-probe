from asyncsnmplib.mib.mib_index import MIB_INDEX
from libprobe.asset import Asset
from libprobe.check import Check
from ..snmpclient import get_snmp_client
from ..snmpquery import snmpquery

QUERIES = (
    (MIB_INDEX['CISCO-CDP-MIB']['cdpInterfaceEntry'], True),
    (MIB_INDEX['CISCO-CDP-MIB']['cdpInterfaceExtEntry'], True),
    (MIB_INDEX['CISCO-CDP-MIB']['cdpCacheEntry'], True),
    (MIB_INDEX['CISCO-CDP-MIB']['cdpCtAddressEntry'], True),
    (MIB_INDEX['CISCO-CDP-MIB']['cdpGlobal'], False),
)


class CheckCdp(Check):
    key = 'cdp'

    @staticmethod
    async def run(asset: Asset, local_config: dict, config: dict) -> dict:

        snmp = get_snmp_client(asset, local_config, config)
        state = await snmpquery(snmp, QUERIES, True)

        return state