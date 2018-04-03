#! /bin/bash

sleep 10

remote_id1=$(
	xinput list |
	sed -n 's/.*Telink Wireless Receiver.*id=\([0-9]*\).*keyboard.*/\1/p' |
	head -n 1
)
[ "$remote_id1" ] || exit

remote_id2=$(
	xinput list |
	sed -n 's/.*Telink Wireless Receiver.*id=\([0-9]*\).*keyboard.*/\1/p' |
	tail -n 1
)
[ "$remote_id2" ] || exit

echo $remote_id2

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
    include "us(basic)"
    key <AB05>  {  type= "ALPHABETIC", symbols[Group1]= [ h, H ]  };
    key <RGHT> {   [     Right ] };
    key <LEFT> {   [     Left ] };
    key <VOL+> {   [ 1 ] };
    key <VOL-> {   [ 2 ] };
    key <MENU> {   [ 3 ] };
    key <ESC>  {   [ 4 ] };
    key <RTRN> {   [ 5 ] };
    key <I150> {   [ 6 ] };
};
EOF

#    key <FK05>   { [ parenright, 1 ] };
#    key <ESC>   { [ 1, parenright ] };
#rr = $(sed 's/\(xkb_symbols.*\)"/\1+custom(remote)"/' )
 setxkbmap -device $remote_id1 -print | sed 's/\(xkb_symbols.*\)"/\1+custom(remote)"/' > /tmp/xkb_config.txt 
xkbcomp -I/tmp/xkb /tmp/xkb_config.txt -i $remote_id1 -synch $DISPLAY 


setxkbmap -device $remote_id2 -print | sed 's/\(xkb_symbols.*\)"/\1+custom(remote)"/' > /tmp/xkb_config.txt 
xkbcomp -I/tmp/xkb /tmp/xkb_config.txt -i $remote_id2 -synch $DISPLAY 
