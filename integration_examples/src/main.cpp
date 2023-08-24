#include <iostream>
#include "resources/hello.txt.nres"

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
	#define PATH_SEP '\\'
#else
	#define PATH_SEP '/'
#endif

int main(){
	//Resource access
	NRes nrf = hello_txt_d9f7c9;

	//Output location
	char cwd[PATH_MAX];
	getcwd(cwd, sizeof(cwd));
	const std::string outDir = std::string(cwd) + PATH_SEP + nrf.filename + ".out";

	std::cout << "fsize: " << nrf.size << std::endl;
	NRStatus state = nresWrite(&nrf, outDir.c_str());
	std::cout << "md5: " << nrf.md5 << std::endl;
	std::cout << "Exported " << nrf.filename << " to " << outDir << " with status code " << state << " (" << (!state ? "SUCCESS" : "FAILURE") << ")" << std::endl;
	return 0;
}