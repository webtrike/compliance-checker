import sys,pytest

from compliance_checker.base import DSPair
from compliance_checker.roms import DefinedROMSBaseCheck
from netCDF4 import Dataset

# not updated
@pytest.mark.xfail
def test_roms(file = "/usr/local/projects/trike/romsGrid.nc"):

    ds = Dataset(file)
    roms = DefinedROMSBaseCheck()
    roms.set_options("3D")
    result = roms.check(DSPair(ds, None))
    print result
    
    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        test_roms(file = sys.argv[1])
    else:    
        test_roms()
