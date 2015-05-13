from werkzeug.serving import run_simple
import wps.wps as handler
from pywps import Service, Process,LiteralInput, ComplexInput,Format,LiteralOutput
from pywps.inout import BBoxOutput

process = Process(handler.handler,identifier='file_checker',inputs=[
    LiteralInput('type', 'string'),
    LiteralInput('options', 'string'),
    ComplexInput('file', [Format('text/UTF-8')]),
    ],   
                  outputs=[LiteralOutput('msg', 'string'),]
                  )
                  
                  
                  #outputs=[ LiteralInput('success', 'boolean'),
                   #                             BBoxOutput()])






service = Service([process])

run_simple('localhost', 5000, service, use_reloader=True)


# test url on my mac
# http://localhost:5000/ows?service=WPS&version=1.0.0&request=Execute&identifier=file_checker&DataInputs=type=roms;options=2D;file=file:///Users/uwer/projects/models/roms/test/marvl/41/roms_grid.nc
