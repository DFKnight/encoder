from inspect import currentframe,getfile
import os
from os import chdir,listdir,mkdir,remove,walk
from os.path import abspath,dirname,exists,isdir,isfile,join
from subprocess import call
import subprocess
from sys import argv,stdout
import sys
import re
import shlex

QUALITY_NONE=0
QUALITY_HD=23
QUALITY_SD=18

STRING_EMPTY=0

default_location=dirname(abspath(getfile(currentframe())))

current_location=default_location
encodes_location=None

extensions=["mkv","iso","img","avi","rmvb","wmv"]
valid_extensions=["mkv","iso","img","avi","mp4","rmvb","wmv"]
recursive=False
subtitles=True
quality=QUALITY_NONE

remove_old_encodes=False

log_files=True
log_location=default_location+"\\logs\\"

# If 0 parameters have been specified, something went wrong with python!
if(len(argv)==0):
    exit("There were 0 arguments in sys.argv. That is impossible in python (as far as I'm aware)! Something must have gone wrong! Please contact an admin ASAP!")

# If 1 parameter has been specified the program ran successfully! The user had no parameters, so default to the Anime location
elif(len(argv)==1):
    print("You have specified no parameters. Using the default directory of default_location("+default_location+") as the current_location.")
# If 2 parameters have been specified the user has entered a directory. Use it as the current_directory
elif(len(argv)>1):
    print("You have specified "+str(len(argv)-1)+" parameter(s).")
    for i in argv:
        if(i.split("=",1)!=None):
            if(i.split("=",1)[0]=="ext"):
                ext=i.split("=",1)[1].split(",")
                for j in ext:
                    if(str(j) in valid_extensions and not str(j) in extensions): 
                        extensions.append(str(j))
                        print(str(j))
                    else:
                        print("Invalid containers detected: "+str(j))
            if(i.split("=",1)[0]=="flags"):
                flags=i.split("=",1)[1]
                if(len(flags)==1):
                    # remove_old_encodes
                    if(int(flags[0])==0):
                        remove_old_encodes=True
                    elif(int(flags[1])==1):
                        remove_old_encodes=False
                    else:
                        print("Invalid value for remove_old_encodes flag. Using default value of "+str(remove_old_encodes))
                else:
                    print("Invalid number of flags! Check documentation, or contact an administrator, and try again!")
            elif(i.split("=",1)[0]=="src"):
                current_location=i.split("=",1)[1]
            elif(i.split("=",1)[0]=="dst"):
                encodes_location=i.split("=",1)[1]
            elif(i.split("=",1)[0]=="log" and i.split("=",1)[1]=="NO"):
                log_files=False
            elif(i.split("=",1)[0]=="quality"):
                if(i.split("=",1)[1]=="SD"):
                    quality=QUALITY_SD
                elif(i.split("=",1)[1]=="HD"):
                    quality=QUALITY_HD
            elif(i.split("=",1)[0]=="recursive"):
                recursive=True
            elif(i.split("=",1)[0]=="no-subs"):
                subtitles=False
            elif(i.split("=",1)[0]=="quality"):
                if(i.split("=",1)[1]=="SD"):
                    quality=QUALITY_SD
                elif(i.split("=",1)[1]=="HD"):
                    quality=QUALITY_HD

# Check to see if the current directory exists or not
if(exists(current_location)==False):
    print("ERROR: Source path does not exist!")
    exit(1)

chdir(dirname(abspath(getfile(currentframe()))))

def getallfiles(path,recursive):
    list_files=[]
    if(recursive==True):
        for root, dirs, files in walk(path):
            for dirname in dirs:
                if(dirname=="VIDEO_TS"):
                    dirname=str(join(root,dirname).encode(stdout.encoding,'replace'))[2:-1]
                    dirname=dirname.replace('\\\\','\\')
                    list_files.append(dirname)
            for filename in files:
                if(filename.rsplit(".",1)[1].lower() in extensions ):
                    filename=str(join(root,filename).encode(stdout.encoding,'replace'))[2:-1]
                    filename=filename.replace('\\\\','\\')
                    list_files.append(filename.replace('\\\\','\\'))
    else:
        for filename in listdir(path):
            if(isfile(path+'\\'+filename) and filename.rsplit(".",1)[1].lower() in extensions):
                filename=str(join(path,filename).encode(stdout.encoding,'replace'))[2:-1]
                filename=filename.replace('\\\\','\\')
                list_files.append(filename.replace('\\\\','\\'))
    return list_files

# Get the list of files (recursively) in the specified path
def getfiles(path,recursive):
    hd_files=[]
    sd_files=[]
    if(recursive==True):
        for root, dirs, files in walk(path):
            for filename in files:
                if(filename.rsplit(".",1)[1].lower() in extensions):
                    filename=str(join(root, filename).encode(stdout.encoding,'replace'))[2:-1]
                    quality=getQuality(filename)
                    if(quality==QUALITY_HD):
                        hd_files.append(filename.replace('\\\\','\\'))
                    elif(quality==QUALITY_SD or quality==QUALITY_NONE):
                        sd_files.append(filename.replace('\\\\','\\'))
    else:
        files=listdir(path)
        if(len(files)>0):
            for filename in files:
                if(isfile(path+'\\'+filename) and filename.rsplit(".",1)[1].lower() in extensions):
                    filename=str(join(path, filename).encode(stdout.encoding,'replace'))[2:-1]
                    quality=getQuality(filename)
                    if(quality==QUALITY_HD):
                        hd_files.append(filename.replace('\\\\','\\'))
                    elif(quality==QUALITY_SD or quality==QUALITY_NONE):
                        sd_files.append(filename.replace('\\\\','\\'))
    return hd_files,sd_files

pattern=re.compile(r'Stream.*Video.*, ([0-9]+)x([0-9]+)')

# Check the quality of the file using ffmpeg.exe
def getQuality(filename):
    quality=QUALITY_NONE
    call_args=["bin\\ffmpeg.exe","-i",filename]
    p=subprocess.Popen(call_args,stderr=subprocess.PIPE)
    out, err = p.communicate()

    match=pattern.search(err.decode('utf-8'))
    if(match):
        x,y=map(int, match.groups()[0:2])
    else:
        x=y=0

    # Determine if the quality of the video is HD or SD based on the number of pixels
    # per frame. Information retrieved from: 
    # http://en.wikipedia.org/wiki/List_of_common_resolutions
    if(x*y>=691200):
        quality=QUALITY_HD
    else:
        quality=QUALITY_SD
    return quality
# Check to see if the file has already been encoded or not
def encodedFileExists(filename):
    if(not(exists(filename.rsplit("\\",1)[0]+"\\encodes\\")) and not(exists(filename.rsplit(".")[0]+".mp4"))):
        return False
    return True
# Check to see if the files have already been encoded or not
def parseEncodedFiles(original_list):
    tmp_files=[]
    for f in original_list:
        if(encodes_location==None):
            encode_location=f.rsplit("\\",1)[0]+"\\encodes\\"
        else:
            encode_location=encodes_location
        if(isdir(encode_location) and exists(encode_location)):
            encoded_file=encode_location+f.rsplit("\\",1)[1].rsplit(".",1)[0]+".mp4"
            if(not(exists(encoded_file))):
                tmp_files.append(f)
        else:
            tmp_files.append(f)
    return tmp_files

# Encode the current file using HandBrakeCLI.exe
def encode(files,quality):
    for f in files:
        if(encodes_location==None):
            encode_location=f.rsplit("\\",1)[0]+"\\encodes\\"
        else:
            encode_location=encodes_location
        if(not(exists(encode_location))):
            try:
                mkdir(encode_location)
            except:
                print("Unable to create encode directory! "+encode_location)
                continue
        print("Currently encoding: "+f.rsplit("\\",1)[1]+" ... ",end='\r')
        stdout.flush()
        title_to_encode=getFirstTitleInfo(f)
        call_args=["C:\\Program Files\\Handbrake\\HandBrakeCLI.exe",str("-i"+f),str("-o"+encode_location+f.rsplit("\\",1)[1].rsplit(".",1)[0]+".mp4"),"-q "+str(quality),"--preset=\"Normal\"","-ex264","-t "+str(title_to_encode)]
        if(subtitles==True):
            call_args.append("-s 1")
            call_args.append("--subtitle-burn")
        #f2=open(log_location+f.rsplit("\\",1)[1]+".txt","w")
        
        p=subprocess.Popen(call_args, bufsize=-1, stdin=open(os.devnull), stdout=subprocess.PIPE, stderr=open(os.devnull))
        line=list()
        while True:
            stdout2=p.stdout.readline(1)
            if(stdout2.decode('utf-8')!='\r'):
                line.append(stdout2.decode('utf-8'))
            else:
                eta_value=""
                percent_value=""
                output=""
                try:
                    eta_value="".join(line).split(' ')[13]
                except:
                    pass
                try:
                    percent_value="".join(line).split(' ')[5]
                except:
                    pass
                output="Currently encoding: "+f.rsplit("\\",1)[1]
                if percent_value is not "":
                    output=output+" ("+str(percent_value)+" %"
                if eta_value is not "":
                    output=output+", ETA: "+eta_value
                elif percent_value is not "":
                    output=output+")"
                output=output+" ... "

                print(output,end='\r')
                sys.stdout.flush()
                
                line=list()
            if(stdout2.decode('utf-8')=='' and p.poll()!=None):
                break
        #f2.close()
        print("Currently encoding: "+f.rsplit("\\",1)[1]+" (100.00 %, ETA: 00h00m00s) ... Done!")

# Get video track information of the file that is going to be encoded
def getFirstTitleInfo(filename):
    call_args=["C:\\Program Files\\Handbrake\\HandBrakeCLI.exe",str("-i"+filename),"-t0"]
    p=subprocess.Popen(call_args,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out, err = p.communicate()

    data=[]
    temp_data=""
    for test in err:
        if(test==10):
            data.append(temp_data)
            temp_data=""
        else:
            temp_data=temp_data+chr(test)
    for test in data:
        if("+ title" in test):
            return int(test[8:-2])

# Get a list of files to be encoded
hd_files=[]
sd_files=[]

if(isfile(current_location)):
    if(quality==QUALITY_NONE):
        quality=getQuality(current_location)
    if(quality==QUALITY_HD and encodedFileExists(current_location)==False):
        hd_files.append(current_location)
    elif(quality==QUALITY_SD and encodedFileExists(current_location)==False):
        sd_files.append(current_location)
elif(isdir(current_location) and current_location.rsplit("\\",1)[1]=="VIDEO_TS"):
    if(quality==QUALITY_NONE):
        quality=QUALITY_HD;
    if(quality==QUALITY_HD and encodedFileExists(current_location)==False):
        hd_files.append(current_location)
    elif(quality==QUALITY_SD and encodedFileExists(current_location)==False):
        sd_files.append(current_location)
elif(isdir(current_location)):
    print("Compiling a list of files to be encoded ... ",end="")
    stdout.flush()
    if(quality==QUALITY_NONE):
        hd_files,sd_files=getfiles(current_location,recursive)
        hd_files=parseEncodedFiles(hd_files)
        sd_files=parseEncodedFiles(sd_files)
    else:
        if(quality==QUALITY_HD):
            hd_files=parseEncodedFiles(getallfiles(current_location,recursive))
        elif(quality==QUALITY_SD):
            sd_files=parseEncodedFiles(getallfiles(current_location,recursive))
    print("Done!\n")

total=len(hd_files)+len(sd_files)
if(total==0):
    print("NO FILES TO ENCODE!")
else:
    print("A total of "+str(len(hd_files))+" files will be HD encoded!")
    print("A total of "+str(len(sd_files))+" files will be SD encoded!")
    print("A total of "+str(total)+" files will be encoded!")

    encode(hd_files,QUALITY_HD)
    encode(sd_files,QUALITY_SD)
    
