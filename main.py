from libprobe.probe import Probe
from lib.check.cpm import CheckCpm
from lib.check.memory_pool import CheckMemoryPool
from lib.check.system import CheckSystem
from lib.version import __version__ as version


if __name__ == '__main__':
    checks = (
        CheckCpm,
        CheckMemoryPool,
        CheckSystem,
    )

    probe = Probe("ciscocatalyst", version, checks)

    probe.start()
