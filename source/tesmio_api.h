// Minimal TesmioLoader API 4 contract used by Worker Workwear.
//
// Only the stable TsmHost prefix through patchIat is required. Keeping this
// local header small makes the plugin's actual loader dependency explicit and
// avoids publishing unrelated service declarations.

#ifndef WORKER_WORKWEAR_TESMIO_API_H
#define WORKER_WORKWEAR_TESMIO_API_H

#include <stddef.h>

#define TSM_API_VERSION 4u

typedef struct TsmHost
{
    unsigned apiVersion;
    unsigned structSize;

    void*          exeModule;
    unsigned char* exeBase;
    size_t         exeSize;
    void*          engineModule;
    const char*    baseDir;
    const char*    pluginDir;

    void (*log)(const char* fmt, ...);

    void** (*findIatSlot)(void* module, const char* dll, const char* fn);
    int (*patchIat)(void* module, const char* dll, const char* fn,
                    void* detour, void** original, const char* label);
} TsmHost;

typedef struct TsmPluginInfo
{
    const char* name;
    const char* version;
} TsmPluginInfo;

#endif // WORKER_WORKWEAR_TESMIO_API_H
