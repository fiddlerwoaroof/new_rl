#!/bin/zsh

arch=linux_x86_64

if [[ $1 != "" ]]; then
   arch=$1
fi

echo blobs/$arch/*.so
ln -s blobs/$arch/*.so .
rm *_debug*.so
ln -s blobs/terminal.png .
