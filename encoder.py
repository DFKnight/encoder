import subprocess
from inspect import currentframe,getfile
from os import listdir,makedirs,remove
from os.path import abspath,dirname,exists,isfile
from sys import argv,builtin_module_names,stdout
from threading import Thread
import select

# This is for later. Use queues to store HandBrake encoding jobs. 
try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty

# Some important/useless variables

# The exact path to HandBrakeCLI.exe
# NOTE: HB_LOCATION MUST BE SPECIFIED HERE
hb_location="C:\\Program Files\\Handbrake\\HandBrakeCLI.exe"
# Set the current directory where the encoder.py file is located as the default directory.
default_location=dirname(abspath(getfile(currentframe())))
encodes_location=None
current_location=default_location
logs_location=dirname(abspath(getfile(currentframe())))+"\\logs\\"
valid_files=[]
remove_mp4_encodes = False # Flag to specify if .mp4 files that have been encoded should be deleted or not
remove_old_encodes = False # Flag to specify if any files that have been encoded and their (original doesn't exist anymore) should be deleted or not
encode_mp4_videos = False # Flag to specify is .mp4 files will be encoded or not. (NOTE: THIS HAS NOT BEEN IMPLEMENTED YET!!!!)

#   NOTE: NEW IDEA! (NOTE YET IMPLEMENTED)
#   PASS FORMATS_TO_PARSE AS A LIST FROM COMMAND LINE ARGUMENTS.
#   DEFAULT LIST WOULD ONLY CONSIST OF .MKV and .AVI
#   ANY ADDITIONAL FORMATS WOULD NEED TO BE PASSED AS A COMMAND LINE PARAMETER IN THE FOLLOWING FORMAT
#   formats=avi,rmvb
#   NOTE2: THIS IS BETTER THAN USING A MILLION FLAGS FOR EVERY DIFFERENT TYPE OF FILE THAT WILL BE ENCODED USING THIS APPLICATION
log_files = True # Flag to specify if logs will be made or not
quality = 23 # The quality of the rip. 23=HD and 18=SD. Default is HD
# NOTE: quality can be overridden. See documentation for more details.

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
            if(i.split("=",1)[0]=="flags"):
                flags=i.split("=",1)[1]
                if(len(flags)==2):

                    # remove_mp4_encodes
                    if(int(flags[0])==0):
                        remove_mp4_encodes=True
                    elif(int(flags[0])==1):
                        remove_mp4_encodes=False
                    else:
                        print("Invalid value for remove_mp4_encodes flag. Using default value of "+str(remove_mp4_encodes))

                    # remove_old_encodes
                    if(int(flags[1])==0):
                        remove_old_encodes=True
                    elif(int(flags[1])==1):
                        remove_old_encodes=False
                    else:
                        print("Invalid value for remove_old_encodes flag. Using default value of "+str(remove_old_encodes))

                    # encode_mp4_videos
                    if(int(flags[1])==0):
                        encode_mp4_videos=True
                    elif(int(flags[1])==1):
                        encode_mp4_videos=False
                    else:
                        print("Invalid value for remove_old_encodes flag. Using default value of "+str(encode_mp4_videos))
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
                    quality=18
                elif(i.split("=",1)[1]=="HD"):
                    quality=23

# Check to see if the current directory exists or not
if(exists(current_location)==False):
    print("ERROR: Source path does not exist!")
    exit(1)
    
# Check to see if the logs directory exists or not
if(log_files==True and exists(logs_location)==False):
    try:
        makedirs(logs_location)
    except:
        print("Error creating new directory!")
    print("Created new directory!")
print()

if(len(current_location)>0 and current_location[-1:]!="\\"):
    current_location = current_location + "\\"
if(encodes_location==None):
    encodes_location = current_location+"encodes\\"
elif(len(encodes_location)>0 and encodes_location[-1:]!="\\"):
    encodes_location = encodes_location + "\\"

# Check to see if the encodes directory exists or not
if(exists(encodes_location)==False):
    try:
        makedirs(encodes_location)
    except:
        print("Error creating encodes directory!")
    print("Created encodes directory!")

files = listdir(current_location)
encoded_files = listdir(encodes_location)
files_to_remove_mp4 = []
files_to_remove_old = []
hbargs_src = []
hbargs_dst = []

files.sort()
encoded_files.sort()

# Check to see if there are any files in encoded_files (encodes_location) that don't exist in files (current_location) or are not needed anymore

if(len(list(encoded_files))>0):
    for link in list(encoded_files):

        found_mp4_original=False
        found_in_original=False

        for original_link in files:
            if(link == original_link):
                found_mp4_original=True
            if(link.rsplit(".",1)[0].lower() == original_link.rsplit(".",1)[0].lower()):
                found_in_original=True

            if(found_mp4_original==True and found_in_original==True):
                break

        if((found_mp4_original==True and remove_mp4_encodes==True) or (found_in_original==False and remove_old_encodes==True)):
            print("Found file "+link)
            encoded_files.remove(link)

        if(found_mp4_original==True and remove_mp4_encodes==True):
            files_to_remove_mp4.append(encodes_location+link)
        if(found_in_original==False and remove_old_encodes==True):
            files_to_remove_old.append(encodes_location+link)
else:
    print("No encoded files found!")


if(len(list(files_to_remove_mp4))>0):
    for file in list(files_to_remove_mp4):
        remove(file)
        print("Removing mp4 file "+file+" ... ")
        files_to_remove_mp4.remove(file)
        print("Done!")
else:
    print("No mp4 files to remove!")

if(len(list(files_to_remove_old))>0):
    for file in list(files_to_remove_old):
        remove(file)
        print("Removing old file "+file+" ... ")
        files_to_remove_old.remove(file)
        print("Done!")
else:
    print("No old files to remove!")

print("\nCompiling a list of all mkv and avi files in "+current_location+" that need to be encoded!\n")

for link in files:
    if(isfile(current_location+link) and link.rsplit(".",1)[1].lower() != "mp4" and (link.rsplit(".",1)[1].lower() == "mkv" or link.rsplit(".",1)[1].lower() == "avi" or link.rsplit(".",1)[1].lower() == "ogm")):
        if(isfile(encodes_location+link.rsplit(".",1)[0]+".mp4")==False):
            print(link)
            src_file = current_location+link
            dst_file = encodes_location+link.rsplit(".",1)[0]+".mp4"

            hbargs_src.append("-i"+src_file)
            hbargs_dst.append("-o"+dst_file)



if(len(hbargs_src)==0 and len(hbargs_dst)==0):
    print("NO FILES TO ENCODE!")
else:
    print("\nEncoding files now ...\n")
    i=0
    progress=float(0.0)
    for args in hbargs_src:
        print('Currently encoding: '+hbargs_src[i].rsplit("\\",1)[1]+' ... ', end='')
        stdout.flush()
        #call_args=[hb_location,hbargs_src[i],hbargs_dst[i],"-q "+str(quality),"--preset=\"Normal\"","-ex264","-s 1","--subtitle-burn"]
        call_args=[hb_location,hbargs_src[i],hbargs_dst[i],"-q "+str(quality),"--preset=\"Normal\"","-ex264"]
    
        f=open(logs_location+hbargs_src[i].rsplit("\\",1)[1]+".txt","w")
    
        #print(call_args)
        subprocess.call(call_args,stdout=f,stderr=f)

        print('Done!')
        f.close()
        i=i+1
