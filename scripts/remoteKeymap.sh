#! /bin/bash

# sleep 20

remote_id=$(
	xinput list |
	sed -n 's/.*HID.*id=\([0-9]*\).*keyboard.*/\1/p'
)
[ "$remote_id" ] || exit

echo $remote_id

# Source for keymapping: https://gist.github.com/zoqaeski/3880640
# Source for instructions: https://superuser.com/questions/760602/how-to-remap-keys-under-linux-for-a-specific-keyboard-only
# Use xev to get key numbers for the device

# remap the following keys for a KAKY remote pointer
#
# page_up -> left  (PGUP to LEFT)
# page_down -> right  (PGDN to RIGHT )
# escape -> 0  ( ESC to AE10)
# Shift-F5 -> 0 (FK05 + shift to AE10 reversed)
# B -> H  (AB05 to AC06)

mkdir -p /tmp/xkb/symbols

mkdir -p /tmp/xkb/symbols
cat >/tmp/xkb/symbols/custom <<\EOF
xkb_symbols "remote" {
    key <AB05>  {  type= "ALPHABETIC", symbols[Group1]= [ h, H ]  };
    key <PGDN> {   [     Right ] };
    key <PGUP> {   [     Left ] };
    key <FK05>   { [ parenright, 1 ] };
    key <ESC>   { [ 1, parenright ] };
};
EOF

#rr = $(sed 's/\(xkb_symbols.*\)"/\1+custom(remote)"/' )
setxkbmap -device $remote_id -print | sed 's/\(xkb_symbols.*\)"/\1+custom(remote)"/' | xkbcomp -I/tmp/xkb -i $remote_id -synch - $DISPLAY 

