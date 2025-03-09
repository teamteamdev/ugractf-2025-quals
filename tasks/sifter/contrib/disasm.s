00: imm r0, 0x81
02: imm r1, 0x82
04: ldr r2, r0
05: out r2
06: inc r0
07: cmp r0, r1
08: jne 0x4
0a: imm r0, 0x81
0c: in r2
0d: str r0, r2
0e: inc r0
0f: cmp r0, r1
10: jne 0xc
12: imm r0, 0x81
14: out r0
15: imm r0, 0x81
17: dec r1
18: ldr r2, r1
19: str r0, r2
1a: inc r0
1b: cmp r0, r1
1c: jne 0x17
1e: dec r1
1f: ldr r0, r1
20: neg r0
21: dec r1
22: ldr r2, r1
23: dec r2
24: dec r1
25: ldr r3, r1
26: rol r3, 5
28: add r3, r0
29: str r1, r3
2a: dec r1
2b: dec r1
2c: ldr r0, r1
2d: com r0
2e: xor r0, r3
2f: str r1, r0
30: dec r1
31: dec r1
32: ldr r3, r1
33: ror r3, 2
35: add r3, r2
36: str r1, r3
37: dec r1
38: ldr r2, r1
39: rbt r2
3a: xor r2, r0
3b: str r1, r2
3c: inc r1
3d: ldr r0, r1
3e: inc r1
3f: ldr r3, r1
40: rol r3, 7
42: xor r3, r2
43: str r1, r3
44: inc r1
45: ldr r2, r1
46: inc r2
47: add r2, r0
48: str r1, r2
49: inc r1
4a: ldr r2, r1
4b: rbt r2
4c: xor r2, r0
4d: str r1, r2
4e: inc r1
4f: ldr r2, r1
50: dec r2
51: inc r1
52: ldr r0, r1
53: com r0
54: add r0, r2
55: str r1, r0
56: inc r1
57: ldr r0, r1
58: xor r0, r3
59: str r1, r0
5a: inc r1
5b: imm r3, 0x84
5d: ldr r2, r3
5e: dec r2
5f: str r3, r2
60: tst r2
61: jne 0x1e
63: imm r0, 0x81
65: dec r1
66: ldr r3, r1
67: ldr r2, r0
68: inc r0
69: cmp r2, r3
6a: imm r3, 0x84
6c: jne 0xf9
6e: cmp r0, r1
6f: jne 0x65
71: imm r0, 0x81
73: ldr r0, r0
74: imm r1, 0x82
76: imm r3, 0x84
78: ldr r2, r1
79: xor r0, r2
7a: rol r0, 3
7c: str r1, r0
7d: inc r1
7e: ldr r2, r1
7f: add r0, r2
80: neg r0
81: str r1, r0
82: inc r1
83: dec r3
84: tst r3
85: jne 0x78
87: imm r0, 0x81
89: ldr r0, r0
8a: imm r1, 0x82
8c: dec r0
8d: ldr r2, r0
8e: dec r1
8f: ldr r3, r1
90: xor r2, r3
91: str r0, r2
92: imm r3, 0x84
94: cmp r1, r3
95: jne 0x8c
97: imm r3, 0x84
99: str r3, r0
9a: imm r3, 0x84
9c: cmp r0, r3
9d: jne 0x71
9f: jmp 0xf9
a1: jl 0xda
a3: dec r1
a4: unk 0xd5
a5: rbt r0
a6: str r0, r0
a7: xor r2, r1
a8: xor r0, r3
a9: ldr r1, r1
aa: cmp r2, r3
ab: or r0, r1
ac: cmp r1, r1
ad: or r2, r0
ae: xor r0, r0
af: or r0, r0
b0: cmp r1, r0
b1: or r3, r0
b2: or r3, r0
b3: or r3, r1
b4: cmp r3, r3
b5: or r2, r0
b6: cmp r0, r1
b7: and r2, r2
b8: xor r0, r0
b9: ldr r2, r1
ba: cmp r3, r3
bb: or r2, r0
bc: cmp r2, r0
bd: cmp r1, r2
be: cmp r0, r1
bf: cmp r0, r1
c0: cmp r1, r1
c1: cmp r2, r3
c2: xor r2, r3
c3: mov r2, r2
c4: mov r0, r0
c5: shr r1, 27
c7: out r1
c8: unk 0xed
c9: cmp r2, r1
ca: ldr r3, r0
cb: xor r2, r2
cc: str r0, r1
cd: or r1, r1
ce: unk 0xdf
cf: unk 0xe4
d0: unk 0xe2
d1: unk 0xd9
d2: inc r2
d3: unk 0xd7
d4: je 0xc1
d6: cmp r3, r1
d7: inc r2
d8: in r2
d9: com r3
da: dec r3
db: unk 0xd5
dc: rol r1, 156
de: unk 0xe1
df: or r3, r0
e0: mov r0, r3
e1: imm r1, 0x82
e3: add r3, r3
e4: and r1, r1
e5: and r2, r1
e6: and r1, r0
e7: xor r3, r0
e8: mov r3, r2
e9: out r1
ea: inc r0
eb: mov r2, r2
ec: ldr r2, r3
ed: and r2, r3
ee: cmp r2, r1
ef: unk 0xe4
f0: and r2, r2
f1: mov r3, r3
f2: and r3, r1
f3: xor r0, r1
f4: or r1, r3
f5: mov r0, r1
f6: unk 0xf5
f7: out r0
f8: inc r3
f9: ldr r0, r3
fa: tst r0
fb: jne 0xf7
fd: imm r1, 0x82
ff: str r0, r1
