# Project settings
project(
	'main',
	'cpp',
	version: '1.0',
	default_options: ['cpp_std=c++11', 'warning_level=3', 'werror=false']
)

# Directory variables
RESOURCE_DIR = 'resources'
RESOURCE_DIR_INC = '.'
SRC_DIR = 'src'

# Tools
NRES = '.scripts/nr_gen_aio.py'

# Pre-build scripts
nres = run_command(
	find_program('python3', 'python'),
	NRES, '-d', RESOURCE_DIR,
	check: true
)
message(nres.stdout().strip())

# Includes
includes = include_directories(
	RESOURCE_DIR_INC
)

# Executable settings
executable(
	meson.project_name(),
	[SRC_DIR + '/main.cpp'],
	dependencies: [],
	cpp_args: [],
	link_args: [],
	include_directories: includes,
	install: false,
	win_subsystem: 'console'
)
