from asyncsnmplib.mib.mib_index import MIB_INDEX
from libprobe.asset import Asset
from libprobe.check import Check
from ..snmpclient import get_snmp_client
from ..snmpquery import snmpquery
from ..utils import InterfaceLookup

QUERIES = (
    (MIB_INDEX['IF-MIB']['ifEntry'], True),
    (MIB_INDEX['CISCO-CDP-MIB']['cdpInterfaceEntry'], True),
    (MIB_INDEX['CISCO-CDP-MIB']['cdpCacheEntry'], True),
    (MIB_INDEX['CISCO-CDP-MIB']['cdpGlobal'], False),
)


class CheckCdp(Check):
    key = 'cdp'

    @staticmethod
    async def run(asset: Asset, local_config: dict, config: dict) -> dict:

        snmp = get_snmp_client(asset, local_config, config)

        if_entry = InterfaceLookup.get(asset.id)
        if if_entry is None:
            state_data = await snmpquery(snmp, QUERIES, True)
            if_entry = InterfaceLookup.set(asset.id, state_data.get('if', []))
        else:
            state_data = await snmpquery(snmp, QUERIES[1:], True)

        cdp_if = state_data.get('cdpInterface', [])
        for item in cdp_if:
            if_index = item['name']

            # remove unused metric
            item.pop('MessageInterval', None)

            try:
                if_item = if_entry[if_index]
                item['Interface'] = if_item['Descr']
            except Exception:
                continue

        cdp_cache = state_data.get('cdpCache', [])
        for item in cdp_cache:
            # split key (ifIndex.deviceIndex)
            if_index = item['name'].split('.', 1)[0]

            # remove unused metric
            item.pop('Capabilities', None)
            item.pop('LastChange', None)

            try:
                if_item = if_entry[if_index]
                item['Interface'] = if_item['Descr']
            except Exception:
                continue

        cdp_global = state_data.get('cdpGlobal', [])
        for item in cdp_global:
            # remove unused metric
            item.pop('LastChange', None)

        return {
            'cdpInterface': cdp_if,
            'cdpCache': cdp_cache,
            'cdpGlobal': cdp_global,
        }
