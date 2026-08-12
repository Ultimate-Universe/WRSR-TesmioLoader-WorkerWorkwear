// Worker Workwear v1.1.0
// Workers & Resources: Soviet Republic v1.1.1.9 / TesmioLoader API 4
//
// Forces the dedicated manual-work worker renderer to use only the two
// overall-clad male material variants (muz1 and muz2).
//
// The game normally loads four materials for this renderer:
//   workers2/working2/muz1.mtl
//   workers2/working2/muz2.mtl
//   workers2/working2/muz3.mtl
//   workers2/working2/muz4.mtl
//
// This plugin redirects muz3 -> muz1 and muz4 -> muz2 at the material-load
// seam. Normal citizen appearance selection is not modified.

#include "tesmio_api.h"

extern "C" int _fltused = 0;

typedef int BOOL;
typedef unsigned long DWORD;
typedef void* HINSTANCE;
typedef void* LPVOID;

extern "C" __declspec(dllimport)
BOOL __stdcall DisableThreadLibraryCalls(HINSTANCE module);

extern "C" BOOL __stdcall DllMain(HINSTANCE module, DWORD reason, LPVOID)
{
    if (reason == 1u)
        DisableThreadLibraryCalls(module);
    return 1;
}

// Preserve an image-base relocation so Windows can freely rebase the DLL
// under ASLR even though normal code and data references are RIP-relative.
extern "C" void* volatile g_workerWorkwearRelocationAnchor =
    reinterpret_cast<void*>(&DllMain);

typedef unsigned long long u64;

static const TsmHost* H = 0;
static int g_active = 0;
static unsigned g_seenRedirects = 0;

// public: int C3D_MATERIAL::Load(char const*, enum _C3DFORMAT, int)
// MS x64 member-call ABI: RCX=this, RDX=path, R8=format, R9=flags.
typedef int (__fastcall *tMaterialLoad)(void* self, const char* path, int format, int flags);
static tMaterialLoad o_MaterialLoad = 0;

static char LowerAscii(char c)
{
    if (c >= 'A' && c <= 'Z') return (char)(c + ('a' - 'A'));
    if (c == '\\') return '/';
    return c;
}

static u64 StrLen(const char* s)
{
    if (!s) return 0;
    u64 n = 0;
    while (s[n]) ++n;
    return n;
}

static int EndsWithPathI(const char* full, const char* tail)
{
    if (!full || !tail) return 0;
    const u64 nf = StrLen(full);
    const u64 nt = StrLen(tail);
    if (nt > nf) return 0;
    const u64 off = nf - nt;

    for (u64 i = 0; i < nt; ++i)
        if (LowerAscii(full[off + i]) != LowerAscii(tail[i])) return 0;

    return 1;
}

static int __fastcall h_MaterialLoad(void* self, const char* path, int format, int flags)
{
    const char* use = path;

    if (g_active && EndsWithPathI(path, "workers2/working2/muz3.mtl"))
    {
        use = "workers2/working2/muz1.mtl";
        if ((g_seenRedirects & 1u) == 0u)
        {
            g_seenRedirects |= 1u;
            if (H && H->log)
                H->log("workwear  observed muz3 material; redirected to muz1");
        }
    }
    else if (g_active && EndsWithPathI(path, "workers2/working2/muz4.mtl"))
    {
        use = "workers2/working2/muz2.mtl";
        if ((g_seenRedirects & 2u) == 0u)
        {
            g_seenRedirects |= 2u;
            if (H && H->log)
                H->log("workwear  observed muz4 material; redirected to muz2");
        }
    }

    return o_MaterialLoad ? o_MaterialLoad(self, use, format, flags) : 0;
}

extern "C" unsigned TsmPluginApiVersion(void)
{
    return TSM_API_VERSION;
}

extern "C" int TsmPluginInit(const TsmHost* host, TsmPluginInfo* info)
{
    H = host;
    if (!host || !info || host->apiVersion < TSM_API_VERSION ||
        host->structSize < offsetof(TsmHost, patchIat) + sizeof(host->patchIat))
        return 1;

    info->name = "worker_workwear";
    info->version = "1.1.0";

    if (H->log)
        H->log("workwear  init v1.1.0 - WRSR 1.1.1.9 / API 4");

    return 0;
}

extern "C" int TsmPluginStart(void)
{
    if (!H || !H->exeModule || !H->patchIat) return 1;

    // Revalidated for WRSR v1.1.1.9. The worker renderer in SOVIET64.exe
    // imports this exact exported C3DDLL64 function and
    // passes (this, path, format, flags) under the Microsoft x64 ABI.
    const char* fn = "?Load@C3D_MATERIAL@@QEAAHPEBDW4_C3DFORMAT@@H@Z";

    void* orig = 0;
    int ok = H->patchIat(H->exeModule, "C3DDLL64.DLL", fn,
                         (void*)&h_MaterialLoad, &orig,
                         "worker manual material load");

    if (!ok)
    {
        ok = H->patchIat(H->exeModule, "C3DDLL64.dll", fn,
                         (void*)&h_MaterialLoad, &orig,
                         "worker manual material load");
    }

    if (!ok || !orig)
    {
        if (H->log)
            H->log("workwear  FAILED - C3D_MATERIAL::Load import not found; no patch installed");
        return 1;
    }

    o_MaterialLoad = (tMaterialLoad)orig;
    g_active = 1;

    if (H->log)
        H->log("workwear  installed v1.1.0 - muz3/muz4 redirected to muz1/muz2");

    return 0;
}
