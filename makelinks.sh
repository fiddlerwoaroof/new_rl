#!/bin/zsh

arch=linux_x86_64

if [[ $1 != "" ]]; then
   arch=$1
fi

echo blobs/$arch/libtcod*
ln -s blobs/$arch/libtcod* .
rm *_debug*.{so,dylib}
ln -s blobs/terminal.png .
