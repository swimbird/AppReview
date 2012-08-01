#!/usr/bin/python
# -*- coding: utf-8 -*-

class SuperClass(object):    #classの宣言
    name = ''         #public変数
    __callcount = 0 #private変数

    def __init__( self ): #コンストラクタ
        self.name = 'SuperClass'

    def call( self ): #メソッドのself記述の省略はできません。ちょっと面倒です。
        self.__callcount = self.__callcount + 1
        return self.name

    def getCallCount( self ):
        return self.__callcount

    def setName( self, name ):  #第一引数はself,第二引数から通常引数
        self.name = name

    def resetName( self ):
        self.name = ''

    def __privateMethod( self ): #privateメソッド
        print 'This is Private Method'

    def internalMethod( self ):
        self.__privateMethod()

    def __del__( self ):  #親クラスのデストラクタ
        del self;

#以下クライアント
if __name__ == '__main__' :
    sc = SuperClass()
    print sc.call()
    sc.resetName()
    print sc.name
    sc.setName( 'hoge' )
    print sc.name
    print sc._SuperClass__callcount  #private的なクラス変数を呼び出し可能。
    print sc.getCallCount()
    print sc.internalMethod() # publicメソッド → private的なメソッドの呼び出し
    print sc._SuperClass__privateMethod() #private的なメソッドの直接呼び出し
