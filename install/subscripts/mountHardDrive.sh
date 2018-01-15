#! /bin/bash

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# The first input should be the path to a file (in the /media directory, i.e. on a USB disk) on the disk you want to mount.
FILE=$(python $THIS_DIR/mountHDD.py)

# Test that a real file was given. 
echo $FILE
if test -f $FILE
then
	echo "$FILE is a file"
elif test -d $FILE
then
	echo "$FILE is a folder"
else
	echo "$FILE is not a valid structure."
	exit
fi

read -p "Are you sure that your picture drive contains the file/folder $FILE? (y/n) : " -n 1 -r

if [[ ! $REPLY =~ ^[Yy]$ ]]
then
	exit
fi

# Using df, get the mount point (i.e. /dev/sda1)
DEVICE_MOUNT_POINT=$(df $FILE | awk '{print $1}' | tail -n 1)

# Usring sed/perl and regular expressions, get the UUID, PARTUUI, and filesystem type from the blkid for the device mount point.
PARTUUID=$(blkid $DEVICE_MOUNT_POINT | sed -n -e 's/^.*PARTUUID="\(.*\)".*$/\1/p')
UUID=$(blkid $DEVICE_MOUNT_POINT | perl -ne '/.*?UUID="(.*?)".*/ and print $1')
FILESYS_TYPE=$(blkid $DEVICE_MOUNT_POINT | perl -ne '/.*?TYPE="(.*?)".*/ and print $1')

echo $FILESYS_TYPE
echo $UUID
echo $PARTUUID

MOUNTPOINT='/mnt/photo_drive'
mkdir -p $MOUNTPOINT

if [[ $FILESYS_TYPE == 'ntfs' ]]; then
    # Need ntfs-3g to mount ntfs
    FILESYS_TYPE='ntfs-3g'
fi

# Create the FSTAB line appropriate to auto-mount the filesystem on boot.
FSTAB_LINE="UUID=$UUID $MOUNTPOINT $FILESYS_TYPE defaults,uid=0,gid=0,noatime,umask=000,locale=en_US.UTF-8,permissions 0 0"
# Append this line to /etc/fstab
echo $FSTAB_LINE
echo $FSTAB_LINE | tee -a /etc/fstab

# Mount the file.
umount -a
mount -a

