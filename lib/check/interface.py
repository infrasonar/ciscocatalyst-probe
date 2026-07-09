import re
from asyncsnmplib.mib.mib_index import MIB_INDEX
from collections import Counter
from libprobe.asset import Asset
from libprobe.check import Check
from libprobe.exceptions import CheckException
from ..snmpclient import get_snmp_client
from ..snmpquery import snmpquery
from ..utils import InterfaceLookup

QUERIES = (
    (MIB_INDEX['IF-MIB']['ifEntry'], True),
    (MIB_INDEX['IF-MIB']['ifXEntry'], True),
    (MIB_INDEX['CISCO-IF-EXTENSION-MIB']['cieIfInterfaceEntry'], True),
    (MIB_INDEX['CISCO-IF-EXTENSION-MIB']['cieIfPacketStatsEntry'], True),
)


'''
ifSpeed OBJECT-TYPE
    SYNTAX      Gauge32
    MAX-ACCESS  read-only
    STATUS      current
    DESCRIPTION
            "An estimate of the interface's current bandwidth in bits
            per second.  For interfaces which do not vary in bandwidth
            or for those where no accurate estimation can be made, this
            object should contain the nominal bandwidth.  If the
            bandwidth of the interface is greater than the maximum value
            reportable by this object then this object should report its
            maximum value (4,294,967,295) and ifHighSpeed must be used
            to report the interace's speed.  For a sub-layer which has
            no concept of bandwidth, this object should be zero."
    ::= { ifEntry 5 }

ifHighSpeed OBJECT-TYPE
    SYNTAX      Gauge32
    MAX-ACCESS  read-only
    STATUS      current
    DESCRIPTION
            "An estimate of the interface's current bandwidth in units
            of 1,000,000 bits per second.  If this object reports a
            value of `n' then the speed of the interface is somewhere in
            the range of `n-500,000' to `n+499,999'.  For interfaces
            which do not vary in bandwidth or for those where no
            accurate estimation can be made, this object should contain
            the nominal bandwidth.  For a sub-layer which has no concept
            of bandwidth, this object should be zero."
    ::= { ifXEntry 15 }
'''


_64_BIT_COUNTERS = (
    'HCInOctets',
    'HCInUcastPkts',
    'HCInMulticastPkts',
    'HCInBroadcastPkts',
    'HCOutOctets',
    'HCOutUcastPkts',
    'HCOutMulticastPkts',
    'HCOutBroadcastPkts',
)

_CISCO_IF_METRICS = (
    'cieIfResetCount',
    'cieIfKeepAliveEnabled',
    'cieIfStateChangeReason',
    'cieIfCarrierTransitionCount',
    'cieIfInterfaceDiscontinuityTime',
    'cieIfSpeedReceive',
    'cieIfHighSpeedReceive',
)

_CISCO_IF_PKT_METRICS = (
    'cieIfLastInTime',
    'cieIfLastOutTime',
    'cieIfLastOutHangTime',
    'cieIfInRuntsErrs',
    'cieIfInGiantsErrs',
    'cieIfInFramingErrs',
    'cieIfInOverrunErrs',
    'cieIfInIgnored',
    'cieIfInAbortErrs',
    'cieIfInputQueueDrops',
    'cieIfOutputQueueDrops',
    'cieIfPacketDiscontinuityTime',
)


class CheckInterface(Check):
    key = 'interface'

    @staticmethod
    async def run(asset: Asset, local_config: dict, config: dict) -> dict:

        snmp = get_snmp_client(asset, local_config, config)
        state_data = await snmpquery(snmp, QUERIES, True)

        counts = Counter()
        itms = state_data.get('if', [])

        # lookup is used by lldp check
        InterfaceLookup.set(asset.id, itms)

        items = []
        if_x_entry = {i.pop('name'): i for i in state_data.pop('ifX', [])}
        cie_if_entry = {i.pop('name'): i
                        for i in state_data.pop('cieIfInterface', [])}
        cie_if_pkt_entry = {i.pop('name'): i
                            for i in state_data.pop('cieIfPacketStats', [])}
        for item in itms:
            key = item['name']

            name = item.get('Descr')
            if not isinstance(name, str):
                raise CheckException(
                    'Missing ifDesc OID for creating an interface name'
                )

            mtu = item.get('Mtu')
            if mtu is None:
                raise CheckException(
                    'Incomplete ifEntry missing ifMtu OID'
                )

            idx = counts[name]
            counts[name] += 1
            item['name'] = f'{name}_{idx}' if idx else name

            items.append(item)

            # join cieIfInterface metrics
            cie_if_item = cie_if_entry.get(key)
            if cie_if_item:
                for name in _CISCO_IF_METRICS:
                    if name in cie_if_item:
                        shortname = name[5:]  # strip "cieIf" prefix
                        item[shortname] = cie_if_item[name]

                if 'SpeedReceive' in item and 'HighSpeedReceive' in item:
                    # max value for this metric, shown if value is overloading
                    if (item['SpeedReceive'] == 4294967295 and
                            item['HighSpeedReceive'] != 4294):
                        # ifspeed is in bits, ifHighSpeed in MBits.
                        item['SpeedReceive'] = \
                            item['HighSpeedReceive'] * 1000000

            # join cieIfPacketStats metrics
            cie_if_pkt_item = cie_if_pkt_entry.get(key)
            if cie_if_pkt_item:
                for name in _CISCO_IF_PKT_METRICS:
                    if name in cie_if_pkt_item:
                        shortname = name[5:]  # strip "cieIf" prefix
                        value = cie_if_pkt_item[name]
                        # omit metrics with max value
                        if value != 4294967295:
                            item[shortname] = value

            # join ifX metrics
            try:
                item.update(if_x_entry[key])
            except KeyError:
                continue  # no 64 bit counter, skip code below

            for _64_bit_name in _64_BIT_COUNTERS:
                if _64_bit_name in item:
                    _32_bit_name = _64_bit_name[2:]
                    item[_32_bit_name] = item.pop(_64_bit_name)

            if 'Speed' in item and 'HighSpeed' in item:
                # max value for this metric, shown if value is overloading
                if (item['Speed'] == 4294967295 and
                        item['HighSpeed'] != 4294):
                    # ifspeed is in bits, ifHighSpeed in MBits.
                    item['Speed'] = item['HighSpeed'] * 1000000

        return {
            'interface': items
        }
