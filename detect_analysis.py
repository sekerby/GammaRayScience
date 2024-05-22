import os as os
from astropy.io import fits
import numpy as np

from TestWithin2 import TestWithin

FGL = fits.open('4FGL_DR4.fit')
FGLnames = FGL[1].data['Source_Name']
FGLRA = FGL[1].data['RAJ2000 ']
FGLDec = FGL[1].data['DEJ2000 ']
FGLsma = FGL[1].data['Conf_95_SemiMajor']
FGLsmi = FGL[1].data['Conf_95_SemiMinor']
FGLang = FGL[1].data['Conf_95_PosAng']

startpath=os.getcwd()+"/"
os.chdir(startpath)

specpath="testData"
totpath=startpath+specpath
os.chdir(totpath)

i=0

empty=[]
analyzed=[]
problem=[]

for dirpath, dirnames, filenames in os.walk(totpath):
    os.chdir(dirpath)
    print(dirpath)
    
    # does the directory have a ximage .det file?
    if 'total.det' in filenames:
        
        detfile = open('total.det','r')
        logfile = open('ximage.log','r')
        outfile = open('detinfo.csv','w')
        
        
        dets = []
        Xpixels = []
        Ypixels = []
        SN = []
        print('Have found an XImage detection file')
        
        #read lines from .det and .log files
        lines = [line.rstrip() for line in detfile]
        loglines = [line.rstrip() for line in logfile]
        
        # the lines in the .det file that we want do not start with '!'
        for line in lines:
            if line.split()[0] != '!':
                dets.append(line)
        
        # the lines in the .log file that we want start with 'X'
        for i in range(0,len(loglines)):
            if loglines[i].split()[0] == 'X':
                Xpixels.append(loglines[i].split()[2])
                Ypixels.append(loglines[i].split()[5])
        
        # the lines with the SOSTA S/N start with "Signal"       
        for i in range(0,len(loglines)):
            if loglines[i].split()[0] == 'Signal':
                SN.append(loglines[i].split()[-1])
        # check to make sure that the same number of .det and .leg files have been found        
        if len(dets) != len(SN):
            print('Problem! The .det and .log files may be malformed.')
            problem.append(dirpath[-12:])
        else:
            analyzed.append(dirpath[-12:])
        
        #outfile.write('hh mm ss DD DM DS SNdetect SNsosta\n')
        # for i in range(0,len(dets)):
        #     outfile.write(dets[i][50:77]+''+dets[0][98:]+' '+SN[i])
        #     outfile.write('\n')
                
#%% now reading in the created file
        MyRAs = 15*(float(dets[0][50:52])+float(dets[0][53:55])/60+float(dets[0][56:62])/3600)
        MySign = np.abs(float(dets[0][63:66]))/float(dets[0][63:66])
        MyDecs = float(dets[0][63:66])+MySign*(float(dets[0][67:69])/60+float(dets[0][70:76])/3600)
        
        MyRAs=MyDets['RA'].values
        MyDecs=MyDets['Dec'].values
        MyName='4FGL '+dirpath.split('\\')[-1]
        
        find = np.where(FGLnames == MyName)[0][0]
        thisRA,thisDec,thissma,thissmi,thisang = FGLRA[find],FGLDec[find],FGLsma[find],FGLsmi[find],FGLang[find]
        
        detfile.close()
        logfile.close()
        outfile.close()
        
        TestWithin(MyRAs,MyDecs,thisRA,thisDec,thissma,thissmi,thisang,MyName,True)
