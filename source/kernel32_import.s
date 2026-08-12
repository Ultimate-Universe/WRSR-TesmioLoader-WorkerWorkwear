// Minimal conventional PE import descriptor for
// KERNEL32!DisableThreadLibraryCalls. This keeps the no-CRT build independent
// of a Windows SDK import library while still producing a normal PE import.
        .section .idata$2,"dr"
        .p2align 2
        .globl __IMPORT_DESCRIPTOR_KERNEL32
__IMPORT_DESCRIPTOR_KERNEL32:
        .long .Lilt@IMGREL
        .long 0
        .long 0
        .long .Ldllname@IMGREL
        .long .Liat@IMGREL

        .section .idata$3,"dr"
        .p2align 2
        .zero 20

        .section .idata$4,"dr"
        .p2align 3
.Lilt:
        .long .Lhint@IMGREL
        .long 0
        .quad 0

        .section .idata$5,"drw"
        .p2align 3
        .globl __imp_DisableThreadLibraryCalls
.Liat:
__imp_DisableThreadLibraryCalls:
        .long .Lhint@IMGREL
        .long 0
        .quad 0

        .section .idata$6,"dr"
        .p2align 1
.Lhint:
        .short 0
        .asciz "DisableThreadLibraryCalls"
.Ldllname:
        .asciz "KERNEL32.dll"
