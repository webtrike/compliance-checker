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
        return Result(level, (score, out_of), name, messages,None,"generic",the_method)

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
            raise RuntimeError('Cannot find coordinate variables in %s' % str(ds.filepath))
        
        
        
        lons = ds.variables[xvar][:]
        lats = ds.variables[yvar][:]
        
        bounds = [float(np.amin(lons)), float(np.amax(lons)), float(np.amin(lats)), float(np.amax(lats))]
      
        xshape = ds.variables[xvar].shape
        yshape = ds.variables[yvar].shape
        rotation = 0.
        
        if len(xshape) > 1:
            import math
            ni = xshape[len(xshape) -1]
            nj = xshape[len(xshape) -2]
            
            # from the horizontal -> cartesian
            widthX = lons[0,ni-1] - lons[0,0] 
            heightX = lats[0,ni-1] - lats[0,0]
            rotation = DefinedNCBaseCheck.calc_rotation(self,widthX,heightX)
            # now extract the actual width and height
            widthY = lons[nj-1,0] - lons[0,0] 
            heightY = lats[nj-1,0] - lats[0,0]
            
            height=math.sqrt((widthY*widthY)+(heightY*heightY))
            width=math.sqrt((widthX*widthX)+(heightX*heightX))
        else:
            ni = xshape[0]
            nj = yshape[0]
            width = lons[len(lons)-1] - lons[0]
            height = lats[len(lats)-1] - lats[0] 
            rotation = 0.
            
            
        ninj = [ ni, nj ]
        vals = dict()
        vals['bounds'] = bounds
        vals['nij'] = ninj
        vals['rotation'] = rotation
        vals['height'] = height
        vals['width'] = width
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
                    
        '''            
        # now the question is if we should be tight about anything this component does not actually do ?
        for o in self.options:
            if o != '2D' and o != 'generic':
                scores.append(self.make_result(DefinedNCBaseCheck.LOW, 0, 1,'Requested test' ,['Option not supported',o],o))
        '''
        
        
        return scores