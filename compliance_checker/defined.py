import traceback
import sys
from compliance_checker.suite import CheckSuite
from compliance_checker.roms import DefinedROMSBaseCheck

    
        
            

class ComplianceCheckerCheckSuiteDefined(CheckSuite):
    
    options = []
    """
    CheckSuite that defines all the possible Checker classes for the application, must be an extension of DefinedBaseCheck.
    """
    checkers = {
        'roms'      : DefinedROMSBaseCheck 
    }
    
    def set_optpions(self,t_options):
        self.options = t_options
    
    def run(self, ds, *checker_names):
        """
        Runs this CheckSuite on the dataset with all the passed Checker instances.

        Returns a dictionary mapping checker names to a 2-tuple of their grouped scores and errors/exceptions while running checks.
        """

        ret_val      = {}
        checkers     = self._get_valid_checkers(ds, checker_names)

        if len(checkers) == 0:
            print "No valid checkers found for tests '%s'" % ",".join(checker_names)

        for checker_name, checker_class in checkers:

            checker            = checker_class()   # @TODO: combine with load_datapair/setup
            dsp                = checker.load_datapair(ds)
            checker.setup(dsp)
            errs               = {}
            # here where we differ from the super implementation
            # instead of finding all 'check_' functions we leave it to the implementing class to call checks based on the options defined
            # it must be a class of DefinedBaseCheck
            
            try:
                checker.set_options(self.options)
                vals = checker.check(dsp)
            except Exception as e:
                errs['check'] = (e, sys.exc_info()[2])
            # score the results we got back
            groups = self.scores(vals)
            
            ret_val[checker_name] = groups, errs, checker.limits(dsp)

        return ret_val
    

class ComplianceCheckerDefined(object):
    
    @classmethod
    def run_checker(cls, ds_loc, checker_names, verbose, criteria, options=None):
        """
        Static check runner.

        @param  ds_loc          Dataset location (url or file)
        @param  checker_names    List of string names to run, should match keys of checkers dict (empty list means run all)
        @param  verbose         Verbosity of the output (0, 1, 2)
        @param  criteria        Determines failure (lenient, normal, strict)

        @returns                If the tests failed (based on the criteria)
        """
        retval = True

        cs = ComplianceCheckerCheckSuiteDefined()
        cs.set_options(options)
        ds = cs.load_dataset(ds_loc)
        score_groups = cs.run(ds, *checker_names)

        if criteria == 'normal':
            limit = 2
        elif criteria == 'strict':
            limit = 1
        elif criteria == 'lenient':
            limit = 3

        #Calls output routine to display results in terminal, including scoring.  Goes to verbose function if called by user.
        # @TODO cleanup
        for checker, rpair in score_groups.iteritems():
            groups, errors = rpair

            if len(errors):
                print "The following exceptions occured during the %s checker (possibly indicate compliance checker issues):" % checker

                for check_name, epair in errors.iteritems():
                    print "%s.%s: %s" % (checker, check_name, epair[0].message)
                    if verbose > 0:
                        traceback.print_tb(epair[1].tb_next.tb_next)    # skip first two as they are noise from the running itself @TODO search for check_name
                        print

            score_list, points, out_of = cs.standard_output(limit, checker, groups)
            if not verbose:
                cs.non_verbose_output_generation(score_list, groups, limit, points, out_of)
            else:
                cs.verbose_output_generation(groups, limit, points, out_of)

        return cs.passtree(groups, limit)
    