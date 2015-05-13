from compliance_checker.defined import ComplianceCheckerCheckSuiteDefined
from netCDF4 import Dataset

def handler(request,response):
    import urllib2
    type = request.inputs['type']
    options = request.inputs['options']
    print request.inputs['file']
    
    cs = ComplianceCheckerCheckSuiteDefined()
    ds = Dataset(file)
    cs.set_optpions(options)
    vals = cs.run(ds, type)
    print vals

    msg = "Received test result: "+vals
           
    #msg='received ' + type + ' and options: '+options
    response.outputs['msg'].setvalue(msg)
    return response