#include <iostream>
#define NRES_NEED_GETCWD //Adds support structures for getcwd()
#include "resources/hello.txt.nres"

int main(){
	//Resource access
	NRes nrf = hello_txt_d9f7c9;

	//Output location
	GETCWD_VAR(cwd)
	const std::string outDir = std::string(cwd) + PATH_SEP + nrf.filename + ".out";

	std::cout << "fsize: " << nrf.size << std::endl;
	NRStatus state = nresWrite(&nrf, outDir.c_str());
	std::cout << "md5: " << nrf.md5 << std::endl;
	std::cout << "Exported " << nrf.filename << " to " << outDir << " with status code " << state << " (" << (!state ? "SUCCESS" : "FAILURE") << ")" << std::endl;
	return 0;
}