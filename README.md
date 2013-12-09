encoder
=======
The latest and most up-to-date version of this project can be found at: https://bitbucket.org/qureszai/encoder

What is it? 
-------
rencoder.py is a small script file used (in conjunction with HandBrakeCLI.exe and ffmpeg.exe to encode a batch of script files located within a directory (but not it's subdirectories/see rencoder.py for recursive encoding). 

NOTE: encoder.py is deprecated. Please use rencoder.py.

How do I use it?
-------
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

- quality = HD | SD | (int)
    There are 2 quality profiles stored within the application. HD will attempt to lower the quality, in an effort to preserve file space, while SD will attempt to increase the quality in exchange for increased file space.
    
        eg. encoder.py quality=HD src=file.mkv dst=file.mp4

- recursive
    This option will scan a directory recursively, select any valid files which have not been encoded already, and encode the selected files.
    
        eg. encoder.py src=directory recursive

        directory
        directory/file1.avi
        directory/file2.avi
        directory/director2/file3.mkv
        directory/director3/file4.mkv

        The list of files that will be encoded will be the following: 
        - file1.avi
        - file2.avi
        - file3.mkv
        - file4.mkv

- no-subs
    By default, subtitle track #1 will be encoded as a hardsub on the encoded video. The no-subs option is used in order to avoid encoded subtitles.
    
        eg encoder.py src=<filename or directory> no-subs
