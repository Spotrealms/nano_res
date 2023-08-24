#ifndef NANO_RES_H_20230614
#define NANO_RES_H_20230614

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

//C++ support
#ifdef __cplusplus
extern "C" {
#endif


//Structs
/** Represents an embedded resource. */
typedef struct {
	/** The MD5 hash of the file. This value is always 33 bytes long. */
	const char md5[33]; //+1 for `\0`

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
	if((out = fopen(path == NULL || path[0] == '\0' ? obj->filename : path, "wb")) == NULL) 
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

#endif //NANO_RES_H_20230614