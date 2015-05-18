from compliance_checker.defined import ComplianceCheckerCheckSuiteDefined
from netCDF4 import Dataset
from pywps import Service, Process,LiteralInput, ComplexInput,Format,LiteralOutput
from pywps.inout import BBoxOutput
from pywps.app import BoundingBoxOutput


def handler(request,response):
    import urllib2
    type = request.inputs['type']
    options = request.inputs['options']
    file = request.inputs['file']
    print str(file)
    
    cs = ComplianceCheckerCheckSuiteDefined()
    ds = Dataset(file)
    cs.set_optpions(options)
    vals = cs.run(ds, type)
    results = vals[type]
    
    # now extract the score and BBox
    scoreResult = results[0][0]
    errors = results[1]
    bbdict = results[2]
    scoreTuple = scoreResult.value
    if not scoreTuple[0] == scoreTuple[1]:
        print 'unsuccessful: '+ str(scoreResult.msgs)
        response.outputs['success'].setvalue(str(False))
        response.outputs['bbox'].setValue('None')
    else:
        response.outputs['success'].setvalue(str(True))
        """ TODO fix this once bb is implemented
        bb = BoundingBoxOutput('bbox')
        blist = bbdict['bounds']
        bb.ll =  blist[2],blist[0]
        bb.ur =  blist[3],blist[1]
        response.outputs['bbox'] = bb
        """
        
    print str(results)
    msg = "Received test result: "+str(results)
    
           
    #msg='received ' + type + ' and options: '+options
    response.outputs['msg'].setvalue(msg)
    
    return response


def createProcess():
    process = Process(handler,identifier='file_checker',inputs=[
    LiteralInput('type', 'string'),
    LiteralInput('options', 'string'),
    ComplexInput('file', [Format('text/UTF-8')]),
    ],   
                  outputs=[LiteralOutput('msg',data_type='string'),
                           LiteralOutput('success',data_type='boolean')
                           #,LiteralOutput('nij',data_type='string')
                           #,LiteralOutput('bounds',data_type='string')
                           #,BBoxOutput('bbox')
                           ]
                  )
    
    return process