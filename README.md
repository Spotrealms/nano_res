# NanoRes

## Overview

### What is it?

NanoRes is a simple resource processor for C and C++. It creates C header files that can be used directly in programs, simply by including the generated file and referring to it by an assigned name. Its main use case is via a build system, whether it be GNU Make, CMake, Meson, etc. This allows executables to contain embedded resources such as OGL shaders, translation units, and so much more. However, this comes at the cost of increased executable size and compilation time. This style of resource inclusion works best for smaller resources that are under 16 MB in size (the default file size limit). Bigger resources should be linked to at runtime rather than statically compiled with the binary. These resources can either be bundled with the program via an installer or downloaded from a remote CDN and unpacked when the time comes to use them.

### Why?

NanoRes was created due to a lack of simple, cross-platform resource processor programs for C and C++. A notable resource processor that meets similar requirements to NanoRes is Bin2Cpp. However, b2cpp was written in C++, making it not easily distributed in binary form with build script templates due to a different binary being needed for each host operating system. Additionally, the tool generates C++ code, making it incompatible for use in C-based projects. NanoRes solves both of these problems by using Python as its host language and generating C headers as opposed to C++ headers. NanoRes' Python backend was chosen due to its simplicity, portability, general availability (especially when using Meson and Ninja), and RAD capabilities. In addition, this allows for easy modification by projects that use this tool, allowing users to customize this tool and/or generated artifacts to fit their own needs.

## Usage

### Options

NanoRes has a few command-line options to control what it does. By default, it takes a single argument, a path, that points to the resource to encode. The resultant C header will be dropped into the same directory as the input resource. The available options are as follows:

- `-h`/`--help`: Shows a simple help menu and exits.
- `-d`/`--dir`: Specifies that the path given points to a directory rather than an individual file. NanoRes will walk the directory and recurse into subdirectories, encoding any file it can find.
- `-p`/`--purge`: Purges the directory pointed to by the path. This will delete any resource files in the specified directory. It is assumed that the input path points to a directory rather than at a single file.

### Failure Conditions

NanoRes will fail to process an existent file if one of the following occurs:
- The file is 0 bytes in size
- The file is greater than 16 MB in size

### Examples

For the following examples, refer to the below sample directory structure to get an idea of a hypothetical environment this tool might run in:
```
project-root/
├── .mesondep/
│   └── nr_gen.py
├── .vscode
├── include
├── resources/
│   ├── lang/
│   │   ├── de.toml
│   │   ├── en_us.toml
│   │   └── fr.toml
│   ├── 20mb.mp4
│   ├── hello.txt
│   └── test.png
├── src
└── meson.build
```

One resource: 
```
$ python .mesondep/nr_gen.py resources/test.png
[1/1] Processing 'test.png'...
Wrote 'test.png.nres' with MD5 'b72262bebbf9d6a9d2b13ea1f51dce7a'. 
This file can now be referenced via including it as 'test.png.nres' with struct variable name 'test_png_b72262'

Finished processing the file pointed to by 'resources/test.png'. Run statistics are as follows:
	Successful: 1
	Fail: 0
	Total: 1
```

Many resources:
```
$ python .mesondep/nr_gen.py -d resources/
[1/6] Processing '20mb.mp4'...
Caught exception with cause `Cannot encode a file that is greater than 16 MB in size. Consider loading and using the resource in a different way`. Skipping...

[2/6] Processing 'test.png'...
Wrote 'test.png.nres' with MD5 'b72262bebbf9d6a9d2b13ea1f51dce7a'. 
This file can now be referenced via including it as 'test.png.nres' with struct variable name 'test_png_b72262'

[3/6] Processing 'hello.txt'...
Wrote 'hello.txt.nres' with MD5 'd9f7c9688960411531aadc4dc1ea4e8f'. 
This file can now be referenced via including it as 'hello.txt.nres' with struct variable name 'hello_txt_d9f7c9'

[4/6] Processing 'de.toml'...
Wrote 'de.toml.nres' with MD5 '06d68f9eddf8230fdd3c23ba1184a1b9'. 
This file can now be referenced via including it as 'de.toml.nres' with struct variable name 'de_toml_06d68f'

[5/6] Processing 'en_us.toml'...
Wrote 'en_us.toml.nres' with MD5 '4a4f0c317865a12104484d9a7d9540d6'. 
This file can now be referenced via including it as 'en_us.toml.nres' with struct variable name 'en_us_toml_4a4f0c'

[6/6] Processing 'fr.toml'...
Wrote 'fr.toml.nres' with MD5 '5fa5833f9f1368443c8a8d103d94ecdf'. 
This file can now be referenced via including it as 'fr.toml.nres' with struct variable name 'fr_toml_5fa583'

Finished processing the directory pointed to by 'resources'. Run statistics are as follows:
        Successful: 5
        Fail: 1
        Total: 6
```

Purging a directory of generated resources:
```
$ python .mesondep/nr_gen.py -p resources/
Purging directory 'resources' of all .nres files...
Cleaned up 5 resource files.
```

As seen in the examples, NanoRes will name output headers with the filename, sans any non-ASCII and illegal characters, eg: `test.txt` becomes `test.txt.nres`. For the actual struct names in these files, the filename becomes the source filename, sans illegal C identifier characters, and the first 6 digits of the file's MD5 hash, eg: `test.txt` becomes `test_txt_d9f7c9`. Keep in mind that any filename starting with a number will automatically have an underscore prepended to the struct name, eg: `3testing.txt` becomes `_3testing_txt_35571d`. This ensures that filenames do not clash with the identifier rules for C. If this information is somehow missed, then this same information will be written to a file called `nres_manifest.txt` in the starting directory that the tool ran in. If the tool ran for a single file, then this manifest file will be placed alongside the processed resource in the same directory.

### Usage In Code

All NanoRes-generated headers ship with the following struct object:
```c
typedef struct {
	/** The MD5 hash of the file. This value is always 33 bytes long. */
	const char md5[33];

	/** The name of the file, including its extension. */
	const char* filename;

	/** The size of the file in bytes. */
	const size_t size;

	/** The actual data of the file. */
	const uint8_t* data;
} NRes;
```

When a resource is converted, an instance of this struct is generated too, allowing various attributes of the file to be accessed in a programmatic way. For example, the size can be obtained via calling `obj.size`. For a file called `hello.txt` of size 42 bytes, the following struct will be generated:
```c
const NRes hello_txt_d9f7c9 = {
	"d9f7c9688960411531aadc4dc1ea4e8f",
	"hello.txt",
	42,
	hello_txt_d9f7c9688960411531aadc4dc1ea4e8f_bytes //Pointer to the raw array of bytes, which immediately precedes this declaration
};
```

Refer to [this C++ source](integration_examples/src/main.cpp) for a complete example of how to use this struct.

### Extras: Current Directory Information

NanoRes also ships with a utility macro to get the current directory as an absolute path. Simply add `#define NRES_NEED_GETCWD` before including any NanoRes generated header and use the macro `GETCWD_VAR(foo)`. This will create a `char*` variable named `foo` with the result of `getcwd()`. In C++17, one may use `std::filesystem::current_path()` instead. For more information on `getcwd()`, see [the documentation](https://linux.die.net/man/3/getcwd). Do keep in mind that this function is also supported in Windows, which is automatically taken care of if using this feature of NanoRes.

## Project Integration

### Overview

This script is simple to include into an existing C/C++ build system. Simply include the following three files into a subdirectory of your choosing:

- `nr_gen.py`: The main script used to generate resources.
- `scaffold.txt`: The base file that is processed to create a resource header. This contains placeholders that are substituted when running this script.
- `nano_res.h`: The common dependencies for the generated headers. This file contains utility functions for working with generated resources as well as the resource struct itself. These items will appear in every resource file generated, but only faces source inclusion once due to the header guard present in this file.

The subdirectory in your build system should look like the following for inclusion to be successful:
```
subdir/
├── nr_gen.py
├── scaffold.txt
└── nano_res.h
```

Do keep in mind that if either `scaffold.txt` or `nano_res.h` are missing, then the script will fail to run. If this behavior is not desired, then consider using the single file version.

### Single File Version

If desired, this script can be run standalone. This enables more flexibility with integration, but at the cost of readability of the artifacts used to generate resource header files. This version of the script might be more desirable if customization isn't a requirement, and may be the best option for most people looking to use this project. To build a standalone version of this script, simply run the dist script via `python dist.py`. An all in one version of the script should now be present in a folder called `dist` with the name `nr_gen_aio.py`. Then, its as simple as just dropping this script in a subdirectory of your project and invoking it where necessary. The subdirectory will look like the following: 
```
subdir/
└── nr_gen_aio.py
```

Usage is identical to the split file version, albeit without the requirements of `scaffold.txt` and `nano_res.h` being in the same directory as the script. The below integration examples all use this AIO version, and can all be found under the `integration_examples` directory.

### Project Integration Example: Make/GNU Make

Because of how much leeway Make gives to the user, there are many ways to integrate into a Make-based project. The following example demonstrates one such way using phony targets. It can be run via `make res`:
```makefile
...
# Variables
RESOURCE_DIR := resources

# Tools
NRES := .scripts/nr_gen_aio.py

# Python commandline
ifeq ($(OS), Windows_NT) #Windows does not use the `python3` binary name for Python
	PYTHON := python
else 
	PYTHON := python3
endif

# Phony rules
.PHONY: res
res:
	@echo RESOURCES $(RESOURCE_DIR)
	$(PYTHON) $(NRES) -d $(RESOURCE_DIR)
...
```

See [Makefile](integration_examples/Makefile) for the unabridged version of this makefile and a complete sample project.

### Project Integration Example: CMake

CMake integration is done via the `execute_process()` function, and is run after the compiler testing stage and before the configuration stage. The following example demonstrates how to do this:
```cmake
...
# Variables
set(RESOURCE_DIR resources)

# Tools
set(NRES .scripts/nr_gen_aio.py)

# Python commandline
if(WIN32) #Windows does not use the `python3` binary name for Python
	set(PYTHON_BIN python)
else()
	set(PYTHON_BIN python3)
endif()

# Pre-build scripts
execute_process(COMMAND ${PYTHON_BIN} ${NRES} -d ${RESOURCE_DIR})
...
```

See [CMakeLists.txt](integration_examples/CMakeLists.txt) for the unabridged version of this script and a complete sample project. For simplicity, the script can be run via `make cmake`. This will generate the required Ninja build files and build the project in one step.

### Project Integration Example: Meson

Meson integration is done via the `run_command()` function, and is run after the compiler testing stage and before the executable configuration stage. The following example demonstrates how to do this:
```py
...
# Variables
RESOURCE_DIR = 'resources'

# Tools
NRES = '.scripts/nr_gen_aio.py'

# Pre-build scripts
nres = run_command(
	find_program('python3', 'python'),
	NRES, '-d', RESOURCE_DIR,
	check: true
)
message(nres.stdout().strip())
...

```

See [meson.build](integration_examples/meson.build) for the unabridged version of this script and a complete sample project. For simplicity, the script can be run via `make meson`. This will generate the required Ninja build files and build the project in one step.

## Contributions

Contributions are welcome and encouraged as long as they are done so in a civilized and professional manner in accordance with the contributor code of conduct outlined below. Feel free to open an issue to report a bugfix or a pull request to suggest new features or fixes. When filling out a bug report, ensure that the bug is clearly outlined and reproducible so that it may be fixed. For pull requests, alignment to the style guide is required to ensure that the code style remains consistent and readable by the project maintainer and other contributors.

### Basic Style Guide

This project enforces code style via [Pylint](https://pylint.readthedocs.io/en/latest/). It can be installed via Pip (`pip install pylint`) or via [your favorite package manager](https://pkgs.org/search/?q=pylint). All contributions should follow this style guide to ensure style consistency. To run Pylint checks, simply call `pylint $(git ls-files '*.py') `. In regards to the scaffold and C header, there is no specific style guide, but care should be taken to ensure that formatting and style resembles what already exists.

### Contributor Code of Conduct

This project's contribution rules align with the "No Code Of Conduct" framework. In short, discussion should only involve the project, eg: bug reports, pull requests, etc. Discussions involving politics, current events, and other dividing subjects will not be tolerated. Please see the [NCoC homepage](https://github.com/domgetter/NCoC) for more info.

## License

This project conforms to the GNU General Public License, version 3 (GPL-3.0-or-later). Projects that use this script don't have to abide by the terms of the GPL, but rather only with regards to the script itself. This entails full source disclosure of any modifications made via a fork of this repository. Inclusion of this script into publicly accessible toolchains must retain the GPL header at the top of the main and dist scripts. The license preamble may be omitted from generated artifacts without penalty, as this script only translates them into a format used by a C/C++ compiler. See [LICENSE.md](LICENSE.md) or [The GPL Homepage](https://www.gnu.org/licenses/gpl-3.0.en.html) for further info.
