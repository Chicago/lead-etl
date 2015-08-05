#!/usr/bin/python

import sys
import numpy as np

with open(sys.argv[1]) as f:
    content = f.read().replace(',',' ').splitlines()

column_names=['Cur_frst_t','Cur_last_t','Addr_ln1_t','Addr_zi', 'Birth_d', 'Hse_inc_', 'Hseh', 'Pa_c', 'Edc_d', 'Educ', 'Empl', 'Occp']

# Fixes for ErieSuperior
replace_columns = np.array([
    # Infant
    ['ADDR_ZIP_N', 'Addr_zi_t'],
    ['IRTH_D', 'Birth_d'],
    ['HSE_INC_A', 'Hse_inc_'], 
    ['HSEHLD_N', 'Hseh'],
    ['_CDE1_C', 'Pa_c'],
    ['PA_C', 'Pa_c'],
    # Pregnant
    ['EDUCATN_', 'Educ'],
    ['EMPLYMNT', 'Empl'],
    ['OCCPTN_', 'Occp'],
    ['HSEHLD_', 'Hseh'],
    ['ADDR_ZIP', 'Addr_zi_t'],
    ['DC_D', 'Edc_d'],
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

# use uniform names for columns
def fix_header(header):
    for old_column,new_column in replace_columns:
        header = header.replace(old_column,new_column)
    return header.lower()

# erie_p has bad spacing in the public assistance fields so parse them manually
def erie_p_fix(line):
    pa_index = line.rfind(',')+1
    spaces = re.compile("[ ]+")
    new_line,n = spaces.subn(',', line[pa_index:])
    new_line += ','*(4-n)
    return line[:pa_index] + new_line


lines = iter(content)
printed_header = False # has the header been printed yet?
erie_p = False # is this the erie_p file?

for line in lines:
    if line.startswith('Cur_') or line.startswith('CUR_'):
        if line.startswith('CUR_'): # headers in Erie pdf are spilled :(
            next_line = lines.next() # use next line to figure out if this is infant or mother data
            # across three lines in infant data
            if 'BIRTH_D' in next_line:
                line = join_lines((line, next_line, lines.next()[1:]))
            # across two lines and misaligned in mother data
            else:
                line = join_lines((line, next_line))
                line = 'CUR_FRST_T         CUR_LAST_T      ADDR_LN1_T        ADDR_ZIPDC_D' + line[65:]
                line = line.replace('HSE_INC_A', '           HSE_INC_A')
                line = line.replace('PA_CDE1_PA_CDE2_PA_CDE3_PA_CDE4_PA_CDE5_', 'PA_C')
                erie_p = True
        column_positions, column_names = get_column_positions(line)
        if not printed_header:
            header = fix_header(str.join(',',column_names))
            if erie_p:
                header +=',pa_c'*4
            print header
            printed_header = True
    elif line.startswith(' '): # fix multiline names in Englewood pdf :(
        pass # TODO: append to name of previous line
    else:
        csv_line = line_to_csv(line,column_positions)
        if erie_p:
            csv_line = erie_p_fix(csv_line)
        print csv_line
