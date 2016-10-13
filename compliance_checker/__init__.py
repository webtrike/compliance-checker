__version__="1.0.3"


DTExportFormat = '{:%Y-%m-%d %H:%M}'



xvarCandidates =  ["x","lon","longitude","x_centre","x_center"]
xunitsCandidates = ["degrees_E","deg_E","degrees_east","degrees_west"]

yvarCandidates = ["y","lat","latitude","y_centre","y_center"]
yunitsCandidates = ["degrees_N","deg_N","degrees_north"]

zvarCandidates = ["z","depth","botz","height"]
zunitsCandidates= ["m","metres","meters","metre","meters"]




def inferVar(ds,varsC, unitsC):
          
    var = None
    varlist = list()
    for vv in ds.variables.values():
        if "units" in vv.ncattrs() and vv.units in unitsC:
            varlist.append(vv)
               
    #varlist = ds.get_variable_by_attribute(units=unitsC[0])#lambda v: v in unitsC)
    
    if varlist is not None and len(varlist) > 0:
            
        for v in varlist:
            if v.name in varsC:
                var = v
                break
                
        if var is None and len(varlist) == 1:
            var = varlist[0]
                
    return var



def inferXVar(ds):
    return inferVar(ds,xvarCandidates,xunitsCandidates)


def inferYVar(ds):
    return inferVar(ds,yvarCandidates,yunitsCandidates)
    
def inferZVar(ds):
    return inferVar(ds,zvarCandidates,zunitsCandidates)
    


