# Котёнок: Write-up

Открываем картинку в stegsolve и смотрим, что там есть. На `Red plane 0` виднеется QR-код. Сканируем его и получаем флаг:

![](./writeup/stegsolve.png)

```shell
$ zbarimg -Stest-inverted writeup/stegsolve.png
QR-Code:ugra_you_a_kitty_meow_meow_mrrrp_mrreoww_kvuywpankseraodmcluakvgnwfeoi
scanned 1 barcode symbols from 1 images in 0.15 seconds
```

Флаг: **ugra_you_a_kitty_meow_meow_mrrrp_mrreoww_kvuywpankseraodmcluakvgnwfeoi**
