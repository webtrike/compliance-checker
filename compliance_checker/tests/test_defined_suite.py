from compliance_checker.defined import ComplianceCheckerCheckSuiteDefined
from netCDF4 import Dataset
import sys,pytest


# not updated
@pytest.mark.xfail
def test_suite(file = "/usr/local/projects/trike/romsGrid.nc"):
    cs = ComplianceCheckerCheckSuiteDefined()
    ds = Dataset(file)
    cs.set_optpions('3D')
    vals = cs.run(ds, 'roms')
    print vals


if __name__ == '__main__':
    if len(sys.argv) > 1:
        test_suite(file = sys.argv[1])
    else:    
        test_suite()