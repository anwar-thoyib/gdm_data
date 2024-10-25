#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import re
from datetime import datetime

##############################################################################
class Batch:
### CONFIG ###
  MAX_LINE      = 100
  TRAILING_ZERO = 3
  
#----------------------------------------------------------------------------
  def __init__(self, name):
    today               = datetime.today()
    today_str           = today.strftime("%Y%m%d_%H%M")
    self.base_filename  = today_str +'_'+ name
    self.batch_list     = []
    self.fout           = object()
    self.index          = 0
    self.counter        = 0
    self.batch_filename = ''

#----------------------------------------------------------------------------
  def _begin_batch(self):
    self.fout = open(self.batch_filename, 'w')
    self.fout.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    self.fout.write('<!DOCTYPE batchscript SYSTEM "batch.dtd">\n')
    self.fout.write('<batchscript name="'+ self.batch_filename +'" lStopConsecErrors="10000000" lStopTotalErrors="100000000"><command><operation name="inadvantage/TmafBatch.CAO_LDM_00"/><inputdata><format type="bin"/><data><inline><![CDATA[\n')

#----------------------------------------------------------------------------
  def begin_batch(self):
    if self.counter == 0:
      trailing = self.TRAILING_ZERO - len(str(self.index))
      self.batch_filename = self.base_filename +'_'+ trailing*'0' + str(self.index) +'.xml'
      self.batch_list.append(self.batch_filename)
      self._begin_batch()

#----------------------------------------------------------------------------
  def _content_batch(self, content):
    self.fout.write('@TRANSACTION\n')
    self.fout.write(content)
    self.fout.write('@END_TRANSACTION\n')

#----------------------------------------------------------------------------
  def _end_batch(self):
    self.fout.write(')]]></inline></data></inputdata><outputdata><format type="bin"/><file url="'+ self.batch_filename +'.out"/></outputdata></command></batchscript>\n')
    self.fout.close()

#----------------------------------------------------------------------------
  def end_batch(self):
    self.counter += 1
    if self.counter >= self.MAX_LINE:
      self._end_batch()
      self.counter = 0
      self.index  += 1

#----------------------------------------------------------------------------
  def report(self):
    print('Batch filename: ' )
    for filename in self.batch_list:
      print('  '+ filename)



##############################################################################
class GmfRPP(Batch):
  
#----------------------------------------------------------------------------
  def __init__(self, name='GmfRpp'):
    Batch.__init__(self, name)

#----------------------------------------------------------------------------
  def content_batch(self, Level, CustomerId, Key):
    content = 'GMF::EntireDelete:'+ Level +'(CustomerId="' +CustomerId +'",OfferProfileKey=1,Key='+ Key +',@NoTouchCheck=TRUE,@NoBucketRollover=TRUE);\n'
    self._content_batch(content)

#----------------------------------------------------------------------------
  def collect(self, line):
    rline = re.search(r'^\w+(\.\w+)+;Read:(\w+) \(CustomerId="(\d+)", Key=(\d+), ', line)
    if rline:
      Level      = rline.group(2) 
      CustomerId = rline.group(3)
      Key        = rline.group(4)
      
      return Level, CustomerId, Key
    
    return '', '', ''
    
#----------------------------------------------------------------------------
  def create(self, source_filename):
    fin = open(source_filename)
    for line in fin.readlines():
      
      Level, CustomerId, Key = self.collect(line)      # Custom Regex
      
      if Level:
        self.begin_batch()
        self.content_batch(Level, CustomerId, Key)     # Custom Batch
        self.end_batch()
    
    fin.close()
    
    if self.counter > 0:
      self._end_batch()
          

###########################################################################
if __name__ == "__main__":

  source_filename = ''
  if len(sys.argv) > 1:
    source_filename = sys.argv[1]  
  else:
    print("ERROR: need input filename!")
    exit(0)
    
  myBatch = GmfRPP()
  myBatch.create(source_filename)
  myBatch.report()
