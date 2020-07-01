#!/usr/bin/env python3


def main():
    # read in a file
    classes = set()
    with open('/Users/markfawcett/OneDrive - UK Parliament/_junk/para_classes.txt') as f:
        lines = f.readlines()


    for line in lines:
        classes.add(line.strip())

    # turn set into list and then sort
    classes_list = list(classes)
    classes_list.sort()

    print('\n'.join(classes_list))



if __name__ == "__main__":
    main()
