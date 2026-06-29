from asyncsnmplib.mib.mib_index import MIB_INDEX
from libprobe.asset import Asset
from libprobe.check import Check
from ..snmpclient import get_snmp_client
from ..snmpquery import snmpquery

QUERIES = (
    (MIB_INDEX['CISCO-PROCESS-MIB']['cpmCPUTotalEntry'], True),
)


def on_item(item: dict, interval: int) -> dict:
    cpu_load_key = ['cpmCPULoadAv1Min', 'cpmCPULoadAv5Min'][interval >= 300]
    cpu_total_key = ['cpmCPUTotal1Min', 'cpmCPUTotal5Min'][interval >= 300]
    cpu_load = item.get(cpu_load_key)
    cpu_total = item.get(cpu_total_key)
    mem_comitted = item.get('cpmCPUMemoryCommittedHC',
                            item.get('cpmCPUMemoryCommitted'))
    mem_free = item.get('cpmCPUMemoryFreeHC', item.get('cpmCPUMemoryFree'))
    mem_used = item.get('cpmCPUMemoryFreeHC', item.get('cpmCPUMemoryFree'))
    mem_kernel_reserved = item.get('cpmCPUMemoryKernelReservedHC',
                                   item.get('cpmCPUMemoryKernelReserved'))
    return {
        'name': item['name'],
        'cpuLoad': cpu_load,
        'cpuTotal': cpu_total,
        'memoryComitted': mem_comitted,
        'memoryFree': mem_free,
        'memoryKernelReserved': mem_kernel_reserved,
        'memoryUsed': mem_used,
    }


class CheckCpm(Check):
    key = 'cpm'
    unchanged_eol = 0

    @staticmethod
    async def run(asset: Asset, local_config: dict, config: dict) -> dict:

        snmp = get_snmp_client(asset, local_config, config)
        state = await snmpquery(snmp, QUERIES)

        interval = config.get('_interval', 300)
        items = [
            on_item(item, interval)
            for item in state.get('cpmCPUTotalEntry', [])
        ]

        return {
            'cpm': items
        }
