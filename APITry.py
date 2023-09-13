import swifttools.ukssdc.xrt_prods as ux
import time as t
import tarfile

max_jobs = 5 # How many jobs we'll submit in any one go.
my_email = "sek289@psu.edu"

SendReq=False

#Request Properties
myReq = ux.XRTProductRequest(my_email, silent=False)
myReq.setGlobalPars(name='GRB 221027B',targ='01131397')
myReq.setGlobalPars(RA=225.621,Dec=47.442)
myReq.setGlobalPars(centroid=True,posErr=1.5)
myReq.setGlobalPars(useSXPS=False)

#Source detection properties
myReq.addProduct('SourceDet')
myReq.setProductPars('SourceDet',whichData='all',whichBands='total')

#Image properties
# myReq.addProduct('Image')
# myReq.setProductPars('Image',energies='0.3-10',whichData='all')


if SendReq==True:
    ok=myReq.submit()
    done=myReq.complete
    
    while not done:
      t.sleep(60)
      done=myReq.complete
      
    DownOut=myReq.downloadProducts('products/', format='zip',clobber=True)
    
src = myReq.retrieveSourceList(returnData=True)

#%%

print(src['Total'][0]['rate'])