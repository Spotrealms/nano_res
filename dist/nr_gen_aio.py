#!/usr/bin/env python3

### NanoRes resource processor - Version 1.0.1 ###
## Adapted from: https://gist.github.com/rakete/c6f7795e30d5daf43bb600abc06a9ef4
## Call via: nr_gen.py
## Example (one resource): `python .mesondep/nr_gen.py "resources/my-resource.txt"``
## Example (many resources): `python .mesondep/nr_gen.py -d "resources/"``
## Example (single file version): `python nr_gen_aio.py ...`

"""
NanoRes resource processor.
Copyright (C) 2023 Spotrealms Network

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

* Artifacts generated using this tool are NOT bound by the terms of
the GPL. Feel free to apply your own license to these files.
"""

from argparse import ArgumentParser, Namespace
from pathlib import Path
import datetime
import hashlib
import os
import re
import sys

## Constants
MAX_SIZE_MB = 16
OUT_EXT = "nres"
MANIFEST_NAME = "nres_manifest.txt"


## Functions
def fbytes(fPath: Path) -> str:
	"""
	Converts a file, given a path, to a byte stream for representation as a byte array.

	Args:
		fpath (Path): The path to the file

	Returns:
		str: The bytes of the file delimited by commas

	Raises:
		Exception: If the file doesn't exist, its size is 0 bytes, or its size is over 100 MB
	"""

	#Ensure the file path exists before continuing
	if not fPath.exists():
		raise FileNotFoundError(f"The file at path '{fPath.name}' doesn't exist or no path was given")

	#Create the output buffer string
	out: str = ""

	#Attempt to open the file at the path
	with open(fPath, "rb") as fi:
		#Get the size of the file
		fi.seek(0, os.SEEK_END)
		size: int = fi.tell()
		fi.seek(0)

		#Skip files with 0 size
		if size == 0:
			raise RuntimeError("Cannot encode a file that is 0 bytes in size")

		#Refuse to process the file if its over x MB in size
		#1 MB = 1,000,000 Bytes (in decimal)
		if size > MAX_SIZE_MB * 1000000:
			raise RuntimeError(f"Cannot encode a file that is greater than {MAX_SIZE_MB} MB in size. Consider loading and using the resource in a different way")

		#Loop over the file until an EOF is hit
		#This construct emulates a do-while loop and should terminate normally under most circumstances
		begin: bool = True
		while True:
			#Get the current byte
			byte: bytes = fi.read(1)

			#Stop processing at an EOF
			if not byte: break

			#Add a comma to the output buffer unless this is the beginning of the file
			#The else should fire on the first iteration and the if on subsequent iterations
			if not begin:
				out += ","
			else: begin = False

			#Convert the byte to a hex string and append
			out += "0x" + format(ord(byte), "02x")

	#Return the output buffer
	return out

def fstr(fpath: Path) -> str:
	"""
	Reads in a file as a string.

	Args:
		fpath (Path): The path to the file

	Returns:
		str: The file content as a string
	"""

	#Create the output buffer
	out: str = ""

	#Read in the file to the string
	with open(fpath, "r", encoding="utf-8") as fi:
		out = fi.read()

	#Return the buffer
	return out

def replaceStr(instr: str, replacements: dict[str, str]) -> str:
	"""
	Replaces placeholders in a string with a given value. A placeholder is defined as
	a string enclosed in % signs, eg: `%appdata%`.

	Args:
		instr (str): The string to replace placeholders in. Will not be mutated
		replacements (dict[str, str]): The list of placeholders and their replacements

	Returns:
		str: The resultant string with placeholders resolved
	"""

	#Clone the input string for immutability
	out: str = instr

	#Replace each placeholder in the input string
	for key in replacements.keys():
		out = out.replace(f"%{key}%", replacements[key])

	#Return the resulting output string
	return out


## Main
if __name__ == "__main__":
	#Setup the argument parser
	scriptPath: Path = Path(__file__)
	parser: ArgumentParser = ArgumentParser(
		prog=scriptPath.name,
		description=f"Generates `.{OUT_EXT}` embedded resource files for C and C++ programs.",
		epilog=f"Example (one file): `{scriptPath.name} <filename>` ; Example (many files): `{scriptPath.name} -d <directory>`"
	)
	parser.add_argument("-d", "--dir", action="store_true", help="Whether the passed filename is a directory")
	parser.add_argument("-p", "--purge", action="store_true", help=f"Whether to purge the directory specified by the path argument of all .{OUT_EXT} files")
	parser.add_argument("path", help="The path of the file or directory to process")

	#Perform argument parsing and unpack arguments
	args: Namespace = parser.parse_args()
	filePath: Path = Path(args.path)
	isDir: bool = args.dir
	shouldPurge: bool = args.purge

	#Check if the path is valid
	errorText: str = f"Input path '{filePath.name}' does not {{0}}. Try your entry again."
	if not os.path.exists(filePath):
		raise FileNotFoundError(errorText.format("exist"))

	#Check if the file should point to a directory or file
	if (shouldPurge or isDir) and not filePath.is_dir():
		raise FileNotFoundError(errorText.format("point to a directory"))

	#Check if the file should point to a directory or file
	if (not (shouldPurge or isDir)) and not filePath.is_file():
		raise FileNotFoundError(errorText.format("point to a file"))

	#Check if the directory should be purged
	if shouldPurge:
		print(f"Purging directory '{filePath}' of all .{OUT_EXT} files...")
		ctr: int = 0
		for file in Path(os.getcwd()).joinpath(filePath).rglob(f"*.{OUT_EXT}"):
			#Delete the file
			os.remove(file)
			ctr += 1

		#Purge the manifest file if it exists
		manifestPath: Path = Path(os.getcwd()).joinpath(f"{filePath}/{MANIFEST_NAME}")
		if manifestPath.exists():
			os.remove(manifestPath)
			ctr += 1

		#Announce the number of files purged and exit
		print(f"Cleaned up {ctr} resource file{'s' if ctr != 1 else ''}.")
		sys.exit(0)

	#Check if the path should be processed recursively
	globbed: list[Path] = []
	if isDir:
		#Glob the directory
		for file in Path(os.getcwd()).joinpath(filePath).rglob("*"):
			#Skip nres files and directories
			if file.name.endswith(f".{OUT_EXT}") or file.is_dir() or file.name == MANIFEST_NAME: continue
			globbed.append(Path(file))
	else:
		globbed.append(filePath)

	#Load in the scaffolding and shared header
	#These files are required in order for the script to work. They are separate from the script to make editing them easier
	#See `nr_gen_aio.py` for the combined version of this script
	#The last 2 lines in this block will be replaced with multiline string literals by the dist function
	scriptParent: Path = scriptPath.parent
	pwd: Path = Path(os.getcwd())
	scaffold: str = """/**
 * This file was generated by NanoRes: The tiny but mighty resource embedding tool. DO NOT EDIT!
 * File generated on: %date%
 * NanoRes v. 1.0.1
 */

#ifndef %filenameUscore%_%fmd5%
#define %filenameUscore%_%fmd5%


#ifdef __cplusplus
extern "C" {
#endif

%nresHeader%

static const uint8_t %filenameUscore%_%fmd5%_bytes[%filesize%] = {%bytes%};
const NRes %filenameUscore%_%fshortID% = {
	"%fmd5%",
	"%filename%",
	%filesize%,
	%filenameUscore%_%fmd5%_bytes
};


#ifdef __cplusplus
}
#endif

#endif //%filenameUscore%_%fmd5%
"""
	header: str = """#ifndef NANO_RES_H_20230614
#define NANO_RES_H_20230614

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

//C++ support
#ifdef __cplusplus
extern "C" {
#endif

//Stuff for getcwd()
#ifdef NRES_NEED_GETCWD

//FS stuff for getcwd
#ifdef _MSC_VER
	#define WIN32_LEAN_AND_MEAN
	#include <direct.h>
	#include <windows.h>
	#define getcwd _getcwd
	#define PATH_MAX MAX_PATH
#else
	#include <climits>
	#include <unistd.h>
#endif
#ifdef _WIN32
	#define PATH_SEP '\\\\'
#else
	#define PATH_SEP '/'
#endif

//Macros for cwd
#define GETCWD_VAR(name) char name[PATH_MAX]; getcwd(name, sizeof(name));

#endif //NRES_NEED_GETCWD


//Structs
/** Represents an embedded resource. */
typedef struct {
	/** The MD5 hash of the file. This value is always 33 bytes long. */
	const char md5[33]; //+1 for `\\0`

	/** The name of the file, including its extension. */
	const char* filename;

	/** The size of the file in bytes. */
	const size_t size;

	/** The actual data of the file. */
	const uint8_t* data;
} NRes;


//Constants
/** Enum containing status codes for NanoRes operations. */
typedef enum {
	/** The exit code returned when a resource file is successfully written to the disk. */
	SUCCESSFUL = 0,

	/** The exit code returned when a resource file failed to be written to the disk. */
	FAILURE = 1
} NRStatus;


//Functions
/**
 * @brief Writes a nano resource to a real file on the system.
 * 
 * @param obj The source object to write
 * @param path The path to write the file to. Will be substituted for the filename if null or blank
 * @return 0 if successful, 1 if an error occurred
 */
NRStatus nresWrite(const NRes* obj, const char* path){
	//Create a new file and open it for writing
	FILE* out;
	if((out = fopen(path == NULL || path[0] == '\\0' ? obj->filename : path, "wb")) == NULL) 
		return FAILURE; //Fail if the path is invalid or the IO operation isn't allowed

	//Write the bytes to the file
	fwrite(obj->data, sizeof(uint8_t), obj->size, out);

	//Close the stream and return
	fclose(out);
	return SUCCESSFUL;
}

#ifdef __cplusplus
}
#endif

#endif //NANO_RES_H_20230614"""

	#Setup counters
	success: int = 0
	error: int = 0

	#Create a file for the manifest file
	mstartPath: Path = Path(os.getcwd()).joinpath(filePath)
	with open((mstartPath if isDir else mstartPath.parent).joinpath(MANIFEST_NAME), "w", encoding="utf-8") as manifest:
		#Loop over all globbed paths
		idx: int = 0
		for file in globbed:
			try:
				#Begin processing the file
				print(f"[{idx + 1}/{len(globbed)}] Processing '{file.name}'...")

				#Get the bytes, filesize, and the MD5 for the file
				#Strip out non-ASCII characters and ones that neither Windows nor Linux allow in paths; see: https://stackoverflow.com/a/31976060
				filename: str = re.sub(r"[^A-Za-z0-9``~!@#$%^&()-_=+\[\]{};',. ]", "", file.name)
				filenameLegalIdents: str = re.sub(r"[^A-Za-z0-9_]", "_", filename) #Intermediate filename with legal C idents only
				#Avoid creating struct names beginning with numbers as per C ident rules
				filenameUscore: str = "_" + filenameLegalIdents if filenameLegalIdents[0].isdigit() else filenameLegalIdents
				fBytes: str = fbytes(file)
				filesize: int = os.stat(file).st_size
				fmd5: str = ""
				with open(file, "rb") as digest:
					fmd5 = hashlib.md5(digest.read()).hexdigest()
				fshortID: str = fmd5[0:6] #First 6 digits of the file's MD5

				#Run placeholder replacement on the scaffold for this particular resource
				replacementMap: dict[str, str] = {
					"date": str(datetime.datetime.now()),
					"filenameUscore": filenameUscore,
					"fmd5": fmd5,
					"nresHeader": header,
					"filesize": str(filesize),
					"bytes": fBytes,
					"fshortID": fshortID,
					"filename": filename
				}
				encoded: str = replaceStr(scaffold, replacementMap)

				#Write the result to a new file in the same directory as the original, but with the `.nres` extension
				outPath: Path = file.parent.joinpath(filename + f".{OUT_EXT}")
				with open(outPath, "w", encoding="utf-8") as res:
					res.write(encoded)

				#Write information about the file to the manifest
				manifest.write(f"--| {file.relative_to(pwd)} |--\n")
				manifest.write(f"\tResource file: {outPath.name}\n")
				manifest.write(f"\tStruct name: {filenameUscore}_{fshortID}\n")
				manifest.write(f"\tInclusion line for C/C++: `#include \"{outPath.relative_to(pwd)}\"`\n")
				manifest.write(f"\tFilesize (bytes): {filesize}\n")
				manifest.write(f"\tMD5: {fmd5}\n")
				manifest.write("\n")

				#Print results
				print(f"Wrote '{outPath.name}' with MD5 '{fmd5}'. \nThis file can now be referenced via including \
it as '{outPath.name}' with struct variable name '{filenameUscore}_{fshortID}'\n")
				success += 1

			#Handle exceptions
			except (FileNotFoundError, RuntimeError) as e:
				print(f"Caught exception with cause `{e}`. Skipping...\n")
				error += 1

			#Increment the index
			idx += 1

	#Print stats
	print(f"Finished processing the {'file' if not isDir else 'directory'} pointed to by '{filePath}'. Run statistics \
are as follows:\n\tSuccessful: {success}\n\tFailed: {error}\n\tTotal: {idx}")
