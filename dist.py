#!/usr/bin/env python3

"""
NanoRes resource processor: dist script.
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
"""

import os

## Constants
IN_SCRIPT = "nr_gen.py"
OUT_SCRIPT = "nr_gen_aio.py"
DIST_LOC = "dist"
SCAFFOLD_FN = "scaffold.txt"
HEADER_FN = "nano_res.h"
SCAFFOLD_TARGET = f"fstr(scriptParent.joinpath(\"{SCAFFOLD_FN}\"))"
HEADER_TARGET = f"fstr(scriptParent.joinpath(\"{HEADER_FN}\"))"


##Functions
def reprN(instr: str) -> str:
	"""
	Replaces null characters with their escaped equivalents in a given string.

	Args:
		instr (str): The string to run replacements on

	Returns:
		str: The resultant string
	"""
	return instr.replace("\\0", "\\\\0") #Required for preserving null chars. Maybe expand to support all non-printables other than CR, LF, and TAB


## Main
if __name__ == "__main__":
	#Create the output directory
	os.makedirs(DIST_LOC, exist_ok = True)

	#Open the script, scaffold, and header for reading
	#`repr()` is used to preserve non-printable character codes so char literals aren't written
	with open(IN_SCRIPT, "r", encoding="utf-8") as file: script = reprN(file.read())
	with open(SCAFFOLD_FN, "r", encoding="utf-8") as file: scaffold = reprN(file.read())
	with open(HEADER_FN, "r", encoding="utf-8") as file: header = reprN(file.read())

	#Perform the replacements
	scriptout = script.replace(SCAFFOLD_TARGET, f'"""{scaffold}"""')
	scriptout = scriptout.replace(HEADER_TARGET, f'"""{header}"""')

	#Write the output script
	with open(os.path.join(DIST_LOC, OUT_SCRIPT), "w", encoding="utf-8") as file: file.write(scriptout)
