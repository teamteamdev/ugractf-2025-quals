import zhuzhelitsa

crypto = zhuzhelitsa.Zhuzhelitsa(None, True)

for p_0 in range(256):
    m = bytes([0, 0, 0, 0, 0, 0, 0, 0])
    fm = bytes([255 if (p_0 >> i) & 1 else 0 for i in range(8)])

    p = [-1] * 256
    used = [False] * 256

    p[0] = p_0
    used[p_0] = True

    ok = True

    while -1 in p:
        c = crypto._encrypt_block(m)
        fc = crypto._encrypt_block(fm)
        tfc = zhuzhelitsa.transpose(fc)
        for i in range(8):
            if p[c[i]] == tfc[i]:
                continue
            if p[c[i]] != -1 or used[tfc[i]]:
                ok = False
                break
            p[c[i]] = tfc[i]
            used[tfc[i]] = True
        if not ok:
            break
        m = c
        fm = fc

    if not ok:
        continue

    print(bytes(p).hex())
