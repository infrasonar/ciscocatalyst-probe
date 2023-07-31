from libprobe.probe import Probe
from lib.check.catalyst import check_catalyst
from lib.version import __version__ as version


if __name__ == '__main__':
    checks = {
        'catalyst': check_catalyst,
    }

    probe = Probe("ciscocatalyst", version, checks)

    probe.start()
