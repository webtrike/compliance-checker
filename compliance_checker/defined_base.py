from compliance_checker.base import BaseCheck,BaseNCCheck,DSPair
import string
from abc import abstractmethod
import numpy as np

class DefinedBaseCheck(BaseCheck):
    options = []
    
    def set_options(self,options):
        self.options = string.split(str(options).lower())
    
    @abstractmethod
    def check(self,dsp):
        raise NotImplementedError("Define this in your derived Checker class")
    
    
    def load_datapair(self, ds):
        """
        Returns a DSPair object with the passed ds as one side and the proper Dogma object on the other.

        Override this in your derived class.
        """
        return DSPair(ds, None)



class DefinedNCBaseCheck(DefinedBaseCheck,BaseNCCheck):
    @abstractmethod
    def check(self,dsp):
        raise NotImplementedError("Define this in your derived Checker class")
        
    @abstractmethod
    def limits(self):
        """
        return the limits as dictionary of the data set interrogated and defined by the Checker context
        """
        raise NotImplementedError("Define this in your derived Checker class")
    
    
    def calc_rotation(self, dx, dy ):
        # now calculate the overall rotation, its going to be off for curvliniar grids ...
        rotation = 0.
        if dx == 0:
            if dx > 0:
                rotation = 90.
            else:
                rotation = 270.
        else:    
            theta = np.arctan(dy/dx)
            rotation = theta * 180./np.pi
            
        return rotation
    
    
    def load_datapair(self, ds):
        """
        Returns a DSPair object with the passed ds as one side and the proper Dogma object on the other.

        Override this in your derived class.
        """
        return BaseNCCheck.load_datapair(self,ds)
