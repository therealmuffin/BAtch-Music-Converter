#from __future__ import print_function
import os, argparse, sys, signal, shutil, subprocess

# Variables / ESC (1b) - VT100 codes
CURSOR_UP_ONE = '\x1b[1A'
ERASE_LINE = '\x1b[2K'

# Default settings
location =  {   "input": os.getcwd(), 
                "output" : os.path.abspath("../extracted"), 
                "converter": "ffmpeg",
                "alt_converter": "avconv",
                "embedder" : "AtomicParsley",
                "status": "bam_converter.tmp"
            }

settings =  {   "daemonize": False,
                "input_format": "flac",
                "max_depth": 0,
                "dry_run": False,
                "output_format": "mp3",
                "output_extension": "mp3",
                "output_quality": 320,
                "overwrite": False,
                "embed_covers": False,
                "cover_name": "folder.jpg"
            }

arguments = {
                "converter": "",
                "embedder": ""
            }

def help():
    print("BAtch Music Converter")
    print("")
    print("Usage: python ./bam_converter.py [options...]")
    print("")
    print("Available options are specified in brackets if applicable. The default option is")
    print("indicated by an asterisk")
    print("")
    print("General options")
    print("    -h, --help                   Show this help")
    print("    -d, --daemonize              Daemonize bam_converter")
    print("    -n, --dry_run                Dry run")
    print("    -v, --verbose                Verbose output")
    print("")
    print("Input options:")
    print("    -i, --input_location         Location to read library from ['./'*]")
    print("    -m, --max_depth              Max folder depth (set 0 for infinte) [0*]")
    print("")
    print("Output options:")
    print("    -o, --output_location        Location to write the new library to ['../'*]")
    print("    -f, --output_format          [mp3*|alac]")
    print("    -q, --output_quality         MP3 output quality [128|196|320*]")
    print("    -w, --overwrite              Overwrite file if it already exists")
    print("    -e, --embed_covers           Embeds cover art file if available. Requires")
    print("                                 AtomicParsley if converting to ALAC.")
    print("    -c, --cover_name             Filename of cover art [folder.jpg*|...]")
    print("")
    print("Locations:")
    print("    -p, --atomicparsley          Specify alternative path to AtomicParsley")
    print("    -a, --avconv                 Specify alternative path to avconv/ffmpeg")

def which(file):
    for path in os.environ["PATH"].split(os.pathsep):
        if os.path.exists(os.path.join(path, file)):
                return os.path.join(path, file)
    return None
    
def positive_int(value):
    if int(value) < 0:
         raise argparse.ArgumentTypeError("Integer must be positive: %s" % value)
    return int(value)

def parse_arguments():
    parser = argparse.ArgumentParser(prog='PROG', add_help=False)

    options = {}
    options["general"] = parser.add_argument_group('General options')
    options["general"].add_argument(    "-h",   "--help", action="store_true")
    options["general"].add_argument(    "-d",   "--daemonize", action="store_false")
    options["general"].add_argument(    "-n",   "--dry_run", action="store_false")
    options["general"].add_argument(    "-v",   "--verbose", action="store_false")

    options["input"] = parser.add_argument_group('Input options')
    options["input"].add_argument(      "-i",   "--input_location")
    options["input"].add_argument(      "-m",   "--max_depth", type=positive_int)

    options["output"] = parser.add_argument_group('Output options')
    options["output"].add_argument(     "-o",   "--output_location")
    options["output"].add_argument(     "-f",   "--output_format", choices=['mp3', 'alac'], type = str.lower)
    options["output"].add_argument(     "-q",   "--output_quality", choices=[320, 256, 196, 128], type = int)
    options["output"].add_argument(     "-w",   "--overwrite", action="store_true")
    options["output"].add_argument(     "-e",   "--embed_covers", action="store_true")
    options["output"].add_argument(     "-c",   "--cover_name")

    options["locations"] = parser.add_argument_group('Locations')
    options["locations"].add_argument(  "-p",   "--atomicparsley")
    options["locations"].add_argument(  "-a",   "--avconv")

    args = parser.parse_args()
    
    if(args.help):
        help()
        exit()
    
    if args.dry_run is not None:
        settings["dry_run"] = args.dry_run
    
    if args.daemonize is not None:
        settings["daemonize"] = args.daemonize
    
    if args.verbose is not None:
        settings["verbose"] = args.verbose
    
    if args.output_location is not None:
        args.output_location = str(os.path.expanduser(args.output_location))
        if(os.path.isdir(args.output_location) == False):
            print("output_location is not a valid path: "+args.output_location)
            exit(1)
        else:
            location["output"] = args.output_location
    
    if args.input_location is not None:
        args.input_location = str(os.path.expanduser(args.input_location))
        if(os.path.isdir(args.input_location) == False):
            print("input_location is not a valid path: "+args.input_location)
            exit(1)
        else:
            location["input"] = args.input_location
    
    if args.avconv is not None:
        args.avconv = str(os.path.expanduser(args.avconv))
        if(os.path.isfile(args.avconv) == False):
            print("avconv is not a valid path: "+args.avconv)
            exit(1)
        else:
            location["converter"] = args.avconv
    
    if args.atomicparsley is not None:
        args.atomicparsley = str(os.path.expanduser(args.atomicparsley))
        if(os.path.isfile(args.atomicparsley) == False):
            print("atomicparsley is not a valid path: "+args.atomicparsley)
            exit(1)
        else:
            location["embedder"] = args.atomicparsley
    
    if args.max_depth is not None:
        settings["max_depth"] = int(args.max_depth)
    
    if args.overwrite is not None:
        settings["overwrite"] = args.overwrite
    
    if args.output_format is not None:
        settings["output_format"] = str(args.output_format)
    
    if args.output_quality is not None:
        settings["output_quality"] = args.output_quality
    
    if args.cover_name is not None:
        settings["cover_name"] = str(args.cover_name)
    
    if args.embed_covers is not None:
        settings["embed_covers"] = args.embed_covers
        
    location["status"] = os.path.join(location["input"], location["status"])
    #print args

def check_requirements():
    if(os.path.isfile(location["converter"]) == False):
        if(which(location["converter"]) != None):
            location["converter"] = which(location["converter"])
        elif(which(location["alt_converter"]) != None):
            location["converter"] = which(location["alt_converter"])
        else:
            print("Neither FFMPEG or AVCONV seems to be pressent, exiting...")
            exit(1)
    
    if(settings["output_format"] == "alac" and settings["embed_covers"] == True and os.path.isfile(location["embedder"]) == False):
        if(which(location["embedder"]) != None):
            location["embedder"] = which(location["embedder"])
            print("AtomicParsley is found")
        else:
            print("AtomicParsley seems not to be pressent, exiting...")
            exit(1)
    
    if(os.path.isfile(location["status"]) == True):
        print("The target location is already being used by and active instance of bam_extracter, exiting...")
        exit(0)
    open(location["status"], "w+").close()
    

def compile_arguments():
    options = arguments["converter"]+""
    if(settings["overwrite"] == False):
        options = options+" -n"
    if(settings["output_format"] == "mp3"):
        options = options+" -ab "+str(settings["output_quality"])+"k -acodec mp3"
    elif(settings["output_format"] == "alac"):
        options = options+"  -acodec alac"
        settings["output_extension"] = "m4a"
    arguments["converter"] = options

def clean_exit(signal, frame):
    print("Exiting, initiating cleanup")
    status = open(location["status"], "r")
    lastline = status.readline()
    status.close()
    
    if(os.path.isfile(lastline) == True):
        os.remove(lastline)
    if(os.path.isfile(lastline+".tmp") == True):
        os.remove(lastline+".tmp")
    if(os.path.isfile(location["status"]) == True):
        os.remove(location["status"])
        
    print("Done cleaning up, exit.")
    
    exit(0)

def process_locations(path):
    path_relative = os.path.relpath(path, location["input"])
    path_target = os.path.join(location["output"], path_relative)
    
    print(path_target)
    
    if(settings["dry_run"] == False):
        return
    
    if os.path.isdir(path_target) is False:
        os.makedirs(path_target)
    
    if(os.path.isfile(os.path.join(path, settings["cover_name"])) == True):
        shutil.copy(os.path.join(path, settings["cover_name"]), path_target)
    
    for file in os.listdir(path):
        if file.lower().endswith("."+settings["input_format"]) is False:
            continue
        file_input = os.path.join(path, file)
        file_output = os.path.splitext(file)
        file_output = file_output[0]+'.'+settings["output_extension"]
        file_output = os.path.join(path_target, file_output)
        if(os.path.isfile(file_output) == True):
            continue
        print("processing: "+file)
        status = open(location["status"], "w")
        status.write(file_output)
        status.close()
        command = location["converter"]+" -i \""+file_input+"\" "+arguments["converter"]+" \""+file_output+"\" >/dev/null 2>&1"
        subprocess.call([command], shell = True)
        print(CURSOR_UP_ONE + ERASE_LINE + CURSOR_UP_ONE)
        
        if(settings["embed_covers"] == True and settings["output_format"] != 'alac'):
            print("Embedding artwork: " + file_output)
            shutil.move(file_output, file_output+".tmp")
            abs_cover_path = os.path.join(path, settings["cover_name"])
            command = location["converter"]+" -i \""+file_output+".tmp\" -i \""+abs_cover_path+"\" -c copy -map 0 -map 1 -metadata:s:v title=\"Album cover\" -metadata:s:v comment=\"Cover (Front)\" \""+file_output+"\" >/dev/null 2>&1"
            subprocess.call([command], shell = True)
            os.remove(file_output+".tmp")
            print(CURSOR_UP_ONE + ERASE_LINE + CURSOR_UP_ONE)
            
        if(settings["embed_covers"] == True and settings["output_format"] == 'alac'):
            print("Embedding artwork: " + file_output)
            abs_cover_path = os.path.join(path, settings["cover_name"])
            command = location["embedder"]+" \""+file_output+"\" --artwork  \""+abs_cover_path+"\"  --overWrite >/dev/null 2>&1"
            subprocess.call([command], shell = True)
            print(CURSOR_UP_ONE + ERASE_LINE + CURSOR_UP_ONE)
        open(location["status"], "w").close()
    print(CURSOR_UP_ONE + "\t\t\t\t\t\t    done!    ")
    


def walk_locations(path, depth):
    process_locations(path)
    if(settings["max_depth"] != 0 and depth >= settings["max_depth"]):
        return
    for directory in os.listdir(path):
        if os.path.isdir(os.path.join(path, directory)):
            walk_locations(os.path.join(path, directory), depth+1)


parse_arguments()
check_requirements()
compile_arguments()

for sig in [signal.SIGTERM, signal.SIGINT, signal.SIGHUP, signal.SIGQUIT]:
    signal.signal(sig, clean_exit)

walk_locations(location["input"], 0)
clean_exit("","")

print(arguments["converter"])
exit(0)