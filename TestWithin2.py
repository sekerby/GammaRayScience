import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None

import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import Ellipse
mpl.rcParams['font.family']='serif'
mpl.rcParams['font.size']=16

import astropy.units as u
from astropy.io import fits
from astropy.coordinates import SkyCoord
from astropy.coordinates import Angle
from astropy.wcs import WCS
from regions import PixCoord
from regions import EllipseSkyRegion, EllipsePixelRegion
from regions import make_example_dataset

#%%

def TestWithin(pointRA,pointDec,cenRA,cenDec,SMA,SMI,angi,Plot=True):
    #pointRA, pointDec : RA and Dec, in decimal degrees, of test point
    #cenRA, decDec     : RA and Dec center of ellipse
    #SMA, SMI          : semi-major and semi-minor axis in degrees
    #angi              : angle from north towards east
    
    #angi is degrees towards east from celestial north of SMA. Needs to be converted, though
    
    #make WCS for our purposes
    w = WCS(naxis=2)
    w.wcs.crpix = [cenRA, cenDec]
    w.wcs.cdelt = np.array([-0.01, 0.01])
    w.wcs.crval = [0, 0]
    w.wcs.ctype = ["RA---AIR", "DEC--AIR"]
    w.wcs.set_pv([(0, 0, 0)])
    
    #define target point
    point_sky = SkyCoord(pointRA, pointDec, unit='deg' ,frame='fk5')
    
    #check to make sure SMA > SMI : reverse them if they are not
    if SMA < SMI:
        holder = SMA
        SMA = SMI
        SMI = holder
    
    #convert angle "from north" to angle "from east" for calculatio purposes
    ang = angi+90
    
    #defining the ellipse
    
    center_sky = SkyCoord(cenRA*u.deg, cenDec*u.deg, frame='fk5') 
    region_sky = EllipseSkyRegion(center=center_sky,width=2*SMA*u.deg, height=2*SMI*u.deg,angle=ang*u.deg)
    
    if Plot:
        
        point_pixel = point_sky.to_pixel(w)
        center_pixel = center_sky.to_pixel(w)
                
        region_pixel = region_sky.to_pixel(w)
        region_artist = region_pixel.as_artist(fc='white',color='red')

        ax = plt.gca()
        ax.set_aspect('equal')
        
        ax.add_artist(region_artist)
        ax.plot(center_pixel[0],center_pixel[1],'bx')
        ax.plot(point_pixel[0],point_pixel[1],'gx')
        
        ax.set_xlim(-500,500)
        ax.set_ylim(-500,500)
        ax.grid()
        
        plt.show()
    
    return region_sky.contains(point_sky, w)
 
    
#%% making venn diagram : loading stuff in

ExcessSum = pd.read_csv('ExcessSummary.txt')
ExcessSum['Inside95actual'] = ExcessSum['Inside95?'].values
ExcessSum['Flag'] = ExcessSum['Inside95?'].values

ExcessRA = ExcessSum['RA'].values
ExcessDec = ExcessSum['Dec'].values

ExcessCoord = SkyCoord(ra=ExcessRA, dec=ExcessDec, frame='fk5',unit=(u.hourangle, u.deg))

FGL = fits.open('4FGL_DR4.fit')

FGLname = FGL[1].data['Source_Name']
FGLRA = FGL[1].data['RAJ2000 ']
FGLDec = FGL[1].data['DEJ2000 ']
FGLsma = FGL[1].data['Conf_95_SemiMajor']
FGLsmi = FGL[1].data['Conf_95_SemiMinor']
FGLang = FGL[1].data['Conf_95_PosAng']

#%% comparing

for i in range(0,len(ExcessSum)):
    FindIt = np.where((FGLname == ExcessSum['Name'][i]+'c') + (FGLname == ExcessSum['Name'][i]+'e') + (FGLname == ExcessSum['Name'][i]))[0]
    if len(FindIt) == 0:
        ExcessSum['Flag'][i] = False
        continue
    else:
        ExcessSum['Flag'][i] = True
    FindIt = FindIt[0]
    
    myRA = ExcessCoord[i].ra.deg
    myDec = ExcessCoord[i].dec.deg
    
    toPlot=False
    # if i%500 == 0:
    #     toPlot=True
    
    MyOutput = TestWithin(myRA,myDec,FGLRA[FindIt],FGLDec[FindIt],FGLsma[FindIt],FGLsmi[FindIt],FGLang[FindIt],Plot=toPlot)
    
    if i%500 == 0:
        print(MyOutput)
    
    ExcessSum['Inside95actual'][i] = MyOutput