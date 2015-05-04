import numpy as np
from compliance_checker.base import check_has, Result
from compliance_checker.defined_base import DefinedNCBaseCheck
from netCDF4 import Dataset

# more varlists - not used for checking
def roms_varlist(option):
    """
    varlist = roms_varlist(option)

    Return ROMS varlist.
    """

    if option == 'physics':
        varlist = (['temp','salt','u','v','ubar','vbar','zeta'])
    elif option == 'physics2d':
        varlist = (['ubar','vbar','zeta'])
    elif option == 'physics3d':
        varlist = (['temp','salt','u','v'])
    elif option == 'mixing3d':
        varlist = (['AKv','AKt','AKs'])
    elif option == 's-param':
        varlist = (['theta_s','theta_b','Tcline','hc'])
    elif option == 's-coord':
        varlist = (['s_rho','s_w','Cs_r','Cs_w'])
    elif option == 'coord':
        varlist = (['lon_rho','lat_rho','lon_u','lat_u','lon_v','lat_v'])
    elif option == 'grid':
        varlist = (['h','f','pm','pn','angle','lon_rho','lat_rho', \
          'lon_u','lat_u','lon_v','lat_v','lon_psi','lat_psi', \
          'mask_rho','mask_u','mask_v','mask_psi'])
    elif option == 'hgrid':
        varlist = (['f','dx','dy','angle_rho','lon_rho','lat_rho', \
          'lon_u','lat_u','lon_v','lat_v','lon_psi','lat_psi', \
          'mask_rho','mask_u','mask_v','mask_psi'])
    elif option == 'vgrid':
        varlist = (['h','s_rho','s_w','Cs_r','Cs_w', \
          'theta_s','theta_b','Tcline','hc'])
    else:
        raise Warning, 'Unknow varlist id'

    return varlist


class DefinedROMSBaseCheck(DefinedNCBaseCheck):

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
        
        if 'lat_rho' in ds.variables and 'lon_rho' in ds.variables:
            lons = ds.variables['lon_rho'][:]
            lats = ds.variables['lat_rho'][:]
        else:
            raise RuntimeError('Cannot find lat_rho/lon_rho variables in %s' % ds.filepath)
    
        bounds = [float(np.amin(lons)), float(np.amax(lons)), float(np.amin(lats)), float(np.amax(lats))]
      
        xshape = ds.variables['lon_rho'].shape
        yshape = ds.variables['lat_rho'].shape
        
        if len(xshape) > 1:
            ni = xshape[len(xshape) -1]
            nj = xshape[len(xshape) -2]
        else:
            ni = xshape[0]
            nj = yshape[0]

        ninj = [ ni, nj ]
        
        return {['bounds',bounds],['ni_nj',ninj]}
    
    
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



    def do_check_2D(self, ds):

        '''
        Verifies the dataset has the required variables for the 2D grid
        
        what about these
        
        '''
        # we could go overboard and test for units and dimensions on the variables as well ....
        # not really necessary here
        required_variables = [
            'lon_rho',
            'lat_rho',
            'lon_u',
            'lat_u',
            'lon_v',
            'lat_v',
            'lon_psi',
            'lat_psi',
            'f',
            'pm',
            'pn',
            'dmde',
            'dndx',
            'xl',
            'el',
            'spherical',
            'angle',
            'mask_rho',
            'mask_u',
            'mask_v',
            'mask_psi'
        ]
        
        
        required_dimensions = [
            'xi_rho',
            'xi_u',
            'xi_v',
            'xi_psi',
            'eta_rho',
            'eta_u',
            'eta_v',
            'eta_psi'
        ]
        
        # TODO-UR check that the dimensions have the correct size relationship?
        
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
                messages.append("%s is a required dimension" % dim)
        
        return self.make_result(level, score, out_of, 'Required Variables and Dimensions', messages,'check_2D')
        
        
    def do_check_3D(self, ds):

        '''
        Verifies the dataset has the required variables for the 3D grid
        
        '''
        # we could go overboard and test for units and dimensions on the variables as well ....
        # not really necessary here
        required_variables = [
            'theta_s',
            'theta_b',
            #'Tcline',
            'hc',
            's_rho',
            's_w',
            'Cs_r',
            'Cs_w',            
            'Vstretching',
            'Vtransform'
        ]
        
        required_dimensions = [
            's_rho',
            's_w'
        ]
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
        
        return self.make_result(level, score, out_of, 'Required Variables and Dimensions', messages,'check_3D')
        

    def do_check_bathy(self, ds):

        '''
        Verifies the dataset has the required variables for bathy
        '''
        # we could go overboard and test for units and dimesnions on the variables as well ....
        # not really necessary here
        required_variables = [
            'h',
            'hraw',
            'depthmin',
            'depthmax'
            
        ]
        
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
        
        return self.make_result(level, score, out_of, 'Required Variables and Dimensions', messages,'check_bathy')



    def check(self,dsp):
    
        scores = []
        ds = dsp.dataset
        scores.append(self.do_check_2D(ds))
                      
        if str("3D").lower() in self.options:
            scores.append(self.do_check_3D(ds))
        
                          
        if str("bathy").lower() in self.options:
            scores.append(self.do_check_bathy(ds))             
        
        
        
        return scores


