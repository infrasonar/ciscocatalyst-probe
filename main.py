from libprobe.probe import Probe
from lib.check.base import CheckBase
from lib.check.cpm import CheckCpm
from lib.check.interface import CheckInterface
from lib.check.interface_ext import CheckInterfaceExt
from lib.check.interface_pkt import CheckInterfacePkt
from lib.check.ip import CheckIp
from lib.check.ip_address import CheckIpAddress
from lib.check.lldp import CheckLldp
from lib.check.memory_pool import CheckMemoryPool
from lib.check.system import CheckSystem
from lib.check.tcp import CheckTcp

from lib.version import __version__ as version


if __name__ == '__main__':
    checks = (
        CheckBase,
        CheckCpm,
        CheckInterface,
        CheckInterfaceExt,
        CheckInterfacePkt,
        CheckIp,
        CheckIpAddress,
        CheckLldp,
        CheckMemoryPool,
        CheckSystem,
        CheckTcp,
    )

    probe = Probe("ciscocatalyst", version, checks)

    probe.start()
