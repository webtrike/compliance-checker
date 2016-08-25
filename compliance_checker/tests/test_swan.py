import sys,pytest

from compliance_checker.base import DSPair
from compliance_checker.swan import DefinedSWANBaseCheck
from netCDF4 import Dataset

# not updated
@pytest.mark.xfail
def test_swan(ffile = "/usr/local/projects/trike/in.nc",ftype = "cf"):
    #from wicken.netcdf_dogma import NetCDFDogma
    ds = Dataset(ffile)
    shoc = DefinedSWANBaseCheck()
    shoc.set_options("3D bathy "+ftype)
    dsp = shoc.load_datapair(ds)
    #dsp = DSPair(ds, NetCDFDogma)
    result = shoc.check(dsp)
    limits = shoc.limits(dsp)
    print result
    print limits
    
    
if __name__ == '__main__':
    if len(sys.argv) > 2:
        test_swan(ffile = sys.argv[1],ftype = sys.argv[2])
    elif len(sys.argv) > 1:
        test_swan(ffile = sys.argv[1])
    else:    
        test_swan()
