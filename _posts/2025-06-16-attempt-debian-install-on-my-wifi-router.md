---
layout: post
title: Attempt Debian install on my WiFi router
excerpt: Linksys EA7250 doesn't have a wireless driver to run OpenWRT, but it's got a whopping 2 cores of ARMv7 CPU which are better then those MIPS processors commonly found in these cheap routers out there. Let's not get this goes to waste and make a custom Debian build for it to see how it's stack up against a Raspberry Pi 4 I have laying around.
---

Last year, as I was on the hunt for some cheap routers with interesting features as a hobby (yes I'm kind of a router enjoyer myself, but people collect weird things all the time, aren't they), I stumbled upon this rare species, the [Linksys EA7500v3]() (specs below) which unlike many other Linksys models has ARM CPU. I specifically only look for those with mediatek chips because these have great support in Linux. Later on, I discovered that those wireless chips in this particular CPU have yet to get any open source driver support in OpenWRT, also the second ARM doesn't work in OpenWRT. In the end, I bought it anyway because without wireless, this could still be a good host for experimenting with custom linux build and a greate oppotunity for me to learn some kernel driver development.

Specs:
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

## I did messed it up

## Recover

## Set up a test network
Configure tftp server with dnsmasq
Set up build environment for later

## Build custom u-boot
To enable usb booting

## Build custom linux
Compile and try booting it up

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

