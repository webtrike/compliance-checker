#!/usr/bin/env python

from compliance_checker.cf import CFCheck
from compliance_checker.suite import DSPair, NetCDFDogma
from netCDF4 import Dataset
from tempfile import gettempdir

import unittest
import os


rutgers_glider_path = 'test-data/ru07-20130824T170228_rt0.nc'

class TestCF(unittest.TestCase):
    # @see
    # http://www.saltycrane.com/blog/2012/07/how-prevent-nose-unittest-using-docstring-when-verbosity-2/
    def shortDescription(self):
        return None

    # override __str__ and __repr__ behavior to show a copy-pastable nosetest name for ion tests
    #  ion.module:TestClassName.test_function_name
    def __repr__(self):
        name = self.id()
        name = name.split('.')
        if name[0] not in ["ion", "pyon"]:
            return "%s (%s)" % (name[-1], '.'.join(name[:-1]))
        else:
            return "%s ( %s )" % (name[-1], '.'.join(name[:-2]) + ":" + '.'.join(name[-2:]))
    __str__ = __repr__
    
    def setUp(self):
        '''
        Initialize the dataset
        '''
        self.cf = CFCheck()

    #--------------------------------------------------------------------------------
    # Helper Methods
    #--------------------------------------------------------------------------------

    def new_nc_file(self):
        '''
        Make a new temporary netCDF file for the scope of the test
        '''
        nc_file_path = os.path.join(gettempdir(), 'example.nc')
        if os.path.exists(nc_file_path):
            raise IOError('File Exists: %s' % nc_file_path)
        nc = Dataset(nc_file_path, 'w')
        self.addCleanup(os.remove, nc_file_path)
        self.addCleanup(nc.close)
        return nc

    def get_pair(self, nc_dataset):
        '''
        Return a pairwise object for the dataset
        '''
        if isinstance(nc_dataset, basestring):
            nc_dataset = Dataset(nc_dataset, 'r')
            self.addCleanup(nc_dataset.close)
        dogma = NetCDFDogma('nc', self.cf.beliefs(), nc_dataset)
        pair = DSPair(nc_dataset, dogma)
        return pair
    
    #--------------------------------------------------------------------------------
    # Compliance Tests
    #--------------------------------------------------------------------------------

    def test_filename(self):
        '''
        Section 2.1 Filenames

        NetCDF files should have the file name extension
        '''
        dataset = self.get_pair(rutgers_glider_path)
        result = self.cf.check_filename_extension(dataset)
        self.assertTrue(result.value)


        # Find a place to make a non-compliant file
        bad_dataset_path = os.path.join(gettempdir(), 'example.netcdf')
        if os.path.exists(bad_dataset_path):
            raise IOError('File Exists: %s' % bad_dataset_path)
        self.addCleanup(lambda x : os.path.exists(x) and os.remove(x), bad_dataset_path)

        # Make a non-compliant file
        nc = Dataset(bad_dataset_path, 'w')
        self.addCleanup(nc.close)
        dpair = self.get_pair(nc)
        result = self.cf.check_filename_extension(dpair)
        # Verify that the non-compliant file returns a negative result
        self.assertFalse(result.value)


    def test_naming_conventions(self):
        '''
        Section 2.3 Naming Conventions

        Variable, dimension and attribute names should begin with a letter and be composed of letters, digits, and underscores.
        '''
        # Create a compliant dataset
        nc = self.new_nc_file()

        # Make a dim
        nc.createDimension('time', 2)
        nc.createVariable('time', 'f', ('time',))

        # Make a compliant variable
        nc.createVariable('pressure', 'f', ('time',))

        dataset = self.get_pair(nc)
        result = self.cf.check_naming_conventions(dataset)
        print result


        

