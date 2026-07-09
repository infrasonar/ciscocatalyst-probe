from asyncsnmplib.mib.mib_index import MIB_INDEX
from libprobe.asset import Asset
from libprobe.check import Check
from ..snmpclient import get_snmp_client
from ..snmpquery import snmpquery, snmpwalk

QUERIES = (
    (MIB_INDEX['CISCO-PROCESS-MIB']['cpmCPUTotalEntry'], True),
)

ENTPHYSICALDESCR_OID = MIB_INDEX['ENTITY-MIB']['entPhysicalDescr']
ENTITY_CACHE = {}


def on_item(item: dict, interval5: bool, entity_lk: dict) -> dict:
    cpu_load_key = ['cpmCPULoadAvg1minRev', 'cpmCPULoadAvg5minRev'][interval5]
    cpu_total_key = ['cpmCPUTotal1minRev', 'cpmCPUTotal5minRev'][interval5]
    cpu_load = item.get(cpu_load_key)
    cpu_total = item.get(cpu_total_key)
    entity_index_or_zero = item.get('cpmCPUTotalPhysicalIndex')
    entity_descr = entity_lk.get(entity_index_or_zero)
    mem_committed = item.get('cpmCPUMemoryHCCommitted',
                             item.get('cpmCPUMemoryCommitted'))
    mem_free = item.get('cpmCPUMemoryHCFree', item.get('cpmCPUMemoryFree'))
    mem_used = item.get('cpmCPUMemoryHCUsed', item.get('cpmCPUMemoryUsed'))
    mem_kernel_reserved = item.get('cpmCPUMemoryHCKernelReserved',
                                   item.get('cpmCPUMemoryKernelReserved'))
    return {
        'name': item['name'],
        'CPULoad': cpu_load,
        'CPUTotal': cpu_total,
        'EntityDescr': entity_descr,
        'MemoryCommitted': mem_committed,
        'MemoryFree': mem_free,
        'MemoryKernelReserved': mem_kernel_reserved,
        'MemoryUsed': mem_used,
    }


class CheckCpm(Check):
    key = 'cpm'
    unchanged_eol = 0

    @staticmethod
    async def run(asset: Asset, local_config: dict, config: dict) -> dict:

        snmp = get_snmp_client(asset, local_config, config)
        state = await snmpquery(snmp, QUERIES)

        if not any(state.values()):
            return {}

        if asset.id not in ENTITY_CACHE:
            varbinds = await snmpwalk(snmp, ENTPHYSICALDESCR_OID)
            ENTITY_CACHE[asset.id] = {
                # oid[-1] == entPhysicalIndex == item name
                str(oid[-1]): value.decode('utf-8')
                for oid, value in varbinds
            }

        interval5 = config.get('_interval', 300) >= 300
        items = [
            on_item(item, interval5, ENTITY_CACHE[asset.id])
            for item in state.get('cpmCPUTotalEntry', [])
        ]

        return {
            'cpm': items
        }
