from asyncsnmplib.mib.mib_index import MIB_INDEX
from libprobe.asset import Asset
from libprobe.check import Check
from ..snmpclient import get_snmp_client
from ..snmpquery import snmpquery

QUERIES = (
    (MIB_INDEX['CISCO-ENVMON-MIB']['ciscoEnvMonSupplyStatusEntry'], True),
    (MIB_INDEX['CISCO-STACK-MIB']['chassisGrp'], False),
    (MIB_INDEX['CISCO-STACK-MIB']['systemGrp'], False),
)


class CheckSystem(Check):
    key = 'system'
    unchanged_eol = 14400

    @staticmethod
    async def run(asset: Asset, local_config: dict, config: dict) -> dict:

        snmp = get_snmp_client(asset, local_config, config)
        state = await snmpquery(snmp, QUERIES)

        return state
