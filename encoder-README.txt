What is it? 

encoder.py is a small script file used (in conjunction with HandBrakeCLI.exe and ffmpeg.exe to encode a batch of script files located within a directory (but not it's subdirectories/see rencoder.py for recursive encoding). 

How do I use it?

First ensure that the location of HandBrakeCLI.exe is the same it is in your system. It is located on the line below "# NOTE: HB_LOCATION MUST BE SPECIFIED HERE". Once the correct location for HandBrakeCLI.exe has been entered, you can use the following parameters (in any order).
Second, ensure that ffmpeg.exe is located in the same location as encoder.py, in a subdirectory called bin.
- src
    This is the source directory that will be scanned. 
    NOTE: Individual files cannot be entered into the application as a source directory. 
    eg. encoder.py src=files
- dst
    This is the destination directory. If it is specified, the location will be used as the destination directory. Otherwise, the default location of src/encodes will be used.
    NOTE: Individual files cannot be entered into the application as a destination directory. 
    eg. encoder.py src=files dst=files/encodes

- quality = HD | SD
    There are 2 quality profiles stored within the application. HD will attempt to lower the quality, in an effort to preserve file space, while SD will attempt to increase the quality in exchange for increased file space.
    eg. encoder.py quality=HD src=file.mkv dst=file.mp4