import sys,pytest

from compliance_checker.base import DSPair
from compliance_checker.shoc import DefinedSHOCBaseCheck
from netCDF4 import Dataset

# not updated
@pytest.mark.xfail
def test_shoc(ffile = "/usr/local/projects/trike/in.nc",ftype = "std"):
    #from wicken.netcdf_dogma import NetCDFDogma
    ds = Dataset(ffile)
    shoc = DefinedSHOCBaseCheck()
    shoc.set_options("3D bathy "+ftype)
    dsp = shoc.load_datapair(ds)
    #dsp = DSPair(ds, NetCDFDogma)
    result = shoc.check(dsp)
    limits = shoc.limits(dsp,ftype)
    print result
    print limits
    
    
if __name__ == '__main__':
    if len(sys.argv) > 2:
        test_shoc(ffile = sys.argv[1],ftype = sys.argv[2])
    elif len(sys.argv) > 1:
        test_shoc(ffile = sys.argv[1])
    else:    
        test_shoc()
