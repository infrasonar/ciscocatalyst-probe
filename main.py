from libprobe.probe import Probe
from lib.check.chassis import CheckChassis
from lib.check.packet import CheckPacket
from lib.check.sensor import CheckSensor
from lib.version import __version__ as version


if __name__ == '__main__':
    checks = (
        CheckChassis,
        CheckPacket,
        CheckSensor,
    )

    probe = Probe("ciscocatalyst", version, checks)

    probe.start()
