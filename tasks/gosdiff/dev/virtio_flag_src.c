#include <linux/init.h>
#include <linux/module.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("U Tse Cugov and collaborators");
MODULE_DESCRIPTION("Security module");
MODULE_VERSION("6.39");

static int __init virtio_flag_device_init(void)
{
		return 0;
}

static void __exit virtio_flag_device_exit(void)
{
}

module_init(virtio_flag_device_init);
module_exit(virtio_flag_device_exit);
