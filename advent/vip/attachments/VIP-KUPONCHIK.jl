# -*-*-*-*-*-*-*-*-*-*-             install emacs to edit this file (M-x shrink)                -*-*-*-*-*-*-*-*-*-*-*-
# ---------------------------------------------------------------------------------------------------------------------
# Date: 30.02     Author: :)
# File created by AGS Elite.                                                              nikolai.msk.ru/~agrokekstroi/
#
#                                               (C) Author rights protected.
#                                      TheVillage (OOO), AGS Elite (Agrokekstroy JSC).
# ---------------------------------------------------------------------------------------------------------------------
#
#  V       V   ii   PPPP
#   V     V    ii   P   P
#    V   V     ii   PPPP
#     V V      ii   P
#      V       ii   P
#
#  ViP - K U P O N C H I Q U E
#       for entrancing
#      the PRIVATE club
#    <<THE VILLAGE PRO MAX>>
#
# POZDRAVL'AEM VI PRIGLASHENY NA VE4NUU VECHERINKU
# NADO LISH ZAPUSTIT ETOT KUPON V VASHEM RABOCHEM PK.
#
# 1. ECLI HE PA6OTAET, TO OT UMENU ADMINISTRATORA.
#
# 2. ECLI HE PA6OTAET POTOM TO}|{E, YCTAHOBUTE XZ.
#
# 3. ZATEM VVEDITE PAROLCHIK NA KYPOH4IK ....
#
# ---------------------------------------------------------------------------------------------------------------------
module VILLAGE_SMART_KUPON
    import Base.*
    #           1     2     3     4         5        6       7       8        9       10       11
    topics   = ["en", "ru", "de", "buffer", "bound", "code", "auto", "alone", "easy", "coder", "stream"]
    version  = [0x6c, 0x7a, 0x6d, 0x61] |> String
# ---------------------------------------------------------------------------------------------------------------------
#                              DALEE SLEDUYET TEHNICHESKAYA INFORMATSI'YA ... Ne chitat'!
# ---------------------------------------------------------------------------------------------------------------------
const PT                                         = Union{Base.CodeUnits, Array{UInt8}}
const CT                                         = Union{Char, UInt8}
      *(x::T) where T <: PT                      = x |> pointer
      topic(r...)                                = map(Base.Fix1(getindex, topics), r) |> join
      ↓(s, x)                                    = "$(s[begin:x])_$(s[(x + 1):end])"
      *(x::Type)                                 = Ptr{x}
      ⨷(x::CT, y::CT)                            = convert(UInt128, x) ⊻ convert(UInt128, y) |> Char

const XZ                                         = "liblzma.so.5"
const CALL_1                                     = version * (((topic(11, 4, 5) ↓ 12) ↓ 6) ↓ 0)
const CALL_2                                     = version * (((topic(9, 4, 1, 6) ↓ 4) ↓ 11) ↓ 0)
const CALL_3                                     = (version * ((topic(7, 3, 10) ↓ 4) ↓ 0))
const CALL_4                                     = (version * (topic(6) ↓ 0))
const CALL_5                                     = (version * (topic(1, 3)[(1:end - 1)]) ↓ 0)
const ID                                         = [0x00, 0x00, 0xff, 0x12, 0xd9, 0x41, 0x03, 0xc0, 0x39, 0x96, 0x01,
                                                   0x21, 0x01, 0x16, 0x00, 0x00, 0x00, 0x00, 0x98, 0x29, 0x17, 0x01,
                                                   0xe0, 0x00, 0x95, 0x00, 0x31, 0x5d, 0x00, 0x16, 0xe8, 0x91, 0x89,
                                                   0x25, 0x22, 0x04, 0x5b, 0x75, 0xd2, 0xd1, 0xc6, 0xb1, 0x7a, 0x08,
                                                   0x9a, 0xed, 0x93, 0x65, 0xc0, 0xa1, 0xe2, 0x4f, 0xdf, 0xc0, 0x5b,
                                                   0x92, 0x48, 0xa1, 0x58, 0x85, 0xc2, 0x7a, 0xa4, 0x73, 0x43, 0xdd,
                                                   0x16, 0x12, 0x3a, 0x3b, 0xe1, 0x7f, 0x2d, 0xf7, 0x22, 0x4b, 0x00,
                                                   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x49, 0x96, 0x01, 0x00,
                                                   0x00, 0x00, 0xac, 0x3a, 0xf8, 0x0d, 0xa8, 0x00, 0x0a, 0xfc, 0x02,
                                                   0x00, 0x00, 0x00, 0x00, 0x00, 0x59, 0x5a]
const OK                                         = 0
const RUN                                        = 0
const END                                        = 1
println("""
                                 (C) Author rights protected.
                         TheVillage (OOO), AGS Elite (Agrokekstroy JSC).

    V       V   ii   PPPP
     V     V    ii   P   P
      V   V     ii   PPPP
       V V      ii   P
        V       ii   P

      ViP - K U P O N C H I Q U E
         for entrancing
        the PRIVATE club
      <<THE VILLAGE PRO MAX>>

     POZDRAVL'AEM VI PRIGLASHENY NA VE4NUU VECHERINKU

    N ADO LISH ZAPUSTIT ETOT KUPON V VASHEM RABOCHEM PK.

     1. ECLI HE PA6OTAET, TO OT UMENU ADMINISTRATORA.
     2. ECLI HE PA6OTAET POTOM TO}|{E, YCTAHOBUTE XZ.
     3. ZATEM VVEDITE PAROLCHIK NA KYPOH4IK ....

""")
inpb                                             = *(begin print("INSIDE PAROLchik u [ENTER] > "); readline() end,
                                                     ['0' for _ ∈ 1:100] |> String
                                                   ) |> codeunits
inpl                                             = inpb |> length
outb                                             = Vector{UInt8}(
    undef,
    :(
        @ccall XZ.$CALL_1(inpl::Csize_t)::Csize_t
    )                                            |> eval
                                                 )
outl                                             = Ref{Csize_t}(0)
check                                            = 0
clvl                                             = 6
GC.@preserve inpb outb outl                      begin
    ret                                          =  :(
        @ccall XZ.$CALL_2(
            clvl                                 :: UInt32,
            check                                :: UInt32,
            C_NULL                               :: *(Nothing),
            *(inpb)                              :: *(UInt8),
            inpl                                 :: Csize_t,
            *(outb)                              :: *(UInt8),
            outl                                 :: Ref{Csize_t},
            (outb |> length)                     :: Csize_t
        )                                        :: UInt32
    ) |> eval
    ret == OK                                    || error("$ret")
    res                                          =  outb[begin:outl[]] |> copy
    key                                          =  UInt8[0xfd, 0x37, 0x7a, 0x58, 0x5a, 0x00]
    tip                                          =  Vector{UInt8}()
    append!(tip, res...)
    append!(tip, key...)
    append!(tip, ID... )
    length(tip) & 1 == 0 || begin @error("UNFORTUNATELY NOT 2X AND YOU WRONG."); exit() end
end
(lxb, lya, lyb)                                  = (outl[], outl[] + 1, outl[] * 2)
cx                                               = tip[begin:lxb]
cy                                               = tip[lya:lyb]
cx - cy |> sum |> iszero || begin @error("UNFORTUNATELY YOU TRIED AND WRONG. NOT TRY, JUST DO!"); exit() end
# ---------------------------------------------------------------------------------------------------------------------
mutable struct STREAM
    nx                                           :: *(UInt8)
    ai                                           :: Csize_t
    ti                                           :: UInt64
    no                                           :: *(UInt8)
    ao                                           :: Csize_t
    to                                           :: UInt64
    al                                           :: *(Nothing)
    intt                                         :: *(Nothing)
    _a                                           :: *(Nothing)
    _b                                           :: *(Nothing)
    _c                                           :: *(Nothing)
    _d                                           :: *(Nothing)
    _e                                           :: UInt64
    _f                                           :: UInt64
    _g                                           :: Csize_t
    _h                                           :: Csize_t
    _i                                           :: Cint
    _j                                           :: Cint
end
stream                                           =
        STREAM(
          C_NULL, 0,      0,      C_NULL, 0,
          0,      C_NULL, C_NULL, C_NULL, C_NULL,
          C_NULL, C_NULL, 0,      0,      0,
          0,      0,      0
        )
buf                                              = cx
out                                              = Vector{UInt8}(undef, 100)
println("WINNING CONGRATULATIONS! C PRIOBRETENIEM PRO PREMIYM PAKETA! VERY COOL!")
GC.@preserve tip buf out stream                  begin
    stream.nx                                    = *(buf)
    stream.ai                                    = buf |> length
    stream.no                                    = *(out)
    stream.ao                                    = out |> length
    ret                                          = :(@ccall XZ.$CALL_3(
        stream                                   :: Ref{STREAM},
        typemax(UInt64)                          :: UInt64,
        0                                        :: UInt32
    )                                            :: UInt32
    ) |> eval
    while true
        ret                                      = :(
            @ccall XZ.$CALL_4(
                stream                           :: Ref{STREAM},
                RUN                              :: UInt32
            )                                    :: UInt32
        ) |> eval
        (ret == END || ret != OK) && break
        (stream.ai == 0)          && break
    end
    res                                          = String(out) |> Base.Fix2(split, "000") |> first |> codeunits
    @ccall XZ.lzma_end(
        stream                                   :: Ref{STREAM}
    )                                            :: Cvoid
                                                 end
println("PRIOBRETAITE CODE:")
# ---------------------------------------------------------------------------------------------------------------------
key                                              = [0x58, 0x4a, 0x5f, 0x4c, 0x09, 0x24, 0x35, 0x5e, 0x23, 0x0d,
                                                    0x36, 0x3b, 0x3b, 0x24, 0x1c, 0x3c, 0x59, 0x2e, 0x7e, 0x4f,
                                                    0x48, 0x5e, 0x59, 0x6d, 0x46, 0x41, 0x59, 0x56, 0x5f, 0x6e,
                                                    0x45, 0x5e, 0x72, 0x24, 0x3a, 0x20, 0x12, 0x3b, 0x30, 0x3e,
                                                    0x55, 0x0f, 0x2a, 0x34, 0x35, 0x44, 0x14, 0x15, 0x1e, 0x1f]
                                                    key .⨷ res |> String |> println
# ---------------------------------------------------------------------------------------------------------------------
                                                 end
