mem = [128, 169, 129, 185, 66, 150, 192, 100, 188, 4, 128, 177, 146, 88, 192, 100, 188, 12, 128, 10, 148, 128, 169, 197, 70, 88, 192, 100, 188, 23, 197, 68, 132, 197, 70, 198, 197, 71, 171, 5, 19, 93, 197, 197, 68, 136, 44, 81, 197, 197, 71, 175, 2, 27, 93, 197, 70, 158, 34, 89, 193, 68, 193, 71, 171, 7, 43, 93, 193, 70, 194, 18, 89, 193, 70, 158, 34, 89, 193, 70, 198, 193, 68, 136, 24, 81, 193, 68, 44, 81, 193, 131, 245, 78, 198, 91, 154, 188, 30, 128, 161, 197, 71, 66, 192, 110, 131, 185, 188, 249, 100, 188, 101, 128, 184, 64, 129, 177, 131, 4, 70, 40, 168, 3, 81, 193, 70, 24, 132, 81, 193, 199, 155, 188, 120, 128, 246, 64, 129, 185, 196, 66, 197, 71, 46, 88, 131, 177, 109, 188, 140, 131, 246, 83, 131, 197, 108, 188, 113, 176, 249, 177, 218, 197, 213, 156, 80, 38, 44, 69, 110, 116, 101, 114, 32, 112, 97, 115, 115, 119, 111, 114, 100, 58, 32, 70, 111, 114, 98, 105, 100, 100, 101, 110, 46, 10, 0, 161, 27, 149, 237, 102, 67, 42, 84, 117, 223, 228, 226, 217, 194, 215, 180, 193, 103, 194, 146, 139, 199, 213, 169, 156, 225, 115, 12, 129, 51, 31, 53, 54, 49, 35, 11, 149, 192, 10, 78, 62, 102, 228, 58, 15, 55, 36, 125, 4, 245, 148, 195, 76, 152, 188, 247, 129, 255, 84]

pc = 0
while pc < len(mem):
    if mem[pc] in range(0x00, 0x10):
        print('%02x: mov r%d, r%d'%(pc, mem[pc] % 4, (mem[pc] >> 2) % 4))
        pc += 1
    elif mem[pc] in range(0x10, 0x20):
        print('%02x: add r%d, r%d'%(pc, mem[pc] % 4, (mem[pc] >> 2) % 4))
        pc += 1
    elif mem[pc] in range(0x20, 0x30):
        print('%02x: xor r%d, r%d'%(pc, mem[pc] % 4, (mem[pc] >> 2) % 4))
        pc += 1
    elif mem[pc] in range(0x30, 0x40):
        print('%02x: and r%d, r%d'%(pc, mem[pc] % 4, (mem[pc] >> 2) % 4))
        pc += 1
    elif mem[pc] in range(0x40, 0x50):
        print('%02x: ldr r%d, r%d'%(pc, mem[pc] % 4, (mem[pc] >> 2) % 4))
        pc += 1
    elif mem[pc] in range(0x50, 0x60):
        print('%02x: str r%d, r%d'%(pc, mem[pc] % 4, (mem[pc] >> 2) % 4))
        pc += 1
    elif mem[pc] in range(0x60, 0x70):
        print('%02x: cmp r%d, r%d'%(pc, mem[pc] % 4, (mem[pc] >> 2) % 4))
        pc += 1
    elif mem[pc] in range(0x70, 0x80):
        print('%02x: or r%d, r%d'%(pc, mem[pc] % 4, (mem[pc] >> 2) % 4))
        pc += 1
    elif mem[pc] in range(0x80, 0x84):
        print('%02x: imm r%d, 0x%x'%(pc, mem[pc] % 4, mem[pc + 1]))
        pc += 2
    elif mem[pc] in range(0x84, 0x88):
        print('%02x: neg r%d'%(pc, mem[pc] % 4))
        pc += 1
    elif mem[pc] in range(0x88, 0x8c):
        print('%02x: com r%d'%(pc, mem[pc] % 4))
        pc += 1
    elif mem[pc] in range(0x8c, 0x90):
        print('%02x: shl r%d, 1'%(pc, mem[pc] % 4))
        pc += 1
    elif mem[pc] in range(0x90, 0x94):
        print('%02x: in r%d'%(pc, mem[pc] % 4))
        pc += 1
    elif mem[pc] in range(0x94, 0x98):
        print('%02x: out r%d'%(pc, mem[pc] % 4))
        pc += 1
    elif mem[pc] in range(0x98, 0x9c):
        print('%02x: tst r%d'%(pc, mem[pc] % 4))
        pc += 1
    elif mem[pc] in range(0x9c, 0xa0):
        print('%02x: rbt r%d'%(pc, mem[pc] % 4))
        pc += 1
    elif mem[pc] in range(0xa0, 0xa4):
        print('%02x: shr r%d, %d'%(pc, mem[pc] % 4, mem[pc+1]))
        pc += 2
    elif mem[pc] in range(0xa4, 0xa8):
        print('%02x: sar r%d, %d'%(pc, mem[pc] % 4, mem[pc+1]))
        pc += 2
    elif mem[pc] in range(0xa8, 0xac):
        print('%02x: rol r%d, %d'%(pc, mem[pc] % 4, mem[pc+1]))
        pc += 2
    elif mem[pc] in range(0xac, 0xb0):
        print('%02x: ror r%d, %d'%(pc, mem[pc] % 4, mem[pc+1]))
        pc += 2
    elif mem[pc] in range(0xb0, 0xc0):
        insn = ["jmp", "jl", "jbe", "jle", "je", "js", "jb", "jo", "nop", "jge", "ja", "jg", "jne", "jns", "jae", "jno"][mem[pc] - 0xb0]
        print('%02x: %s 0x%x'%(pc, insn, mem[pc+1]))
        pc += 2
    elif mem[pc] in range(0xc0, 0xc4):
        print('%02x: inc r%d'%(pc, mem[pc] % 4))
        pc += 1
    elif mem[pc] in range(0xc4, 0xc8):
        print('%02x: dec r%d'%(pc, mem[pc] % 4))
        pc += 1
    elif mem[pc] == 0xff:
        print('%02x: hlt')
        pc += 1
    else:
        print('%02x: unk 0x%x'%(pc, mem[pc]))
        pc += 1
