#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys # モジュール属性 argv を取得するため

argvs = sys.argv  # コマンドライン引数を格納したリストの取得
argc = len(argvs) # 引数の個数
# デバッグプリント
print argvs
print argc
print
if (argc != 2):   # 引数が足りない場合は、その旨を表示
    print 'Usage: # python %s filename' % argvs[0]
    quit()         # プログラムの終了

print 'The content of %s ...n' % argvs[1]
f = open(argvs[1])
line = f.readline() # 1行読み込む(改行文字も含まれる)
while line:
    print line
    line = f.readline()
f.close
