#!/bin/zsh-beta

arch=linux_x86_64

if [[ $1 != "" ]]; then
   arch=$1
fi

echo blobs/$arch/*
ln -s blobs/$arch/* .
rm *_debug*.so
