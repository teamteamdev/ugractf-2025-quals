#!/usr/bin/env bash
cd app
rm ../attachments/craftcraft.zip
zip -r ../attachments/craftcraft.zip . -x Dockerfile.kyzylborda
