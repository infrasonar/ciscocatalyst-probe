from libprobe.probe import Probe
from lib.check.cpu import CheckCpu
from lib.check.memory import CheckMemory
from lib.check.system import CheckSystem
from lib.version import __version__ as version


if __name__ == '__main__':
    checks = (
        CheckCpu,
        CheckMemory,
        CheckSystem,
    )

    probe = Probe("ciscocatalyst", version, checks)

    probe.start()
