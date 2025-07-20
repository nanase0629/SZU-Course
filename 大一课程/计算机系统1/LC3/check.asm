.orig x3000
ld r3,a
sti r3,kbsr
again ld r0,b
trap x21
brnzp again
a .fill x4000
b .fill x0032
kbsr .fill xfe00
.end