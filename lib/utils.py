#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import subprocess
import pyminizip


class Singleton(type):
    _instances = {}

    def __call__(cls, *args):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args)
        return cls._instances[cls]


def program_popen(command):
    proc = subprocess.Popen(
        command,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout_value, stderr_value = proc.communicate('through stdin to stdout')
    if len(stderr_value) > 0:
        raise Exception(stderr_value)
    return proc.wait()


def encrypt(src, dst, passwd, compress_level=6):
    if os.path.exists(dst):
        os.remove(dst)

    # cryption OR use shell p7zip with option -p
    pyminizip.compress(src, dst, str(passwd), int(compress_level))

    # remove src
    os.remove(src)


def split(src, dst, chunk_size):
    program_popen('7z a -v{chunk_size} {dst} {src}'.format(src=src, dst=dst, chunk_size=chunk_size))
