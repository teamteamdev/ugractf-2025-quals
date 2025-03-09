import dataclasses
import os
import struct
import sys

reg_by_name = { "a": 0, "b": 1, "c": 2, "d": 3 }

@dataclasses.dataclass
class Cmd:
    opcode: int
    argc: int = 0
    has_immediate: bool = False

    def byte(self, args) -> int | None:
        if self.argc == -1: return
        if self.argc == 0: return self.opcode
        if self.argc == 1: return self.opcode | reg_by_name[args[0]]
        if self.argc == 2: return self.opcode | reg_by_name[args[0]] | (reg_by_name[args[1]] << 2)

    def count(self) -> int:
        if self.argc == -1: return 1
        return 1 + int(self.has_immediate)

commands = {
    "nop": Cmd(0x00),
    "mov": Cmd(0x00, 2),
    "add": Cmd(0x10, 2),
    "xor": Cmd(0x20, 2),
    "and": Cmd(0x30, 2),
    "ldr": Cmd(0x40, 2),
    "str": Cmd(0x50, 2),
    "cmp": Cmd(0x60, 2),
    "or": Cmd(0x70, 2),
    "imm": Cmd(0x80, 1, True),
    "neg": Cmd(0x84, 1),
    "com": Cmd(0x88, 1),
    "shl": Cmd(0x8c, 1, True),
    "in": Cmd(0x90, 1),
    "out": Cmd(0x94, 1),
    "tst": Cmd(0x98, 1),
    "rbt": Cmd(0x9c, 1),
    "shr": Cmd(0xa0, 1, True),
    "sar": Cmd(0xa4, 1, True),
    "rol": Cmd(0xa8, 1, True),
    "ror": Cmd(0xac, 1, True),
    "jmp": Cmd(0xb0, 0, True),
    "jl": Cmd(0xb1, 0, True),
    "jbe": Cmd(0xb2, 0, True),
    "jle": Cmd(0xb3, 0, True),
    "jz": Cmd(0xb4, 0, True),
    "js": Cmd(0xb5, 0, True),
    "jc": Cmd(0xb6, 0, True),
    "jo": Cmd(0xb7, 0, True),
    "j0": Cmd(0xb8, 0, True),
    "jge": Cmd(0xb9, 0, True),
    "ja": Cmd(0xba, 0, True),
    "jg": Cmd(0xbb, 0, True),
    "jnz": Cmd(0xbc, 0, True),
    "jns": Cmd(0xbd, 0, True),
    "jnc": Cmd(0xbe, 0, True),
    "jno": Cmd(0xbf, 0, True),
    "inc": Cmd(0xc0, 1),
    "dec": Cmd(0xc4, 1),
    "ud2": Cmd(0xcc),
    "hlt": Cmd(0xff),
    "db": Cmd(0x00, -1, True),
}


@dataclasses.dataclass
class Label:
    name: str
    offset: int = 0

    def __post_init__(self):
        if "+" in self.name:
            self.name, offset = self.name.split('+')
            self.offset = int(offset)
        if "-" in self.name:
            self.name, offset = self.name.split('-')
            self.offset = -int(offset)

@dataclasses.dataclass
class Operation:
    command: Cmd
    args: list[str]
    imm: Label | int

    def pack(self) -> bytes:
        if isinstance(self.imm, Label):
            self.imm = labels[self.imm.name] + self.imm.offset
        if self.command.argc == -1: return struct.pack("<B", self.imm)
        elif self.command.has_immediate: return struct.pack("<BB", self.command.byte(self.args), self.imm)
        else: return struct.pack("<B", self.command.byte(self.args))

@dataclasses.dataclass
class Internal:
    name: str
    arg: any

    def __post_init__(self):
        assert self.name in ["ascii"]
        if self.name == "ascii": self.arg = eval(self.arg).encode()

    def pack(self) -> bytes:
        if self.name == "ascii": return self.arg

    def count(self) -> int:
        if self.name == "ascii": return len(self.arg)

def parse(line) -> Operation | Label | None:
    [line, *comment] = line.split(';', 1)
    if not line.strip(): return
    [insn, *args] = line.split(None, 1)
    if not insn: return
    if insn[-1] == ':': return Label(insn[:-1])
    if insn[0] == '.': return Internal(insn[1:], (args or [None])[0])
    args = (args or [''])[0].split()
    cmd = commands[insn]
    if cmd.has_immediate:
        [*args, imm] = args
        if imm[-1] == 'h' and all(c in "0123456789abcdef" for c in imm[:-1]):
            imm = int(imm[:-1], 16)
        elif imm.isdigit():
            imm = int(imm)
        else:
            imm = Label(imm)
    else: imm = None
    return Operation(cmd, args, imm)

lines = [line for line in (parse(line) for line in sys.stdin.read().split('\n')) if line is not None]

labels = dict()

i = 0
for line in lines:
    if isinstance(line, Label):
        labels[line.name] = i - line.offset
    elif isinstance(line, Operation):
        i += line.command.count()
    elif isinstance(line, Internal):
        i += line.count()

for line in lines:
    if isinstance(line, Operation) or isinstance(line, Internal):
        os.write(1, line.pack())
