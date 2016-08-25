import numpy as np
from compliance_checker.base import check_has, Result
from compliance_checker.defined_base import DefinedNCBaseCheck
from netCDF4 import Dataset
from __builtin__ import RuntimeError
#from docutils.math.math2html import LimitsProcessor


##
## UR-TODO - simple copy from ROMS, needs adjusting to SHOC
##
##

class DefinedSWANBaseCheck(DefinedNCBaseCheck):

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
        return Result(level, (score, out_of), name, messages,None,"swan",the_method)

    def setup(self, ds):
        pass
    

    
    def limits(self,dsp):
        from wicken.netcdf_dogma import NetCDFDogma
        
        times = list()
        
        if isinstance(dsp.dogma,NetCDFDogma):
            from netCDF4 import num2date
            from compliance_checker import inferXVar,inferYVar,DTExportFormat
            ds = dsp.dataset
        
            xvar = inferXVar(ds)
            yvar = inferYVar(ds)
            if yvar is not None:
                # metric
                lons = yvar[:]
                lats = xvar[:]
            else:
                raise RuntimeError('Cannot find x/y variables in %s' % ds.filepath)
        
            bounds = [float(np.amin(lons)), float(np.amax(lons)), float(np.amin(lats)), float(np.amax(lats))]
          
            xshape = xvar.shape
            yshape = yvar.shape
            
            tt = None
            # test if we have a valid time
            if 't' in ds.variables and len(ds.variables['t']) > 0:
                tt = ds.variables['t']
            elif 'time' in ds.variables and len(ds.variables['time']) > 0:
                tt = ds.variables['time']
                
                
            if tt is not None:
                times.append(str(len(tt)))
                times.append(DTExportFormat.format(num2date(tt[0],tt.units)))
                times.append(DTExportFormat.format(num2date(tt[len(tt)-1],tt.units)))
                
                
        else:
            raise RuntimeError("Only supporting NETCDF files so far")
             
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
        if tt is not None:
            vals['time'] = times
        
        
        return vals
    
    
    @check_has(DefinedNCBaseCheck.HIGH)
    def check_high(self, ds):
        return ['title', 'summary', 'keywords']

    ###############################################################################
    #
    # RECOMMENDED
    #
    ###############################################################################

    @check_has(DefinedNCBaseCheck.MEDIUM)
    def check_recommended(self, ds):
        return [
            'history',
            'comment',
            'date_created',
            'creator_name',
            'creator_url',
            'creator_email',
            'institution',
            'license'
        ]

    ###############################################################################
    #
    # SUGGESTED
    #
    ###############################################################################

    @check_has(DefinedNCBaseCheck.LOW)
    def check_suggested(self, ds):
        return [
            'date_modified',
            'date_issued']



    def do_check_2D(self, ds, ftype = "cf"):

        '''
        Verifies the data set has the required variables for the 2D grid
        
        we don't prescribe a type so let NETCDF dataset figure out what coordinate vars there are
        '''
        from compliance_checker import inferXVar,inferYVar
        
        xvar = inferXVar(ds)
        yvar = inferYVar(ds)
        
        
        messages = []
        success_messages = ""
        score = 0
        level = DefinedNCBaseCheck.HIGH
        
        
        if xvar is not None:
            score = score +1
            success_messages += " xvar: "
            success_messages += xvar.name
        else:
            messages.append("Did not find matching longitude variable")
        
        if yvar is not None:
            score = score +1
            success_messages += " yvar: "
            success_messages += yvar.name
        else:
            messages.append("Did not find matching latitude variable")
            
            
        
        
        return self.make_result(level, score, 2, 'Required 2D Variables '+success_messages, messages,'check_2D')
        
        
    def do_check_3D(self, ds, ftype = "std"):

        '''
        Verifies the dataset has the required variables for the 3D grid
        
        '''
        
            
                
        return self.make_result(DefinedNCBaseCheck.LOW, 0, 0, 'Required bathy Variable', [],'check_3D')
        

    def do_check_bathy(self, ds, ftype = "std"):

        '''
        Verifies the dataset has the required variables for bathy
        '''
        from compliance_checker import inferZVar
        
        zvar = inferZVar(ds)
                        
        messages = []
        success_messages = ""
        score = 0
        level = DefinedNCBaseCheck.HIGH
        
        if zvar is not None:
            score = score +1
            success_messages += " zvar: "
            success_messages += zvar.name
        else:
            messages.append("Did not find matching bathy variable")
        
        return self.make_result(level, score, 1, 'Required bathy Variable '+success_messages, messages,'check_bathy')
    
    
    def do_check_mask(self, ds):

        '''
        Verifies the dataset has the required variables for bathy
        '''
        # we could go overboard and test for units and dimesnions on the variables as well ....
        # not really necessary here
        required_variables = []
        
        required_dimensions = []
        level = DefinedNCBaseCheck.HIGH
        out_of = len(required_variables) + len(required_dimensions)
        score = 0
        messages = []
        for variable in required_variables:
            test = variable in ds.variables
            score += int(test)
            if not test:
                messages.append("%s is a required variable" % variable)
                
        for dim in required_dimensions:
            test = dim in ds.dimensions
            score += int(test)
            if not test:
                messages.append("%s is a required variable" % dim)
        
        return self.make_result(level, score, out_of, 'Required Variables and Dimensions', messages,'check_mask')



    def check(self,dsp):
    
        scores = []
        ds = dsp.dataset
        ftype = "cf"
        
                    
        scores.append(self.do_check_2D(ds,ftype))
        
                          
        #if str("3D").lower() in self.options:
        #    scores.append(self.do_check_3D(ds,ftype))
        
                          
        if str("bathy").lower() in self.options:
            scores.append(self.do_check_bathy(ds,ftype))
          
        
        
        
        return scores


