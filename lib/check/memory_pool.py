from asyncsnmplib.mib.mib_index import MIB_INDEX
from libprobe.asset import Asset
from libprobe.check import Check
from ..snmpclient import get_snmp_client
from ..snmpquery import snmpquery

QUERIES = (
    (MIB_INDEX['CISCO-MEMORY-POOL-MIB']['ciscoMemoryPoolEntry'], True),
)


def on_item(item: dict) -> dict:
    name = item['Name']
    free = item['Free']
    largest_free = item['LargestFree']
    used = item['Used']
    total = free + used
    used_percent = used / total * 100 if total > 0 else None
    valid = item['Valid']
    return {
        'name': name,
        'Free': free,
        'LargestFree': largest_free,
        'Used': used,
        'UsedPercent': used_percent,
        'Valid': valid,
    }


class CheckMemoryPool(Check):
    key = 'memoryPool'
    unchanged_eol = 0

    @staticmethod
    async def run(asset: Asset, local_config: dict, config: dict) -> dict:

        snmp = get_snmp_client(asset, local_config, config)
        state = await snmpquery(snmp, QUERIES, True)

        items = [
            on_item(item)
            for item in state.get('ciscoMemoryPool', [])
        ]

        return {
            'memoryPool': items
        }
