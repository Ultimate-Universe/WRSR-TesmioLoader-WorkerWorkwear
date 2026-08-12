@echo off
setlocal
clang-cl /nologo /c /O2 /GS- /GR- /EHs-c- /Zl /Foworker_workwear.obj worker_workwear.cpp || exit /b 1
clang --target=x86_64-pc-windows-msvc -c kernel32_import.s -o kernel32_import.obj || exit /b 1
lld-link /dll /nodefaultlib /machine:x64 /opt:ref /opt:icf ^
  /def:worker_workwear.def ^
  /entry:DllMain /subsystem:windows /dynamicbase /highentropyva /nxcompat ^
  /include:__IMPORT_DESCRIPTOR_KERNEL32 ^
  /out:worker_workwear.dll worker_workwear.obj kernel32_import.obj || exit /b 1
python finalize_pe.py worker_workwear.dll || exit /b 1
del /q worker_workwear.obj kernel32_import.obj >nul 2>nul
echo Built worker_workwear.dll
endlocal
