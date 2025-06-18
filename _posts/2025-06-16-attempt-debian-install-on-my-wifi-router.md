---
layout: post
title: Attempt Debian install on my WiFi router
excerpt: Linksys EA7250 doesn't have a wireless driver to run OpenWRT, but it's got a whopping 2 cores of ARMv7 CPU which are better then those MIPS processors commonly found in these cheap routers out there. Let's not get this goes to waste and make a custom Debian build for it to see how it stacks up against a Raspberry Pi 4 I have laying around.
---

Last year, as I was on the hunt for some cheap routers with interesting features as a hobby (yes I'm kind of a router enjoyer myself, but people collect weird things all the time, aren't they), I stumbled upon this rare species, the [Linksys EA7500v3]() (specs below) which unlike many other Linksys models has ARM CPU. I specifically only look for those with mediatek chips because these have great support in Linux. Later on, I discovered that those wireless chips in this particular CPU have yet to get any open source driver support in OpenWRT, also the second ARM doesn't work in OpenWRT. In the end, I bought it anyway because without wireless, this could still be a good host for experimenting with custom linux build and a greate oppotunity for me to learn some kernel driver development.

__Specs__:
- CPU: Mediatek 
- RAM: 
- Flash:
- Wireless:
- Wire:
- Unique features:

## Contents
* TOC
{:toc}

## TLDR
My youtube video briefing the process and showcasing final result

## Get It Open
I like these new Linksys router for the sturdy shell which has a smaller footprint than their previous design and seems like it could take some beating before it breaks, but man I hate it every single time I have to crack it open with those dump clips that just break off afterward or warp the hell out the edges.

![EA7250 bottom view](/assets/imgs/2025-06-16/ea7250-bot.jpeg)

Anyway, I got it open with 4 screws, 2 under the label and 2 under the rubber feet. Please don't mind the dust and my glue job there. 

![PCB top view](/assets/imgs/2025-06-16/ea7250-pcb.jpeg)

The board is identical to the one in the Linksys EA7250 which bought recently, in fact, there's nothing to distinguish the two from the outside aside from their labels on the bottom. Here is a pcb comparison, top is EA7250, bottom is EA7500v3.

![PCB compare](/assets/imgs/2025-06-16/ea7250-ea7500v3-pcbs.jpeg)

Both PCBs have the jumper header pins populated on their left edges. No visible marking on which is which, but we all know that's UART and it's trivial to figure them out with a multimeter by checking their connectivity (powered OFF) and voltage level (powered ON):
- If pin X is connected to some large metal shell of a USB connector or eletromagnetic shield (those right under the heatsinks) -> that's __Ground__
- When the device powered on, if pin X voltage is constantly at 3.3v or 5v, it could either be __VCC__ or __RX__ 
- If pin X voltage keeps changing, that's __TX__

We only need 3 pins to talk to it, here's what I found

![PCB uart](/assets/imgs/2025-06-16/ea7250-uart.jpeg)

## Explore u-boot
__First object__: Dump the firmware

There are generally two way to go around this, but in my book and from 'experience' I have narrowed it down to just this one way that I swear by: Kindly ask u-boot to give it to me one piece at a time. Also we should also see what else the stock u-boot can do while we're at it.

```
MT7629> help
?       - alias for 'help'
backup_message- print backup message.
base    - print or set address offset
bdinfo  - print Board Info structure
boot    - boot default, i.e., run 'bootcmd'
bootd   - boot default, i.e., run 'bootcmd'
bootm   - boot application image from memory
bootmenu- ANSI terminal bootmenu
bootp   - boot image via network using BOOTP/TFTP protocol
chpart  - change active partition
cmp     - memory compare
coninfo - print console devices and information
cp      - memory copy
crc32   - checksum calculation
custom_image_check- check if image in load_addr is normal.
download_setting- set download image file name , and device IP , server IP before upgrade
echo    - echo args to console
editenv - edit environment variable
env     - environment handling commands
esw_read- esw_read   - Dump external switch/GMAC status !!

exit    - exit script
false   - do nothing, unsuccessfully
fdt     - flattened device tree utility commands
filesize_check- check if filesize of the image that you want to upgrade is normal.
go      - start application at address 'addr'
gpio_dump- enable utif debug function.
help    - print command description/usage
image_blks- read image size from img_size or image header if no specifying img_size, and divided by blk_size and save image blocks in image_blks variable.
image_check- check if image in load_addr is normal.
iminfo  - print header information for application image
imxtract- extract a part of a multi-image
invaild_env- need to invaild env.
itest   - return true/false on integer compare
loadb   - load binary file over serial line (kermit mode)
loads   - load S-Record file over serial line
loadx   - load binary file over serial line (xmodem mode)
loady   - load binary file over serial line (ymodem mode)
loop    - infinite loop on address range
md      - memory display
mdio    - mdio   - Mediatek PHY register R/W command !!

mm      - memory modify (auto-incrementing address)
mtdparts- define flash/nand partitions
mtk_image_blks- read image size from image header (MTK format) located at load_addr, divided by blk_size and save image blocks in image_blks variable.
mw      - memory write (fill)
n9_jtag - switch GPIO to AUX6 for N9 jtag debug.
n9_uart - switch GPIO to AUX6 for N9 UART output.
nand    - NAND sub-system
nboot   - boot from NAND device
nm      - memory modify (constant address)
ping    - send ICMP ECHO_REQUEST to network host
printenv- print environment variables
reco_message- print recovery message.
reg     - reg   - Mediatek PHY register R/W command !!

reset   - Perform RESET of the CPU
run     - run commands in an environment variable
saveenv - save environment variables to persistent storage
serious_image_check- seriously check if image in load_addr is normal.
setenv  - set environment variables
showvar - print local hushshell variables
sleep   - delay execution for some time
snor    - snor   - spi-nor flash command

source  - run script from memory
test    - minimal test like /bin/sh
tftpboot- boot image via network using TFTP protocol
true    - do nothing, successfully
uboot_check- check if uboot in load_addr is normal.
uid     - uid    - Read Unique ID from spi-nor flash

utif_debug- enable utif debug function.
version - print monitor, compiler and linker version
```

And of course we have to get the environment variables

```
MT7629> printenv
arch=arm
auto_recovery=yes
baudrate=115200
board=leopard_evb
board_name=leopard_evb
boot0=download_setting kernel;tftpboot ${loadaddr} ${kernel_filename};bootm
boot1=download_setting kernel;tftpboot ${loadaddr} ${kernel_filename};run boot_wr_img;run write_image2;run boot_rd_img;bootm
boot2=run boot_rd_img;bootm
boot3=download_setting uboot;tftpboot ${loadaddr} ${uboot_filename};run wr_uboot;invaild_env
boot4=loadb;run wr_uboot;invaild_env
boot5=download_setting ctp;tftpboot ${loadaddr} ${ctp_filename};run wr_ctp
boot6=run wr_cumstom_image;invaild_env
boot7=download_setting flashimage;tftpboot ${loadaddr} ${flashimage_filename};run wr_flashimage;invaild_env
boot8=nand read ${loadaddr} 0x29c0000 0x2800000;nand erase.spread 0x1C0000  0x2800000;image_blks 2048;nand write ${loadaddr} 0x1C0000 0x2800000;run boot2
boot9=nand read ${loadaddr} 0x29c0000 0x2000;image_blks 2048;nand read ${loadaddr} 0x29c0000 ${img_align_size};bootm
boot_part=2
boot_part_ready=3
boot_rd_ctp=nand read 0x40000000 0x1C0000 0xF20000
boot_rd_img=nand read ${loadaddr} 0x1C0000 0x2000;image_blks 2048;nand read ${loadaddr} 0x1C0000 ${img_align_size}
boot_ver=0.1.3
boot_wr_img=filesize_check 0x2800000;if test ${filesize_result} = good; then image_blks 131072;nand erase.spread 0x1C0000  ${filesize};image_blks 2048;nand write ${loadaddr} 0x1C0000 ${filesize};fi
bootcmd=No
bootdelay=3
bootfile=lede_uImage
bootimage=2
bootmenu_0=1. System Load Linux to SDRAM via TFTP.=run boot0
bootmenu_1=2. System Load Linux Kernel then write to Flash via TFTP.=run boot1
bootmenu_2=3. Boot system code via Flash.=run boot2
bootmenu_3=4. System Load U-Boot then write to Flash via TFTP.=run boot3
bootmenu_4=5. System Load U-Boot then write to Flash via Serial.=run boot4
bootmenu_5=6. System Load CTP then write to Flash via TFTP.=run boot5
bootmenu_6=7. Debugger load image then write to Flash.=run boot6
bootmenu_7=8. System Load flashimage then write to Flash via TFTP.=run boot7
bootmenu_delay=30
cbt_env_flag=1
cpu=armv7
ctp_filename=ctp.bin
ethact=mtk_eth
ethaddr=00:0C:E7:11:22:33
flashimage_filename=flashimage.bin
invaild_env=no
ipaddr=192.168.1.1
kernel_filename=7531.bin
loadaddr=0x42007F1C
recovery_enable=1
serverip=192.168.1.100
soc=leopard
stderr=serial
stdin=serial
stdout=serial
uboot_filename=u-boot-mtk.bin
vendor=mediatek
wr_ctp=filesize_check 0xF20000;if test ${filesize_result} = good; then nand erase.spread 0x1C0000 0xF20000 ;nand write ${loadaddr} 0x1C0000 0xF20000;fi
wr_cumstom_image=custom_image_check 0x8000000;if test ${img_result} = good; then nand erase.chip ;nand write 0x40000000 0x0 0x1800000;fi
wr_flashimage=filesize_check 0x8000000;if test ${filesize_result} = good; then nand erase.chip ;nand write ${loadaddr} 0x0 ${filesize};fi
wr_uboot=filesize_check 0x100000;if test ${filesize_result} = good; then mtk_image_blks 131072;nand erase.spread 0x00000  ${filesize} ;mtk_image_blks 2048;nand write ${loadaddr} 0x00000 ${filesize};fi
write_image2=filesize_check 0x2800000;if test ${filesize_result} = good; then image_blks 131072;nand erase.spread 0x29c0000  ${filesize};image_blks 2048;nand write ${loadaddr} 0x29c0000 ${filesize};fi

Environment size: 3256/4092 bytes
```

And the flash map too, but unfortunately mtdparts variable wasn't set, so u-boot isn't aware of the mtd partition. In fact, the default bootmenu option 2 `boot2` calls function `boot_rd_img` to load the kernel using `nand` command at fix offset `0x1C0000` into memory, and boot from there. We could still get the flash layout which shows up linux boot log that I have captured in the last boot, along with some extra info on flash chip as well.

```
[    0.826048] Recognize NAND: ID [
[    0.829109] c2 12 
[    0.831128] ], [MX35LF1GE4AB], Page[2048]B, Spare [64]B Total [128]MB
[    0.837952] nand: device found, Manufacturer ID: 0xc2, Chip ID: 0x12
[    0.844321] nand: Macronix SNAND 128MiB 3,3V 8-bit
[    0.849115] nand: 128 MiB, SLC, erase size: 128 KiB, page size: 2048, OOB size: 64
[    0.856701] [NAND]select ecc bit:4, sparesize :64
[    0.861452] 9 ofpart partitions found on MTD device MTK-SNAND
[    0.867214] Creating 9 MTD partitions on "MTK-SNAND":
[    0.872274] 0x000000000000-0x000000100000 : "Bootloader"
[    0.889418] 0x000000100000-0x000000140000 : "Config"
[    0.905443] 0x000000140000-0x0000001c0000 : "Factory"
[    0.921888] 0x0000001c0000-0x0000029c0000 : "Kernel"
[    0.982719] 0x0000029c0000-0x0000051c0000 : "Kernel2"
[    1.051943] 0x0000029c0000-0x000002b80000 : "kernel"
[    1.069425] 0x000002b80000-0x0000051c0000 : "rootfs"
[    1.118419] mtd: device 6 (rootfs) set to be root filesystem
[    1.157006] 1 squashfs-split partitions found on MTD device rootfs
[    1.163200] 0x0000048c0000-0x0000051c0000 : "rootfs_data"
[    1.197789] 0x0000051c0000-0x000005200000 : "devinfo"
[    1.204161] 0x000005200000-0x000005300000 : "sysdiag"
[    1.211096] 0x000005300000-0x000007300000 : "syscfg"
[    1.252927] 0x000007300000-0x000007340000 : "s_env"
```

## Dump the stock firmware

Now that we've seen how u-boot ask for the kernel from flash using `nand` command, let's ask u-boot to give it the entire flash content including the spare area.

```
MT7629> help nand
nand - NAND sub-system

Usage:
nand info - show available NAND devices
nand device [dev] - show or set current device
nand read - addr off|partition size
nand write - addr off|partition size
    read/write 'size' bytes starting at offset 'off'
    to/from memory address 'addr', skipping bad blocks.
nand read.raw - addr off|partition [count]
nand write.raw - addr off|partition [count]
    Use read.raw/write.raw to avoid ECC and access the flash as-is.
nand erase[.spread] [clean] off size - erase 'size' bytes from offset 'off'
    With '.spread', erase enough for given file size, otherwise,
    'size' includes skipped bad blocks.
nand erase.part [clean] partition - erase entire mtd partition'
nand erase.chip [clean] - erase entire chip'
nand bad - show bad blocks
nand dump[.oob] off - dump page
nand scrub [-y] off size | scrub.part partition | scrub.chip
    really clean NAND erasing bad blocks (UNSAFE)
nand markbad off [...] - mark bad block(s) at offset (UNSAFE)
nand biterr off - make a bit error at offset (UNSAFE)
```

It looks like could you `nand dump <start address in hex>` to dump a single page (2048-byte main + 64-byte spare) starting at that address

```
MT7629> nand dump 0
Address 0 dump (2048):
42 4f 4f 54 4c 4f 41 44 45 52 21 00 56 30 30 36 4e 46 49 49 4e 46 4f 00 00 00 00 08 05 00 40 00
40 00 00 08 10 00 16 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 b1 11 39 64 db 22 23 de c5 24 e5 fe 2c 7f ba d0 2a ba e5 b2 2e 08 01 41 f1 24 00 00
42 4f 4f 54 4c 4f 41 44 45 52 21 00 56 30 30 36 4e 46 49 49 4e 46 4f 00 00 00 00 08 05 00 40 00
40 00 00 08 10 00 16 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 b1 11 39 64 db 22 23 de c5 24 e5 fe 2c 7f ba d0 2a ba e5 b2 2e 08 01 41 f1 24 00 00
42 4f 4f 54 4c 4f 41 44 45 52 21 00 56 30 30 36 4e 46 49 49 4e 46 4f 00 00 00 00 08 05 00 40 00
40 00 00 08 10 00 16 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 b1 11 39 64 db 22 23 de c5 24 e5 fe 2c 7f ba d0 2a ba e5 b2 2e 08 01 41 f1 24 00 00
42 4f 4f 54 4c 4f 41 44 45 52 21 00 56 30 30 36 4e 46 49 49 4e 46 4f 00 00 00 00 08 05 00 40 00
40 00 00 08 10 00 16 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 b1 11 39 64 db 22 23 de c5 24 e5 fe 2c 7f ba d0 2a ba e5 b2 2e 08 01 41 f1 24 00 00

ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff

ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff

ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff

OOB (64):
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff
ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff 00 00 00 00 00 00 00 00
```

To automate this, I prepare a python script to ask u-boot for one page at a time and save the result into a `dump-<hex address>.bin` file, and the reason for including the starting address is because it will take a long time (1.6s for each page) and my uart adapter may give up at some point, thus i have to concatenate multiple `.bin` files to get the entire flash. 

```python
{% include snippets/dump-nand.py %}
```

## I did messed it up the first time

The other way to dump the flash I didn't want to mention is to lift the flash chip (located on the back) off the pcb and use a chip programmer to read the it, you'll get the entire flash content in less in 2 minutes (at least on my XGecu T48). In fact, I attempted this on the first victim, the EA7500v3 and no matter how much heat I gave it, I couldn't make it budge but ended up lifting it off in pieces (yes skill issue isn't it). The failure haunted me since, but I would still try it for the secret sauce on things I would never use again. Which comes to the second problem, it's not that I'm afraid of lifting up chips, it's just those leadless one (like WSON-8 which have no 'legs') because putting them back on the board feels impossible, and I have accompished 0 so far. This feels like a bit of a rant too.

## Recover

With the chip showing off its shiny silicon, the idea of running debian on this ARM chip goes down the drain. However, by coincident early this year, I found another ad about this EA7250 which has no entry in OpenWRT device list or any other device wiki sites at the time, so I went straight to Linksys support website for this model and got myself a copy of the firmware. Thankfully there is encryption as expected, I was able to disect it with binwalk and got my hand on the lovely [linux dts](https://www.kernel.org/doc/html/latest/devicetree/usage-model.html) file

```c
/dts-v1/;

/ {
	timestamp = <0x621974e5>;
	description = "ARM OpenWrt FIT (Flattened Image Tree)";
	#address-cells = <0x01>;

	images {

		kernel@1 {
			description = "ARM OpenWrt Linux-4.4.146";
			data = <some binary>;
			type = "kernel";
			arch = "arm";
			os = "linux";
			compression = "lzma";
			load = <0x40008000>;
			entry = <0x40008000>;

			hash@1 {
				value = <0x1587a0f5>;
				algo = "crc32";
			};

			hash@2 {
				value = <0xdf353030 0x8a23dbe4 0x60b460f4 0xe5212e84 0x72785209>;
				algo = "sha1";
			};
		};

		fdt@1 {
			description = "ARM OpenWrt MT7629-LYNX-RFB3 device tree blob";
			data = [some more binary];
			type = "flat_dt";
			arch = "arm";
			compression = "none";

			hash@1 {
				value = <0x5ea132d0>;
				algo = "crc32";
			};

			hash@2 {
				value = <0x83209e24 0xc92bef00 0x56e693f8 0x276b2df7 0xa00e5266>;
				algo = "sha1";
			};
		};
	};

	configurations {
		default = "config@1";

		config@1 {
			description = "OpenWrt";
			kernel = "kernel@1";
			fdt = "fdt@1";
		};
	};
};
```

We could dig deeper for the full tree with all the hardware by decoding the binary (which I leave out) in fdt@1, but knowing just the cpu is good enough. With that detail and seller's pictures, this one feels like 'old wine in new bottles' (I just looked up this one, do people actually use it), then later that day I snagged it without second thought because the price couldn't be any better, and the seller was really nice too.

Update: I look it up again and this [device.report](https://device.report/linksys/EA7250) shows that there are other models under the same hardware out there

To sumarize, this is the one that I first got the full flash content from using that python script above. We'll set that aside for a letter day.

## Set up a test network

From the boot menu, it's obvious that this device and in fact, almost all of these cheap wifi router support booting from network which will comes in handy when I need to experiment with our own software. The reason we need to get our custom build stuff to run on this is because we always got hit with a login prompt in stock linux after the device fully booted which is as expected and the stock u-boot doesn't support booting anything other than flash and tftp; but come on what else did we expect for this class of devices, it's router bro, normal people don't do weird thing with their router.

Depends on your set up if you want to replicate this, I have the device hooked up with ethernet to same network my PC is on, so we don't have to worry about running another dhcp server when we need one. Here is the `dnsmasq` config file I use to run a tftp server from my PC

```conf
port=0
no-dhcp-interface=
no-daemon
enable-tftp
tftp-root=/tftpserver
tftp-no-fail
```

We disable DHCP and DNS with the first 2 lines, the folder `/tftpserver` needs to be created with the files we'll put in there being world-readable.

```bash
chmod o+r -R /tftpserver
```

## Build custom u-boot

Next, We build a custom u-boot image with support for booting from usb devices

First, as a homelaber myself, I got many of the great software mirroring on a local [Gitea](https://about.gitea.com/) server running in Docker just for these occasions.

```bash
git clone https://git.home.suunhuy.com/backuper/u-boot.git
git checkout v2025.04
```

Let's do the build in a already prepared Docker image to save us some time with tooling

```bash
docker run -it --rm -v $PWD:/app --name my-uboot trini/u-boot-gitlab-ci-runner:noble-20250415.1-14May2025 bash
```

Inside the container, we need some cross compiler since my PC is x86

```bash
apt install gcc gcc-arm-linux-gnueabihf -y
export ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf-
```

Now, switch to a user with the same UID as my PC user, usually `uid=1000` to avoid compiling issues

```bash
su ubuntu # switch to user ubuntu (uid=1000)
make mt7629_rfb_defconfig
```

Make some changes in `make menuconfig` and start the compiling with `make -j$(nproc)`, here are mine
- `CONFIG_USB`
- `CONFIG_CMD_BOOTDEV`
- `CONFIG_CMD_BOOTZ`
- `CONFIG_CMD_LSBLK`
- `CONFIG_CMD_MTD`
- `CONFIG_CMD_PART`
- `CONFIG_CMD_PCI`
- `CONFIG_CMD_POWEROFF`
- `CONFIG_CMD_NFS`
- `CONFIG_CMD_DHCP`
- `CONFIG_CMD_DNS`
- `CONFIG_CMD_PXE`
- `CONFIG_CMD_SYSBOOT`
- `CONFIG_CMD_EXT4`
- `CONFIG_CMD_SQUASHFS`

> Some of these may not actually show up since I only used the included `mt7629_rfb_defconfig` for the reference board when compiling. 

Specifically, it is missing the device source tree which is a `.dts` file that tells the kernel what type of hardware located on which memory addresses. However, all we need from this custom build is usb support to use as jumping point to boot into Debian, the default defconfig is just good enough.

But then on second though, the first time i built with mt7629_rfb_defconfig cause nothing to be recognize. For curiosity, I then went and port the dts file for this EA7500v3 over from OpenWRT, here are a few compiling errors I encountered and managed to compile it successfully
- copying `mt7629-linksys-ea7500-v3.dts` and `mt7629.dtsi` over into u-boot at `arch/arm/dts`, run `make` and got 'Label or path not found' for bch, ssusb, pio and u3phy0
- proceeded to `grep` for those this OpenWRT and found patch that define them at `target/linux/mediatek/patches-6.6/130-dts-mt7629-add-snand-support.patch`, I then copied them over into a my own file named `mt7629-mine.dtsi` and included it `mt7629-linksys-ea7500-v3.dts`. Running `make` again gave 'Duplicate label 'u2port0' on /t-phy@1a0c4000/usb-phy@0 and /usb-phy@1a0c4000/usb-phy@0'
- after another `grep` for 'u2port0', it clear that the `mt7629.dtsi` I copied over had already defined it under 'u3phy' but my `mt7629-mine.dtsi` defined it again under 'u3phy0'. I then removed that 'u3phy0' that change all its references in `mt7629-linksys-ea7500-v3.dts` to 'u3phy'

The fixes seemed to have worked, and I use stock u-boot to load the compiled `u-boot.bin` over tftp, and it stopped at `DRAM: initcall failed`
After carefully comparing the new dts vs dts for reference board, it found the culprit to be myself for forgeting to add an include file name `mt7629-rfb-u-boot.dtsi`. Eventually I finally got it working with the new dts file and was able to control the power LED through `led` command in my new u-boot which hadn't been the case before. Still, I couldn't add get nand info through this new u-boot build since adding `CONFIG_CMD_NAND` cause `make` to failed with `board_nand_init` function missing from `board/mediatek/mt7629/mt7629_rfb.c`.

At this point, I just wanted to take a break from compiling u-boot, we don't even need to read from nand from our u-boot anyway.

```bash
fedora › file u-boot*
u-boot:              ELF 32-bit LSB executable, ARM, EABI5 version 1 (SYSV), static-pie linked, with debug_info, not stripped
u-boot.bin:          DOS executable (COM), start instruction 0xb80000ea 14f09fe5
u-boot.bin.lzma:     LZMA compressed data, streamed
u-boot.cfg:          ASCII text
u-boot.dtb:          Device Tree Blob version 17, size=13112, boot CPU=0, string block size=1023, DT structure block size=12028
u-boot-dtb.bin:      DOS executable (COM), start instruction 0xb80000ea 14f09fe5
u-boot-dtb.img:      u-boot legacy uImage, U-Boot 2025.04-dirty for mt7629 \270, Firmware/ARM, Firmware Image (Not compressed), 456132 bytes, Mon Jun 16 19:46:02 2025, Load Address: 0X41E00000, Entry Point: 0X41E00000, Header CRC: 0X261CFC82, Data CRC: 0X85599D65
u-boot.img:          u-boot legacy uImage, U-Boot 2025.04-dirty for mt7629 \270, Firmware/ARM, Firmware Image (Not compressed), 456132 bytes, Mon Jun 16 19:46:02 2025, Load Address: 0X41E00000, Entry Point: 0X41E00000, Header CRC: 0X261CFC82, Data CRC: 0X85599D65
u-boot.lds:          assembler source, ASCII text
u-boot-lzma.img:     u-boot legacy uImage, U-Boot 2025.04-dirty for mt7629 ], Firmware/ARM, Standalone Program (lzma), 215132 bytes, Mon Jun 16 19:46:03 2025, Load Address: 0X41E00000, Entry Point: 0X41E00000, Header CRC: 0XAACDC848, Data CRC: 0X61CE8B3E
u-boot.map:          ASCII text
u-boot-mtk.bin:      data
u-boot-nodtb.bin:    DOS executable (COM), start instruction 0xb80000ea 14f09fe5
u-boot.srec:         Motorola S-Record; binary data in text format
u-boot.sym:          ASCII text
u-boot-with-spl.bin: data
```

## Build custom linux

In the same manner as building u-boot, we speed things up by using a ubuntu docker container to build the kernel from mainlain source

```bash
# pull from source
git clone https://git.home.suunhuy.com/backuper/linux.git
git checkout v6.15
# run ubuntu container
docker run -it --rm -v $PWD:/app --name my-linux ubuntu:noble bash
# inside container
apt update
apt install -y git make gcc g++ device-tree-compiler bc bison flex libssl-dev libncurses-dev python3-ply python3-git libgmp3-dev libmpc-dev
# install cross-compiler
apt install -y gcc gcc-arm-linux-gnueabihf
# switch to ubuntu user (uid=1000)
su ubuntu
git checkout 1_36_stable # 37 failed
export ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf-
make multi_v7_defconfig
make menuconfig # CONFIG_NET_DSA_MT7530
make -j$(nproc)
```

## Create a debian image

## Save debian to a usb stick

## Persist u-boot onto flash
Save u-boot to some spare flash area
Configure stock u-boot to run it by default

## Booting it untethered
Complete debian boot without relying on tftp server

## Do some benchmark
stress test and compare score to RPi4
run some game server since there is no graphic output

## What to do with the flash dump

## What I learnt

