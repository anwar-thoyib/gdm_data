#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import re

param_list = []
option = ''
if len(sys.argv) > 1:
  max_num = len(sys.argv)
  for i in range(1, max_num):
    param = sys.argv[i]
    param_list.append(param)
  
fout = open('params_else.txt', 'w')
for line in sys.stdin.readlines():
  rline = re.search(r'^\w+(\.\w+)*;\w+:\w+ \((.+)\);$', line)
  if rline:
    output_list = []
    elements = rline.group(2).split(',')
    for element in elements:
      sline = re.search(r'^\s*((\w+)=[^\=]+$)', element)
      if sline:
        telement = sline.group(1)
        tparam = sline.group(2)
        for param in param_list:
          if param == tparam:
            output_list.append(telement)
    
    output_line = ''
    if len(output_list) == len(param_list):
      for index, output in enumerate(output_list):
        if index:
          output_line += ', '
  
        output_line += output
        
      print(output_line)
    else:
      fout.write(line)

fout.close()