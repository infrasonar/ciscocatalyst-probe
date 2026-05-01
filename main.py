from libprobe.probe import Probe
from lib.check.catalyst import CheckCatalyst
from lib.version import __version__ as version


if __name__ == '__main__':
    checks = (
        CheckCatalyst,
    )

    probe = Probe("ciscocatalyst", version, checks)

    probe.start()
