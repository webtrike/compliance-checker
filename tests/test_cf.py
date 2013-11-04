#!/usr/bin/env python

from compliance_checker.cf import CFCheck
from compliance_checker.suite import DSPair, NetCDFDogma
from netCDF4 import Dataset
from tempfile import gettempdir

import unittest
import os

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

        dataset    = Dataset('test-data/ru07-20130824T170228_rt0.nc', 'r')
        dogma      = NetCDFDogma('excuse_me', self.cf.beliefs(), dataset)
        self.dpair = DSPair(dataset, dogma)

    def new_nc_file(self):
        nc_file_path = os.path.join(gettempdir(), 'example.nc')
        if os.path.exists(nc_file_path):
            raise IOError('File Exists: %s' % nc_file_path)
        nc = Dataset(nc_file_path, 'w')
        self.addCleanup(os.remove, nc_file_path)
        self.addCleanup(nc.close)
        return nc

    def test_filename(self):
        '''
        Section 2.1 Filenames
        '''
        result = self.cf.check_filename_extension(self.dpair)
        self.assertTrue(result.value)


        # Find a place to make a non-compliant file
        bad_dataset_path = os.path.join(gettempdir(), 'example.netcdf')
        if os.path.exists(bad_dataset_path):
            raise IOError('File Exists: %s' % bad_dataset_path)

        nc = Dataset(bad_dataset_path, 'w')
        self.addCleanup(os.remove, bad_dataset_path)
        self.addCleanup(nc.close)
        self.dpair.dataset = nc
        result = self.cf.check_filename_extension(self.dpair)
        self.assertFalse(result.value)


    def test_naming_conventions(self):
        '''
        Section 2.2 Naming Conventions

        Variable, dimension and attribute names should begin with a letter and be composed of letters, digits, and underscores.
        '''
        pass


        

