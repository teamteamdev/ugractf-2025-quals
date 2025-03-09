#include <iostream>
#include <cstdio>
#include <cstdint>

static constexpr unsigned char code[256] = {128, 169, 129, 185, 66, 150, 192, 100, 188, 4, 128, 177, 146, 88, 192, 100, 188, 12, 128, 10, 148, 128, 169, 197, 70, 88, 192, 100, 188, 23, 197, 68, 132, 197, 70, 198, 197, 71, 171, 5, 19, 93, 197, 197, 68, 136, 44, 81, 197, 197, 71, 175, 2, 27, 93, 197, 70, 158, 34, 89, 193, 68, 193, 71, 171, 7, 43, 93, 193, 70, 194, 18, 89, 193, 70, 158, 34, 89, 193, 70, 198, 193, 68, 136, 24, 81, 193, 68, 44, 81, 193, 131, 245, 78, 198, 91, 154, 188, 30, 128, 161, 197, 71, 66, 192, 110, 131, 185, 188, 249, 100, 188, 101, 128, 184, 64, 129, 177, 131, 4, 70, 40, 168, 3, 81, 193, 70, 24, 132, 81, 193, 199, 155, 188, 120, 128, 246, 64, 129, 185, 196, 66, 197, 71, 46, 88, 131, 177, 109, 188, 140, 131, 246, 83, 131, 197, 108, 188, 113, 176, 249, 177, 218, 197, 213, 156, 80, 38, 44, 69, 110, 116, 101, 114, 32, 112, 97, 115, 115, 119, 111, 114, 100, 58, 32, 70, 111, 114, 98, 105, 100, 100, 101, 110, 46, 10, 0, 161, 27, 149, 237, 102, 67, 42, 84, 117, 223, 228, 226, 217, 194, 215, 180, 193, 103, 194, 146, 139, 199, 213, 169, 156, 225, 115, 12, 129, 51, 31, 53, 54, 49, 35, 11, 149, 192, 10, 78, 62, 102, 228, 58, 15, 55, 36, 125, 4, 245, 148, 195, 76, 152, 188, 247, 129, 255, 84};

unsigned char data[256] = {128, 169, 129, 185, 66, 150, 192, 100, 188, 4, 128, 177, 146, 88, 192, 100, 188, 12, 128, 10, 148, 128, 169, 197, 70, 88, 192, 100, 188, 23, 197, 68, 132, 197, 70, 198, 197, 71, 171, 5, 19, 93, 197, 197, 68, 136, 44, 81, 197, 197, 71, 175, 2, 27, 93, 197, 70, 158, 34, 89, 193, 68, 193, 71, 171, 7, 43, 93, 193, 70, 194, 18, 89, 193, 70, 158, 34, 89, 193, 70, 198, 193, 68, 136, 24, 81, 193, 68, 44, 81, 193, 131, 245, 78, 198, 91, 154, 188, 30, 128, 161, 197, 71, 66, 192, 110, 131, 185, 188, 249, 100, 188, 101, 128, 184, 64, 129, 177, 131, 4, 70, 40, 168, 3, 81, 193, 70, 24, 132, 81, 193, 199, 155, 188, 120, 128, 246, 64, 129, 185, 196, 66, 197, 71, 46, 88, 131, 177, 109, 188, 140, 131, 246, 83, 131, 197, 108, 188, 113, 176, 249, 177, 218, 197, 213, 156, 80, 38, 44, 69, 110, 116, 101, 114, 32, 112, 97, 115, 115, 119, 111, 114, 100, 58, 32, 70, 111, 114, 98, 105, 100, 100, 101, 110, 46, 10, 0, 161, 27, 149, 237, 102, 67, 42, 84, 117, 223, 228, 226, 217, 194, 215, 180, 193, 103, 194, 146, 139, 199, 213, 169, 156, 225, 115, 12, 129, 51, 31, 53, 54, 49, 35, 11, 149, 192, 10, 78, 62, 102, 228, 58, 15, 55, 36, 125, 4, 245, 148, 195, 76, 152, 188, 247, 129, 255, 84};

template<int which>
static inline uint8_t& reg(uint8_t& r0, uint8_t& r1, uint8_t& r2, uint8_t& r3)
{
    static_assert(which >= 0 && which < 4);
    if constexpr(which == 0)
        return r0;
    else if constexpr(which == 1)
        return r1;
    else if constexpr(which == 2)
        return r2;
    else
        return r3;
}

template<int pc>
static inline void emulate(uint8_t r0, uint8_t r1, uint8_t r2, uint8_t r3, bool z)
{
#define SZ(x) __attribute__((musttail)) return emulate<(pc+(x))>(r0, r1, r2, r3, z)
#define JMP(x) __attribute__((musttail)) return emulate<(x)>(r0, r1, r2, r3, z)
#define REG(x) reg<(x)>(r0, r1, r2, r3)
    enum { opcode = code[(uint8_t)pc] };
    enum { rlow = opcode & 3 };
    enum { rhi = (opcode >> 2) & 3 };
    enum { nextword = code[(uint8_t)(pc+1)] };
    if constexpr(pc >= 256)
        return;
    else if constexpr(opcode >= 0x10 && opcode < 0x20)
    {
        REG(rlow) += REG(rhi);
        SZ(1);
    }
    else if constexpr(opcode >= 0x20 && opcode < 0x30)
    {
        REG(rlow) ^= REG(rhi);
        SZ(1);
    }
    else if constexpr(opcode >= 0x40 && opcode < 0x50)
    {
        REG(rlow) = data[REG(rhi)];
        SZ(1);
    }
    else if constexpr(opcode >= 0x50 && opcode < 0x60)
    {
        data[REG(rlow)] = REG(rhi);
        SZ(1);
    }
    else if constexpr(opcode >= 0x60 && opcode < 0x70)
    {
        z = REG(rlow) == REG(rhi);
        SZ(1);
    }
    else if constexpr(opcode >= 0x80 && opcode < 0x84)
    {
        REG(rlow) = nextword;
        SZ(2);
    }
    else if constexpr(opcode >= 0x84 && opcode < 0x88)
    {
        REG(rlow) = -REG(rlow);
        SZ(1);
    }
    else if constexpr(opcode >= 0x88 && opcode < 0x8c)
    {
        REG(rlow) = ~REG(rlow);
        SZ(1);
    }
    else if constexpr(opcode >= 0x90 && opcode < 0x94)
    {
        REG(rlow) = std::getchar();
        SZ(1);
    }
    else if constexpr(opcode >= 0x94 && opcode < 0x98)
    {
        std::putchar(REG(rlow));
        SZ(1);
    }
    else if constexpr(opcode >= 0x98 && opcode < 0x9c)
    {
        z = !REG(rlow);
        SZ(1);
    }
    else if constexpr(opcode >= 0x9c && opcode < 0xa0)
    {
        uint8_t x = REG(rlow);
        x = (x >> 4) | (x << 4);
        x = ((x & 0xcc) >> 2) | ((x & 0x33) << 2);
        x = ((x & 0xaa) >> 1) | ((x & 0x55) << 1);
        REG(rlow) = x;
        SZ(1);
    }
    else if constexpr(opcode >= 0xa8 && opcode < 0xac)
    {
        enum { sz = nextword & 7 };
        REG(rlow) = (REG(rlow) << sz) | (REG(rlow) >> ((8-sz)%8));
        SZ(2);
    }
    else if constexpr(opcode >= 0xac && opcode < 0xb0)
    {
        enum { sz = nextword & 7 };
        REG(rlow) = (REG(rlow) >> sz) | (REG(rlow) << ((8-sz)%8));
        SZ(2);
    }
    else if constexpr(opcode == 0xb0)
        JMP(nextword);
    else if constexpr(opcode == 0xbc)
    {
        if(z)
            SZ(2);
        else
            JMP(nextword);
    }
    else if constexpr(opcode >= 0xc0 && opcode < 0xc4)
    {
        REG(rlow)++;
        SZ(1);
    }
    else if constexpr(opcode >= 0xc4 && opcode < 0xc8)
    {
        REG(rlow)--;
        SZ(1);
    }
    else if constexpr(opcode == 0xff)
        return;
    else
        std::printf("Unknown opcode 0x%x at 0x%x\n", opcode, pc);
}

int main()
{
    emulate<0>(0, 0, 0, 0, false);
    return 0;
}
