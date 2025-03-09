<?php
passthru("find / -xdev -exec stat -c'u=%u\tg=%g\t%a/%A\t%s\t%N' {} \+ | sort -k5");
