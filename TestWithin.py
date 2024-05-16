import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import Ellipse
mpl.rcParams['font.family']='serif'
mpl.rcParams['font.size']=16

import astropy.units as u
from astropy.io import fits
from astropy.coordinates import SkyCoord
from astropy.coordinates import Angle
from regions import PixCoord
from regions import EllipseSkyRegion, EllipsePixelRegion

def TestWithin(pointRA,pointDec,cenRA,cenDec,SMA,SMI,angi,Plot=True,Blabber=True):
    #pointRA, pointDec : RA and Dec, in decimal degrees, of test point
    #cenRA, decDec     : RA and Dec center of ellipse
    #SMA, SMI          : semi-major and semi-minor axis in degrees
    #angi              : angle from north towards east
    
    #angi is degrees towards east from celestial north of SMA
    
    #check to make sure SMA > SMI : reverse them if they are not
    if SMA < SMI:
        holder = SMA
        SMA = SMI
        SMI = holder
    
    #convert angle "from north" to angle "from east" for calculatio purposes
    ang = angi+90
    
    #calculate the foci
    c = np.sqrt(SMA**2 - SMI**2)
        
    f1x = cenRA + np.cos(np.deg2rad(ang)) * c
    f1y = cenDec - np.sin(np.deg2rad(ang)) * c
    
    f2x = cenRA - np.cos(np.deg2rad(ang)) * c
    f2y = cenDec + np.sin(np.deg2rad(ang)) * c
    
    # if the declinations are close to the poles, the plotting won't reflect reality
    if np.abs(pointDec)>85 and Blabber:
        print('Declination is high or low. Plotting may not accurately show the sky, but T/F output is still valid')
    
    # plot everything if Plot
    
    if Plot:
        fig=plt.figure(figsize=(8,8))
        ax=fig.add_subplot(111)
        
        ellipse = Ellipse(xy=(cenRA, cenDec), width=SMA*2, height=SMI*2,angle=-ang, edgecolor='r', fc='None', lw=2)
        ax.add_patch(ellipse)
        
        ellipse = Ellipse(xy=(cenRA, cenDec), width=SMA*2, height=SMI*2,angle=-ang+90, edgecolor='r', fc='None', lw=1, ls=':')
        ax.add_patch(ellipse)
        
        ax.plot(cenRA,cenDec,'bo')
        ax.plot(f1x,f1y,'bx')
        ax.plot(f2x,f2y,'bx')
        ax.plot(pointRA,pointDec,'go')
        
        ax.axis('equal')
        ax.grid()
        ax.set_xlim(ax.get_xlim()[::-1]) #in astronomy RA increases to the east, but east is often plotted to the left
        ax.set_ylabel('South<    Dec      > North')
        ax.set_xlabel('East<     RA     > West')
    
    #get RA and Dec positions in astropy SkyCoord
    point = SkyCoord(pointRA*u.deg, pointDec*u.deg, frame='fk5')
    foci1 = SkyCoord(f1x*u.deg, f1y*u.deg, frame='fk5')
    foci2 = SkyCoord(f2x*u.deg, f2y*u.deg, frame='fk5')
    
    #calculate total distance
    TotalSep = point.separation(foci1).deg + point.separation(foci2).deg

    #note: due to floating point errors, the conversion to SkyCoord can result in small (1e-4) errors.       
    
    #check total distance against the major axis length, and return True if the test point is within the ellipse
    if (TotalSep <= 2*SMA + 1e-3):
        if Blabber:
            if (TotalSep - 2*SMA) < 1e-3:
                print("It is extremely close to the border. You should probably check this one out") 
        return True
    else:
        return False    
    
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
    
    toPlot = False
    
    if i%500 == 0:
        toPlot = True
    
    MyOutput = TestWithin(myRA,myDec,FGLRA[FindIt],FGLDec[FindIt],FGLsma[FindIt],FGLsmi[FindIt],FGLang[FindIt],Plot=toPlot,Blabber=False)
    
    if i%500 == 0:
        print(MyOutput)
    
    ExcessSum['Inside95actual'][i] = MyOutput