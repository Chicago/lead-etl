#!/usr/bin/python

import sys
import numpy as np

with open(sys.argv[1]) as f:
    content = f.read().replace(',',' ').splitlines()

column_names=['Cur_frst_t','Cur_last_t','Addr_ln1_t','Addr_zi', 'Birth_d', 'Hse_inc_', 'Hseh', 'Pa_c']

replace_columns = np.array([
    ['ADDR_ZIP_N', 'Addr_zi_t'],
    ['IRTH_D', 'Birth_d'],
    ['HSE_INC_A', 'Hse_inc_'], 
    ['HSEHLD_N', 'Hseh'],
    ['_CDE1_C', 'Pa_c'],
    ['PA_C', 'Pa_c']
])

column_names += replace_columns[:,0]

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

# use uniform names for columns and enumerate Pa_c1,...Pa_c5
def fix_header(header):
    for old_column,new_column in replace_columns:
        header = header.replace(old_column,new_column)
    return header.lower()


lines = iter(content)
printed_header = False # has the header been printed yet?

for line in lines:
    if line.startswith('Cur_') or line.startswith('CUR_'):
        if line.startswith('CUR_'): # headers in Erie pdf are spilled across three lines :(
            line = join_lines((line, lines.next(), lines.next()[1:]))
        column_positions, column_names = get_column_positions(line)
        if not printed_header:
            print fix_header(str.join(',',column_names))
            printed_header = True
    elif line.startswith(' '): # fix multiline names in Englewood pdf :(
        pass # TODO: append to name of previous line
    else:
        print line_to_csv(line,column_positions)
