from asyncsnmplib.mib.mib_index import MIB_INDEX
from libprobe.asset import Asset
from libprobe.check import Check
from ..snmpclient import get_snmp_client
from ..snmpquery import snmpquery

QUERIES = (
    (MIB_INDEX['CISCO-STACK-MIB']['chassisGrp'], False),
    (MIB_INDEX['CISCO-ENTITY-SENSOR-MIB']['entSensorValueEntry'], True),
    (MIB_INDEX['CISCO-IF-EXTENSION-MIB']['cieIfPacketStatsEntry'], True),
)


class CheckCatalyst(Check):
    key = 'catalyst'
    unchanged_eol = 0

    @staticmethod
    async def run(asset: Asset, local_config: dict, config: dict) -> dict:

        snmp = get_snmp_client(asset, local_config, config)
        state = await snmpquery(snmp, QUERIES)

        return state
