import os as os

#os.system("export HEADASNOQUERY= \nexport HEADASPROMPT=/dev/null")
#startpath="/Users/kdn5172/Desktop/"
startpath=os.getcwd()+"/"#"/Users/kdn5172/Desktop/"
#print("CWD: "+os.getcwd())
os.chdir(startpath)

specpath="testData"
totpath=startpath+specpath
os.chdir(totpath)

i=0

empty=[]
analyzed=[]

for dirpath, dirnames, filenames in os.walk(totpath):
    os.chdir(dirpath)
    print(dirpath)

    if 'total.fits' in filenames:
        print('Found total.evt. Conducting XImage search')
        analyzed.append(dirpath[-12:])
        imstr = 'ximage <<EOF \n log ximage \n read total.fits \n detect \n sosta/detect_sources \n quit \n \n \n'
        os.system(imstr)
        print('Results logged to .det and ximage.log file')
    else:
        print('This target has no observations or no summed event file')
        empty.append(dirpath[-12:])
    
    if 'total.det' in filenames:
        print('Have found an XImage detection file')
        with open('total.det') as file:
            lines = [line.rstrip() for line in file]
        print(lines)