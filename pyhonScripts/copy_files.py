#!/usr/bin/env python3
import glob

def main():
    # i gress find a bunch of files that follow a pattern
    print(glob.glob('./200*e01.html'))


if __name__ == '__main__':
    main()
