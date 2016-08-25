import numpy as np
from compliance_checker.base import check_has, Result
from compliance_checker.defined_base import DefinedNCBaseCheck
from netCDF4 import Dataset
from compliance_checker import DTExportFormat
#from docutils.math.math2html import LimitsProcessor


##
## UR-TODO - simple copy from ROMS, needs adjusting to SHOC
##
##

class DefinedSHOCBaseCheck(DefinedNCBaseCheck):

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
        return Result(level, (score, out_of), name, messages,None,"shoc",the_method)

    def setup(self, ds):
        pass
    
    
    def limits(self,dsp, ftype = "std"):
        from netCDF4 import num2date
        ds = dsp.dataset
        
        times = list()
        if ftype == "std":
            if 'y_grid' in ds.variables and 'x_grid' in ds.variables:
                lons = ds.variables['x_grid'][:]
                lats = ds.variables['y_grid'][:]
            else:
                raise RuntimeError('Cannot find x_grid/y_grid variables in %s' % ds.filepath)
        
            bounds = [float(np.amin(lons)), float(np.amax(lons)), float(np.amin(lats)), float(np.amax(lats))]
          
            xshape = ds.variables['x_grid'].shape
            yshape = ds.variables['y_grid'].shape
            
            if 't' in ds.variables and len(ds.variables['t']) > 0:
                tt = ds.variables['t']
                times.append(str(len(tt)))
                times.append(DTExportFormat.format(num2date(tt[0],tt.units)))
                times.append(DTExportFormat.format(num2date(tt[len(tt)-1],tt.units)))
                
        else:
            if 'latitude' in ds.variables and 'longitude' in ds.variables:
                lons = ds.variables['longitude'][:]
                lats = ds.variables['latitude'][:]
            else:
                raise RuntimeError('Cannot find latitude/longitude variables in %s' % ds.filepath)
        
            bounds = [float(np.amin(lons)), float(np.amax(lons)), float(np.amin(lats)), float(np.amax(lats))]
          
            xshape = ds.variables['longitude'].shape
            yshape = ds.variables['latitude'].shape
            
            if 'time' in ds.variables and len(ds.variables['time']) > 0:
                tv = ds.variables['time']
                times.append(str(len(tv)))
                times.append(DTExportFormat.format(num2date(tv[0],tv.units)))
                times.append(DTExportFormat.format(num2date(tv[len(tv)-1],tv.units)))
             
        if len(xshape) > 1:
            ni = xshape[len(xshape) -1]
            nj = xshape[len(xshape) -2]
            
            # from the horizontal -> cartesian
            dx = lons[0,ni-1] - lons[0,0] 
            dy = lats[0,ni-1] - lats[0,0]
            rotation = DefinedNCBaseCheck.calc_rotation(self,dx,dy)
        else:
            ni = xshape[0]
            nj = yshape[0]

        ninj = [ ni, nj ]
        vals = dict()
        vals['bounds'] = bounds
        vals['nij'] = ninj
        vals['time'] = times
        vals['rotation'] = rotation
        
        
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



    def do_check_2D(self, ds, ftype = "std"):

        '''
        Verifies the data set has the required variables for the 2D grid
        
        what about these
        
        '''
        if ftype == "std":
            # we could go overboard and test for units and dimensions on the variables as well ....
            # not really necessary here
            required_variables = [
                'x_grid',
                'y_grid',
                'x_left',
                'y_left',
                'x_back',
                'y_back',
                'x_centre',
                'y_centre'
            ]
    
            
            # they must exist in above
            required_dimensions = [
            'j_grid',
            'i_grid',
            'j_centre',
            'i_centre',
            'j_left',
            'i_left',
            'j_back',
            'i_back'
            ]
            
            matching_dimension = [
            ('j_grid','i_grid'),
            ('j_centre','i_centre'),
            ('j_left','i_left'),
            ('j_back','i_back')
            ]
        else:
            required_variables = [
            'longitude',
            'latitude',
            'time'
            ]
            
            # they must exist in above
            required_dimensions = [
            'j',
            'i'
            ]
            
            matching_dimension = []
                
        
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
        
        
    def do_check_3D(self, ds, ftype = "std"):

        '''
        Verifies the dataset has the required variables for the 3D grid
        
        '''
        
        if ftype == "std":
            # we could go overboard and test for units and dimensions on the variables as well ....
            # not really necessary here
            required_dimensions = [
            'record', 
            'j_centre',
            'i_centre'
            ]
            
            required_variables = [
                't',
                'botz'
            ]
        else: # fix me for cf
            required_dimensions = [
            'j',
            'i',
            'k'
            ]
            
            required_variables = [
                'botz',
                'zc',
                'longitude',
                'latitude',
                'time'
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
        

    def do_check_bathy(self, ds, ftype = "std"):

        '''
        Verifies the dataset has the required variables for bathy
        '''
        # we could go overboard and test for units and dimensions on the variables as well ....
        # not really necessary here
        if ftype == "std":
            # we could go overboard and test for units and dimensions on the variables as well ....
            # not really necessary here
            required_dimensions = [
            'j_centre',
            'i_centre'
            ]
            
            required_variables = [
                'botz'
            ]
        else: # fix me for cf
            required_dimensions = [
            'j',
            'i'
            ]
            
            required_variables = [
                'botz',
                'longitude',
                'latitude'
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
        
        return self.make_result(level, score, out_of, 'Required Variables and Dimensions', messages,'check_bathy')
    
    
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
        from wicken.netcdf_dogma import NetCDFDogma
        
        if not isinstance(dsp.dogma,NetCDFDogma):
            raise RuntimeError("Expecting Netcdf dogma, found: "+str(dsp.dogma))
        
        scores = []
        
        ds = dsp.dataset
        ftype = "std"
        
        if str("cf") in self.options :
            ftype = "cf"
                    
        scores.append(self.do_check_2D(ds,ftype))
        
                          
        if str("3D").lower() in self.options:
            scores.append(self.do_check_3D(ds,ftype))
        
                          
        if str("bathy").lower() in self.options:
            scores.append(self.do_check_bathy(ds,ftype))
          
        
        
        
        return scores


'''
dimensions:
        record = UNLIMITED ; // (1 currently)
        k_grid = 48 ;
        j_grid = 57 ;
        i_grid = 33 ;
        k_centre = 47 ;
        j_centre = 56 ;
        i_centre = 32 ;
        j_left = 56 ;
        i_left = 33 ;
        j_back = 57 ;
        i_back = 32 ;
variables:
        double z_grid(k_grid) ;
                z_grid:units = "metre" ;
                z_grid:long_name = "Z coordinate at grid layer faces" ;
                z_grid:coordinate_type = "Z" ;
        double z_centre(k_centre) ;
                z_centre:units = "metre" ;
                z_centre:long_name = "Z coordinate at grid layer centre" ;
                z_centre:coordinate_type = "Z" ;
        double x_grid(j_grid, i_grid) ;
                x_grid:long_name = "Longitude at grid corners" ;
                x_grid:coordinate_type = "longitude" ;
                x_grid:units = "degrees_east" ;
                x_grid:projection = "geographic" ;
        double y_grid(j_grid, i_grid) ;
                y_grid:long_name = "Latitude at grid corners" ;
                y_grid:coordinate_type = "latitude" ;

                y_grid:projection = "geographic" ;
        double x_centre(j_centre, i_centre) ;
                x_centre:long_name = "Longitude at cell centre" ;
                x_centre:coordinate_type = "longitude" ;
                x_centre:units = "degrees_east" ;
                x_centre:projection = "geographic" ;
        double y_centre(j_centre, i_centre) ;
                y_centre:long_name = "Latitude at cell centre" ;
                y_centre:coordinate_type = "latitude" ;
                y_centre:units = "degrees_north" ;
                y_centre:projection = "geographic" ;
        double x_left(j_left, i_left) ;
                x_left:long_name = "Longitude at centre of left face" ;
                x_left:coordinate_type = "longitude" ;
                x_left:units = "degrees_east" ;
                x_left:projection = "geographic" ;
        double y_left(j_left, i_left) ;
                y_left:long_name = "Latitude at centre of left face" ;
                y_left:coordinate_type = "latitude" ;
                y_left:units = "degrees_north" ;
                y_left:projection = "geographic" ;
        double x_back(j_back, i_back) ;
                x_back:long_name = "Longitude at centre of back face" ;
                x_back:coordinate_type = "longitude" ;
                x_back:units = "degrees_east" ;
                x_back:projection = "geographic" ;
        double y_back(j_back, i_back) ;
                y_back:long_name = "Latitude at centre of back face" ;
                y_back:coordinate_type = "latitude" ;
                y_back:units = "degrees_north" ;
                y_back:projection = "geographic" ;
        double botz(j_centre, i_centre) ;
                botz:units = "metre" ;
                botz:long_name = "Z coordinate at sea-bed at cell centre" ;
        double h1au1(j_left, i_left) ;
                h1au1:units = "metre" ;
                h1au1:long_name = "Cell width at centre of left face" ;
                h1au1:coordinates = "x_left, y_left" ;
        double h1au2(j_back, i_back) ;
                h1au2:units = "metre" ;
                h1au2:long_name = "Cell width at centre of back face" ;
                h1au2:coordinates = "x_back, y_back" ;
        double h1acell(j_centre, i_centre) ;
                h1acell:units = "metre" ;
                h1acell:long_name = "Cell width at cell centre" ;
                h1acell:coordinates = "x_centre, y_centre" ;
        double h1agrid(j_grid, i_grid) ;
                h1agrid:units = "metre" ;
                h1agrid:long_name = "Cell width at grid corner" ;
                h1agrid:coordinates = "x_grid, y_grid" ;
        double h2au1(j_left, i_left) ;
                h2au1:units = "metre" ;
                h2au1:long_name = "Cell height at centre of left face" ;
                h2au1:coordinates = "x_left, y_left" ;
        double h2au2(j_back, i_back) ;
                h2au2:units = "metre" ;
                h2au2:long_name = "Cell height at centre of back face" ;
                h2au2:coordinates = "x_back, y_back" ;
        double h2acell(j_centre, i_centre) ;
                h2acell:units = "metre" ;
                h2acell:coordinates = "x_centre, y_centre" ;
        double h2agrid(j_grid, i_grid) ;
                h2agrid:units = "metre" ;
                h2agrid:long_name = "Cell height at grid corner" ;
                h2agrid:coordinates = "x_grid, y_grid" ;
        double thetau1(j_left, i_left) ;
                thetau1:units = "radian" ;
                thetau1:long_name = "Cell rotation at centre of left face" ;
                thetau1:coordinates = "x_left, y_left" ;
        double thetau2(j_back, i_back) ;
                thetau2:units = "radian" ;
                thetau2:long_name = "Cell rotation at centre of back face" ;
                thetau2:coordinates = "x_back, y_back" ;
        double coriolis(j_centre, i_centre) ;
                coriolis:units = " " ;
                coriolis:long_name = "Coriolis parameter" ;
                coriolis:coordinates = "x_centre, y_centre" ;
        short crci(i_centre) ;
        short clci(i_centre) ;
        short crfi(i_grid) ;
        short clfi(i_grid) ;
        short frci(i_centre) ;
        short flci(i_centre) ;
        short frfi(i_grid) ;
        short flfi(i_grid) ;
        short cfcj(j_centre) ;
        short cbcj(j_centre) ;
        short cffj(j_grid) ;
        short cbfj(j_grid) ;
        short ffcj(j_centre) ;
        short fbcj(j_centre) ;
        short fffj(j_grid) ;
        short fbfj(j_grid) ;
        double t(record) ;
                t:units = "days since 2014-08-11 00:00:00 +10:00" ;
                t:long_name = "Time" ;
                t:coordinate_type = "time" ;
        double u1av(record, j_left, i_left) ;
                u1av:units = "metre second-1" ;
                u1av:long_name = "I component of depth averaged current at left face" ;
                u1av:coordinates = "t, x_left, y_left" ;
        double u2av(record, j_back, i_back) ;
                u2av:units = "metre second-1" ;
                u2av:long_name = "J component of depth averaged current at back face" ;
                u2av:coordinates = "t, x_back, y_back" ;
        double wtop(record, j_centre, i_centre) ;
                wtop:units = "metre second-1" ;
                wtop:long_name = "Vertical velocity at surface" ;
                wtop:coordinates = "t, x_centre, y_centre" ;
        double topz(record, j_centre, i_centre) ;
                topz:units = "metre" ;
                topz:long_name = "Z coordinate for surface cell" ;
                topz:coordinates = "t, x_centre, y_centre" ;
        double eta(record, j_centre, i_centre) ;
                eta:units = "metre" ;
                eta:long_name = "Surface Elevation" ;
                eta:coordinates = "t, x_centre, y_centre" ;
        double eta_mean(record, j_centre, i_centre) ;
                eta_mean:tracer2D = "true" ;

                alerts_cumulative:_FillValueWC = 0. ;
                alerts_cumulative:valid_range_wc = 0., 1.e+36 ;
        double U1VH0(record, j_centre, i_centre) ;
                U1VH0:tracer2D = "true" ;
                U1VH0:coordinates = "t, x_centre, y_centre" ;
                U1VH0:long_name = "Initial e1 horizontal viscosity" ;
                U1VH0:units = "" ;
                U1VH0:type = 522 ;
                U1VH0:diagn = 0 ;
                U1VH0:_FillValueWC = 0. ;
                U1VH0:valid_range_wc = 0., 1.e+36 ;
        double U2VH0(record, j_centre, i_centre) ;
                U2VH0:tracer2D = "true" ;
                U2VH0:coordinates = "t, x_centre, y_centre" ;
                U2VH0:long_name = "Initial e2 horizontal viscosity" ;
                U2VH0:units = "" ;
                U2VH0:type = 522 ;
                U2VH0:diagn = 0 ;
                U2VH0:_FillValueWC = 0. ;
                U2VH0:valid_range_wc = 0., 1.e+36 ;
        double sonic_depth(record, j_centre, i_centre) ;
                sonic_depth:tracer2D = "true" ;
                sonic_depth:coordinates = "t, x_centre, y_centre" ;
                sonic_depth:long_name = "Sonic depth" ;
                sonic_depth:units = "m" ;
                sonic_depth:type = 522 ;
                sonic_depth:diagn = 0 ;
                sonic_depth:_FillValueWC = 0. ;
                sonic_depth:valid_range_wc = -10000., 100. ;
        double tau_be1(record, j_centre, i_centre) ;
                tau_be1:tracer2D = "true" ;
                tau_be1:coordinates = "t, x_centre, y_centre" ;
                tau_be1:long_name = "Bottom stress in e1 direction" ;
                tau_be1:units = "Nm-2" ;
                tau_be1:type = 522 ;
                tau_be1:diagn = 0 ;
                tau_be1:_FillValueWC = 0. ;
                tau_be1:valid_range_wc = -10000., 10000. ;
        double tau_be2(record, j_centre, i_centre) ;
                tau_be2:tracer2D = "true" ;
                tau_be2:coordinates = "t, x_centre, y_centre" ;
                tau_be2:long_name = "Bottom stress in e2 direction" ;
                tau_be2:units = "Nm-2" ;
                tau_be2:type = 522 ;
                tau_be2:diagn = 0 ;
                tau_be2:_FillValueWC = 0. ;
                tau_be2:valid_range_wc = -10000., 10000. ;
        double tau_bm(record, j_centre, i_centre) ;
                tau_bm:tracer2D = "true" ;
        double swr_bot_absorb(record, j_centre, i_centre) ;
                swr_bot_absorb:tracer2D = "true" ;
                swr_bot_absorb:coordinates = "t, x_centre, y_centre" ;
                swr_bot_absorb:long_name = "SWR bottom absorption" ;
                swr_bot_absorb:units = "" ;
                swr_bot_absorb:type = 522 ;
                swr_bot_absorb:diagn = 0 ;
                swr_bot_absorb:_FillValueWC = 1. ;
                swr_bot_absorb:valid_range_wc = 0., 1. ;
        double swr_attenuation(record, j_centre, i_centre) ;
                swr_attenuation:tracer2D = "true" ;
                swr_attenuation:coordinates = "t, x_centre, y_centre" ;
                swr_attenuation:long_name = "SWR attenuation" ;
                swr_attenuation:units = "m-1" ;
                swr_attenuation:type = 1034 ;
                swr_attenuation:diagn = 0 ;
                swr_attenuation:_FillValueWC = 0.073 ;
                swr_attenuation:valid_range_wc = 0., 10. ;
        double swr_transmission(record, j_centre, i_centre) ;
                swr_transmission:tracer2D = "true" ;
                swr_transmission:coordinates = "t, x_centre, y_centre" ;
                swr_transmission:long_name = "SWR transmission" ;
                swr_transmission:units = "" ;
                swr_transmission:type = 1034 ;
                swr_transmission:diagn = 0 ;
                swr_transmission:_FillValueWC = 0.26 ;
                swr_transmission:valid_range_wc = 0., 1. ;
        double wind1(record, j_left, i_left) ;
                wind1:units = "Nm-2" ;
                wind1:long_name = "I component of wind stress at left face" ;
                wind1:coordinates = "t, x_left, y_left" ;
        double wind2(record, j_back, i_back) ;
                wind2:units = "Nm-2" ;
                wind2:long_name = "J component of wind stress at back face" ;
                wind2:coordinates = "t, x_back, y_back" ;
        double patm(record, j_centre, i_centre) ;
                patm:units = "Pa" ;
                patm:long_name = "Atmospheric pressure" ;
                patm:coordinates = "t, x_centre, y_centre" ;
        double u1(record, k_centre, j_left, i_left) ;
                u1:units = "metre second-1" ;
                u1:long_name = "I component of current at left face" ;
                u1:coordinates = "t, x_left, y_left, z_centre" ;
        double u2(record, k_centre, j_back, i_back) ;
                u2:units = "metre second-1" ;
                u2:long_name = "J component of current at back face" ;
                u2:coordinates = "t, x_back, y_back, z_centre" ;
        double w(record, k_centre, j_centre, i_centre) ;
                w:units = "metre second-1" ;
                w:long_name = "K component of current at cell centre and Z grid" ;
                w:coordinates = "t, x_centre, y_centre, z_centre" ;
        double salt(record, k_centre, j_centre, i_centre) ;
                salt:tracer = "true" ;

 salt:advect = 1 ;
                salt:diffuse = 1 ;
                salt:decay = "0.0" ;
        double temp(record, k_centre, j_centre, i_centre) ;
                temp:tracer = "true" ;
                temp:coordinates = "t, x_centre, y_centre, z_centre" ;
                temp:long_name = "Temperature" ;
                temp:units = "degrees C" ;
                temp:type = 4 ;
                temp:diagn = 0 ;
                temp:_FillValueWC = 20. ;
                temp:valid_range_wc = -4., 40. ;
                temp:_FillValueSED = 0. ;
                temp:valid_range_sed = 0., 0. ;
                temp:inwc = 1 ;
                temp:insed = 0 ;
                temp:dissol = 1 ;
                temp:partic = 0 ;
                temp:advect = 1 ;
                temp:diffuse = 1 ;
                temp:decay = "0.0" ;
        double smagorinsky(record, k_centre, j_centre, i_centre) ;
                smagorinsky:tracer = "true" ;
flag(record, k_centre, j_grid, i_grid) ;
                flag:long_name = "SHOC masking flags" ;
                flag:coordinates = "t, x_centre, y_centre, z_centre" ;
        double dens(record, k_centre, j_centre, i_centre) ;
                dens:units = "kg metre-3" ;
                dens:long_name = "Density" ;
                dens:coordinates = "t, x_centre, y_centre, z_centre" ;
        double dens_0(record, k_centre, j_centre, i_centre) ;
                dens_0:units = "kg metre-3" ;
                dens_0:long_name = "Potential density" ;
                dens_0:coordinates = "t, x_centre, y_centre, z_centre" ;
                dens_0:_FillValue = 1025. ;
        double Kz(record, k_centre, j_centre, i_centre) ;
                Kz:units = "m2 s-1" ;
                Kz:long_name = "Kz" ;
                Kz:coordinates = "t, x_centre, y_centre, z_centre" ;
                Kz:_FillValue = 0. ;
        double Vz(record, k_centre, j_centre, i_centre) ;
                Vz:units = "m2 s-1" ;
                Vz:long_name = "Vz" ;
                Vz:coordinates = "t, x_centre, y_centre, z_centre" ;
                Vz:_FillValue = 0. ;
        double u1bot(record, j_left, i_left) ;
                u1bot:units = "metre second-1" ;
                u1bot:long_name = "I component of bottom current deviation at left face" ;
                u1bot:coordinates = "t, x_left, y_left" ;
        double u2bot



'''

