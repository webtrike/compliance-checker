import sys,pytest

from compliance_checker.base import DSPair
from compliance_checker.roms import DefinedROMSBaseCheck
from netCDF4 import Dataset

# not updated
@pytest.mark.xfail
def test_roms(ffile = "/usr/local/projects/trike/romsGrid.nc"):
    #from wicken.netcdf_dogma import NetCDFDogma
    ds = Dataset(ffile)
    roms = DefinedROMSBaseCheck()
    roms.set_options("3D")
    #dsp = DSPair(ds, NetCDFDogma)
    dsp = roms.load_datapair(ds)
    result = roms.check(dsp)
    limits = roms.limits(dsp)
    print result
    print limits
    
    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        test_roms(ffile = sys.argv[1])
    else:    
        test_roms()
