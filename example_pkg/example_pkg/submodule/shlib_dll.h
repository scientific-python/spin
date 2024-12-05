#pragma once

// Windows support. When building the `shlib` DLL, this macro expands to
// `__declspec(dllexport)` so we can annotate symbols appropriately as being
// exported. When used in headers consuming a DLL, this macro expands to
// `__declspec(dllimport)` so that consumers know the symbol is defined inside
// the DLL. In all other cases, the macro expands to nothing.
#if defined(SHLIB_DLL_EXPORTS)
    #define SHLIB_DLL __declspec(dllexport)
#elif defined(SHLIB_DLL_IMPORTS)
    #define SHLIB_DLL __declspec(dllimport)
#else
    #define SHLIB_DLL
#endif
