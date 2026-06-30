from asyncsnmplib.mib.mib_index import MIB_INDEX
from libprobe.asset import Asset
from libprobe.check import Check
from ..snmpclient import get_snmp_client
from ..snmpquery import snmpquery

QUERIES = (
    (MIB_INDEX['CISCO-MEMORY-POOL-MIB']['ciscoMemoryPoolEntry'], True),
)


def on_item(item: dict) -> dict:
    free = item['ciscoMemoryPoolFree']
    used = item['ciscoMemoryPoolUsed']
    total = free + used
    if total > 0:
        item['ciscoMemoryPoolUsedPercent'] = used / total * 100
    return item


class CheckMemoryPool(Check):
    key = 'memoryPool'
    unchanged_eol = 0

    @staticmethod
    async def run(asset: Asset, local_config: dict, config: dict) -> dict:

        snmp = get_snmp_client(asset, local_config, config)
        state = await snmpquery(snmp, QUERIES)

        items = [
            on_item(item)
            for item in state.get('ciscoMemoryPoolEntry', [])
        ]

        return {
            'memoryPool': items
        }
