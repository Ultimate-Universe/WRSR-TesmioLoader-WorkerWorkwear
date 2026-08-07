@echo off
setlocal
clang-cl /nologo /c /O2 /GS- /GR- /EHs-c- /Zl /Foworker_workwear.obj worker_workwear.cpp || exit /b 1
lld-link /dll /noentry /nodefaultlib /machine:x64 /opt:ref /opt:icf ^
  /export:TsmPluginApiVersion /export:TsmPluginInit /export:TsmPluginStart ^
  /out:worker_workwear.dll worker_workwear.obj || exit /b 1
echo Built worker_workwear.dll
endlocal
