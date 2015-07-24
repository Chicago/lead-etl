#!/usr/bin/python

import sys

with open(sys.argv[1]) as f:
    content = f.read().replace(',',' ').splitlines()

column_names=['Cur_frst_t','Cur_last_t','Addr_ln1_t','Addr_zi', 'Birth_d', 'Hse_inc_', 'Hseh', 'Pa_c']
column_names += ['ADDR_ZIP_N', 'IRTH_D', 'HSE_INC_A', 'HSEHLD_N', '_CDE1_C'] #+ ['PA_CDE{}_C'.format(i) for i in range(1,6)]
import re
boundaries = re.compile('(' + str.join('|', column_names) + ')', re.IGNORECASE)
def get_column_positions(header):
    return zip(*map(lambda m: (m.start(), m.group()), boundaries.finditer(header)))

last_non_space = re.compile("[^ ][ ]*$")
first_non_space = re.compile("[^ ]")
def line_to_csv(line, column_positions):
    for position in reversed(column_positions[1:]):
        if position < len(line):
            # find the last non-space character position
            space_end = position+first_non_space.search(line[position:]).start()
            line = line[:position] +','+ line[space_end:]
        else:
            line += ','
    return line

def join_lines(lines):
    offsets = [0] + map(len, lines)[:-1]
    offset_lines = [line[offset:] for line,offset in zip(lines, offsets)]
    return ''.join(offset_lines)

lines = iter(content)
printed_header = False # has the header been printed yet?

for line in lines:
    if line.startswith('Cur_') or line.startswith('CUR_'):
        if line.startswith('CUR_'): # headers in Erie pdf are spilled across three lines :(
            line = join_lines((line, lines.next(), lines.next()[1:]))
        column_positions, column_names = get_column_positions(line)
        if not printed_header:
            print str.join(',',column_names)
            printed_header = True
    elif line.startswith(' '): # fix multiline names in Englewood pdf :(
        pass # TODO: append to name of previous line
    else:
        print line_to_csv(line,column_positions)
