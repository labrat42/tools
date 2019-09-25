# has to be executed from command line, run "change_base -h" for help with inputs

import argparse
import string


def change_base(integer, base, result='', neg_flag=0):
    if base < 1 or base > 36:   # check for valid base
        raise ValueError('base b has to be 0 < b < 37')
    if integer < 0 and neg_flag == 0:   # check for negative value
        integer = abs(integer)  # make absolute value, otherwise it will mess up the index for the list of numeric characters
        neg_flag = 1
    hex_list = [str(i) for i in range(0, 10)]+list(string.ascii_uppercase)  # list of numeric characters, 0-9 + a-z, makes for a maximum of base36
    result += hex_list[integer % base]
    modulo = int(integer/base)
    print(modulo, result)
    if modulo != 0:
        return change_base(modulo, base, result, neg_flag)   # continue to next step with modulo,base and  result is transmitted
    else:   # the algorithm is at the end when modulo = 0
        if base == 2:   # some cases of special annotation
            return '-0b%s' % (result[::-1]) if neg_flag else '0b%s' % (result[::-1])  # result has to be reversed with [::-1]
        elif base == 16:
            return '-0x%s' % (result[::-1]) if neg_flag else '0x%s' % (result[::-1])
        else:
            return 'base%s: -%s' % (base, result[::-1]) if neg_flag else 'base%s: %s' % (base, result[::-1])


def init_parser():
    description = 'converts integers to hex'

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-i', '--int', help="integer you want to convert", required=True, type=int)
    parser.add_argument('-b', '--base', help="base you want to convert to (max 36)", required=True, type=int)

    return parser.parse_args()


if __name__ == '__main__':
    parse = init_parser()
    print(change_base(parse.int, parse.base))
