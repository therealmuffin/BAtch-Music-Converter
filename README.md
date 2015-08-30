# BAtch-Music-Converter

BAtch Music Converter (for Linux/Synology)

With the help of ffmpeg this script can convert the format of a music library. This can be
handy to create a paralel library in MP3. Run it once a week and you'll have a nice and up
to date library for mobile use.

If anyone cares input and output formats can be expanded. For now only Flac is supported
as input and MP3 and Alac as output.

<pre>
Usage: ./bam_converter [options...]

Available options are specified in brackets if applicable. The default option is
indicated by an asterisk

General options
    -h, --help                    Show this help
    -d, --daemonize               Daemonize bam_converter

Input options:
    -i, --input_location          Location to read library from ['./'*]

Output options:
    -o, --output_location         Location to write the new library to ['../'*]
    -m, --output_mode             [mp3*|alac]
    -q, --output_quality          MP3 output quality [128|196|320*]
    -w, --overwrite               Overwrite file if it already exists
    -e, --embed_covers            Embeds cover art file if available. Requires
                                  AtomicParsley if converting to ALAC.
    -c, --cover_name              Filename of cover art [folder.jpg*|...]

Locations:
    -p, --atomicparsley           Specify alternative path to AtomicParsley
    -f, --ffmpeg                  Specify alternative path to ffmpeg
</pre>