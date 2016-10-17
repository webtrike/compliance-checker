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
            raise RuntimeError('Cannot find lat_rho/lon_rho variables in %s' % str(ds.filepath))
    
        bounds = [float(np.amin(lons)), float(np.amax(lons)), float(np.amin(lats)), float(np.amax(lats))]
      
        xshape = ds.variables['lon_rho'].shape
        yshape = ds.variables['lat_rho'].shape
        rotation = 0.
        corners = list()
        
        
        
        if len(xshape) > 1:
            import math
            ni = xshape[len(xshape) -1]
            nj = xshape[len(xshape) -2]
            # now calculate the overall rotation, its going to be off for curvlinear grids ...
            # from the vertical -> nautical, off by 90
            # dx = lons[nj-1,0] - lons[0,0] 
            # dy = lats[nj-1,0] - lats[0,0]
            
            # from the horizontal -> cartesian
            '''
            dx = lons[0,ni-1] - lons[0,0] 
            dy = lats[0,ni-1] - lats[0,0]
                
            rotation = DefinedNCBaseCheck.calc_rotation(self,dx,dy)           
            '''
            widthX = lons[0,ni-1] - lons[0,0] 
            heightX = lats[0,ni-1] - lats[0,0]
            rotation = DefinedNCBaseCheck.calc_rotation(self,widthX,heightX)
            # now extract the actual width and height
            widthY = lons[nj-1,0] - lons[0,0] 
            heightY = lats[nj-1,0] - lats[0,0]
            
            height=math.sqrt((widthY*widthY)+(heightY*heightY))
            width=math.sqrt((widthX*widthX)+(heightX*heightX))
            origin = (lons[0,0],lats[0,0])
            corners.append(origin)
            corners.append((lons[nj-1,0],lats[nj-1,0]))
            corners.append((lons[nj-1,ni-1],lats[nj-1,ni-1]))
            corners.append((lons[0,ni-1],lats[0,ni-1]))
            
        else:
            ni = xshape[0]
            nj = yshape[0]
            width = lons[len(lons)-1] - lons[0]
            height = lats[len(lats)-1] - lats[0] 
            origin = (lons[0],lats[0])
            corners.append(origin)
            corners.append((lons[0],lats[nj-1]))
            corners.append((lons[ni-1],lats[nj-1]))
            corners.append((lons[ni-1],lats[0]))
            
            
            
        if "eta_rho" in ds.dimensions:
            print "replacing shape derived nj with dimension eta_rho"
            nj = len(ds.dimensions["eta_rho"])


        if "xi_rho" in ds.dimensions:
            print "replacing shape derived ni with dimension xi_rho"
            ni = len(ds.dimensions["xi_rho"])
        
        ninj = [ ni, nj ]
        vals = dict()
        vals['bounds'] = bounds
        vals['ni_nj'] = ninj
        vals['height'] = height
        vals['width'] = width
        vals['rotation'] = rotation
        vals['origin'] = origin
        vals['corners'] = corners
        
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
        
        # they must exist in above
        matching_dimension = [
                              ('eta_rho','eta_u'),
                              ('eta_psi','eta_v'),
                              ('xi_psi','xi_u'),
                              ('xi_rho','xi_v')]
        # TODO-UR check that the dimensions have the correct size relationship?
        
        level = DefinedNCBaseCheck.HIGH
        out_of = len(required_variables) + len(required_dimensions) + len(matching_dimension)
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
        
        for dimtuple in matching_dimension:
            testdim1 =  ds.dimensions[dimtuple[0]]
            testdim2 =  ds.dimensions[dimtuple[1]]
            test = int(len(testdim1) == len(testdim2))
            score += test
            if not test:
                messages.append("%s are required to be of same size!" % str(dimtuple))
        
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
    
    
    def do_check_mask(self, ds):

        '''
        Verifies the dataset has the required variables for bathy
        '''
        # we could go overboard and test for units and dimesnions on the variables as well ....
        # not really necessary here
        required_variables = [
            'mask_rho',
            'mask_u',
            'mask_v',
            'mask_psi'
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
        
        return self.make_result(level, score, out_of, 'Required Variables and Dimensions', messages,'check_mask')



    def check(self,dsp):
        from wicken.netcdf_dogma import NetCDFDogma
        
        if not isinstance(dsp.dogma,NetCDFDogma):
            raise RuntimeError("Expecting Netcdf dogma, found: "+str(dsp.dogma))
        
        scores = []
        ds = dsp.dataset
        scores.append(self.do_check_2D(ds))
                      
        if str("3D").lower() in self.options:
            scores.append(self.do_check_3D(ds))
        
                          
        if str("bathy").lower() in self.options:
            scores.append(self.do_check_bathy(ds))
            
        if str("mask").lower() in self.options:
            scores.append(self.do_check_mask(ds))             
        
        
        
        return scores


