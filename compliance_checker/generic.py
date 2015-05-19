import numpy as np
from compliance_checker.base import check_has, Result
from compliance_checker.defined_base import DefinedNCBaseCheck
from netCDF4 import Dataset



# we could go overboard and test for units and dimensions on the variables as well ....
# not really necessary here
possible_coord_variables = [
                      ('lon','longitude','LONGITUDE','lon_rho'),
                      ('lat','latitude','LATITUDE','lat_rho')
                      ]
        
        
possible_coord_dimensions = [
                       ('x','i','lon','xu_ocean','xt_ocean','xi_rho'),
                       ('y','j','lat','yu_ocean','yt_ocean','eta_rho')
                       ]
        
        
class DefinedGenericBaseCheck(DefinedNCBaseCheck):

    ###############################################################################
    #
    # HIGHLY RECOMMENDED
    # 
    ###############################################################################
    supported_ds = [Dataset]
    
    @classmethod
    def beliefs(cls): 
        '''
        Not applicable for Defined
        '''
        return {}

    @classmethod
    def make_result(cls, level, score, out_of, name, messages, the_method):
        return Result(level, (score, out_of), name, messages,None,"roms",the_method)

    def setup(self, ds):
        pass

    def limits(self,dsp):
        ds = dsp.dataset
        
        xvar = None
        yvar = None
        scores = 0
        for var in possible_coord_variables[0]:
            if var in ds.variables:
                xvar = var;
                scores += 1
                break
        for var in possible_coord_variables[1]:
            if var in ds.variables:
                yvar = var;
                scores += 1
                break
        if xvar == None or yvar == None:
            raise RuntimeError('Cannot find coordinate variables in %s' % ds.filepath)
        
        
        
        lons = ds.variables[xvar][:]
        lats = ds.variables[yvar][:]
        
        bounds = [float(np.amin(lons)), float(np.amax(lons)), float(np.amin(lats)), float(np.amax(lats))]
      
        xshape = ds.variables[xvar].shape
        yshape = ds.variables[yvar].shape
        
        if len(xshape) > 1:
            ni = xshape[len(xshape) -1]
            nj = xshape[len(xshape) -2]
        else:
            ni = xshape[0]
            nj = yshape[0]
            
        ninj = [ ni, nj ]
        vals = dict()
        vals['bounds'] = bounds
        vals['nij'] = ninj
        
        
        return vals
        
        
    def do_check_2D(self, ds):

        '''
        Verifies the dataset has the required variables for the 2D grid
        
        what about these
        
        '''
        xvar = None
        yvar = None
        scores = 0
        for var in possible_coord_variables[0]:
            if var in ds.variables:
                xvar = var;
                scores += 1
                break
        for var in possible_coord_variables[1]:
            if var in ds.variables:
                yvar = var;
                scores += 1
                break
        messages = []
        
        
        if xvar == None or yvar == None:
            #raise RuntimeError('Cannot find coordinate variables in %s' % )
            messages.append('Cannot find coordinate variables in %s' % ds.filepath)
        
        return self.make_result(DefinedNCBaseCheck.HIGH, scores, 2, 'Required Variables and Dimensions', messages,'check_2D') 
        
        
        
    def check(self,dsp):
        
        scores = []
        ds = dsp.dataset
        scores.append(self.do_check_2D(ds))
                      
        #if str("3D").lower() in self.options:
        #    scores.append(self.do_check_3D(ds))
                    
        
        
        
        return scores