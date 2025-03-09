#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/fs.h>
#include <linux/sched.h>
#include <linux/fs_struct.h>
#include <asm/uaccess.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("U Tse Cugov and collaborators");
MODULE_DESCRIPTION("Security module");
MODULE_VERSION("6.39");

#define DEVICE_NAME "flag"
#define N \
	5
const char data[] = {
	'\x26', '\x32', '\x20', '\x35', '\x18', '\x01', '\x39', '\x37', '\x2a', '\x38', '\x14', '\x1a', '\x07', '\x18', '\x01', '\xf8', '\xd3', '\xfc', '\xed', '\xef', '\xd0', '\xcb', '\xfc', '\xca', '\xfc', '\xce', '\xcd', '\xd2', '\xdb', '\xe5', '\x8e', '\xa8', '\xbe', '\xa4', '\xa2', '\x84', '\x80', '\x87', '\x9d', '\x8c', '\x9a', '\xa0', '\x8a', '\x8c', '\xa0', '\x22', '\x27', '\x24', '\x25', '\x23',
};

static int virtio_flag_device_open(struct inode *, struct file *);
static int virtio_flag_device_release(struct inode *, struct file *);
static ssize_t virtio_flag_device_read(struct file *, char *, size_t, loff_t *);
static ssize_t virtio_flag_device_write(struct file *, const char *, size_t, loff_t *);
static int major_num;
static int device_open_count = 0;
static int pos = 0;
static char forty;

static struct file_operations file_ops =
{
	.read = virtio_flag_device_read,
	.write = virtio_flag_device_write,
	.open = virtio_flag_device_open,
	.release = virtio_flag_device_release
};

char virtio_flag_chr(loff_t);
char virtio_flag_chr(loff_t buffer)
{
	bool amend = false;
	if (buffer < 0 || buffer >= sizeof(data))
	{
		return 0;
	}
	if (buffer % N == 0)
	{
		buffer += 1;
	}
	else if (buffer % N == 1)
	{
		buffer += 1;
	}
	else if (buffer % N == 2)
	{
		buffer += 1;
	}
	else if (buffer % N == 3)
	{
		buffer -= 3;
	}
	if (buffer % N == N - 1)
	{
		amend = true;
	}

	char ret = data[buffer] ^ forty;

	if (amend) {
		forty += 0x17;
		forty &= 0xff;
	}

	return ret;
}

static ssize_t virtio_flag_device_read(struct file *flip, char *buffer, size_t len, loff_t *offset)
{
	char c = virtio_flag_chr(*offset);
	if (c == 0)
	{
		return 0;
	}

	put_user(c, buffer++);
	++(*offset);
	return 1;
}

static ssize_t virtio_flag_device_write(struct file *flip, const char *buffer, size_t len, loff_t *offset)
{
	return -EINVAL;
}

static int virtio_flag_device_open(struct inode *inode, struct file *file)
{
	if (device_open_count > 0)
	{
		return -EBUSY;
	}
	device_open_count++;
	pos = 0;
	forty = 0x4b;
	forty -= 0x04;
	try_module_get(THIS_MODULE);
	return 0;
}

static int virtio_flag_device_release(struct inode *inode, struct file *file)
{
	device_open_count--;
	module_put(THIS_MODULE);
	forty += 0x25;
	return 0;
}

static int __init virtio_flag_device_init(void)
{
	major_num = register_chrdev(0, DEVICE_NAME, &file_ops);
	if (major_num < 0)
	{
		printk(KERN_ALERT "Could not register device: %d\n", major_num);
		return major_num;
	}
	else
	{
		printk(KERN_INFO DEVICE_NAME " loaded, major = %d\n", major_num);
		return 0;
	}
}

static void __exit virtio_flag_device_exit(void)
{
	unregister_chrdev(major_num, DEVICE_NAME);
}

module_init(virtio_flag_device_init);
module_exit(virtio_flag_device_exit);
