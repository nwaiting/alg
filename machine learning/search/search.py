#coding=utf-8

import os

class KeyNode(object):
    def __init__(self, k=None, c=None, p=None, n=None):
        self.key_ = k
        self.count_ = c
        self.pos_ = p #hash表中位置
        self.next_ = n

class DocNode(object):
    def __init__(self,dname=None,c=None,n=None):
        self.doc_name_ = dname
        self.next_ = n
        self.word_freq_ = c

class Search(object):
    def __init__(self,dir_path=None):
        self.dir_path_ = dir_path
        self.all_words_ = set()

        self.cryt_table_size = 0x500 #1280 1024+256
        self.cryt_tables_ = [0 for i in xrange(self.cryt_table_size)]

        #table 数组大小
        self.hash_table_size_ = 10000
        self.hash_table_ = [0 for i in xrange(self.hash_table_size_)]
        self.hash_tablea_ = [0 for i in xrange(self.hash_table_size_)]
        self.hash_tableb_ = [0 for i in xrange(self.hash_table_size_)]
        self.keys_array_ = [0 for i in xrange(self.hash_table_size_)]

    def Init(self):
        filelists = os.listdir(self.dir_path_)
        for f in filelists:
            if f.endswith('.ansjwords'):
                with open(os.path.join(self.dir_path_, f), 'rb') as fd:
                    for line in fd.xreadlines():
                        lineitems = line.split()
                        if len(lineitems) > 1:
                            dnode = DocNode(f,lineitems[1])
                            self.InsertStr(lineitems[0], dnode)

    def PrepareCryptTable(self):
        seed = 0x00100001
        for index1 in xrange(0x100):
            index2 = index1
            for i in xrange(5):
                seed = (seed * 125 + 3) % 0x2AAAAB
                temp1 = (seed & 0xFFFF) << 0x10
                seed = (seed * 125 + 3) % 0x2AAAAB
                temp2 = (seed & 0xFFFF)
                self.cryt_tables_[index2] = (temp1 | temp2)
                index2 += 0x100
        #print self.cryt_tables_

    #暴雪的hash改造算法
    def HashString(self, input_str, hash_type):
        seed1 = 0x7FED7FED
        seed2 = 0xEEEEEEEE
        for i in input_str:
            seed1 = self.cryt_tables_[(hash_type<<8) + ord(i)] ^ (seed1 + seed2)
            seed2 = ord(i) + seed1 + seed2 + (seed2<<5) + 3
        return seed1

    def InternalInsertStr(self, input_str):
        hash_offset = 0
        hash_a = 1
        hash_b = 2
        hash_value = self.HashString(input_str, hash_offset)
        hash_value_a = self.HashString(input_str, hash_a)
        hash_value_b = self.HashString(input_str, hash_b)
        hash_start = hash_value % self.hash_table_size_
        hash_pos = hash_start

        while self.hash_table_[hash_start]:
            hash_start = (hash_start + 1) % self.hash_table_size_
            if hash_start == hash_pos:
                break

        if not self.hash_table_[hash_start]:
            self.hash_tablea_[hash_start] = hash_value_a
            self.hash_tableb_[hash_start] = hash_value_b
            node = KeyNode(k=input_str,c=1,p=hash_start)
            self.keys_array_[hash_start] = node
            return hash_start

        if self.hash_table_[hash_start]:
            print "table is full ", input_str
        else:
            print "error"
        return None

    def SearchStr(self, input_str):
        hash_offset = 0
        hash_a = 1
        hash_b = 2
        hash_value = self.HashString(input_str, hash_offset)
        hash_value_a = self.HashString(input_str, hash_a)
        hash_value_b = self.HashString(input_str, hash_b)
        hash_start = hash_value % self.hash_table_size_
        hash_pos = hash_start

        while self.hash_table_[hash_start]:
            if self.hash_tablea_[hash_start] == hash_value_a and self.hash_tableb_[hash_start] == hash_value_b:
                break
            hash_start = (hash_start + 1) % self.hash_table_size_
            if hash_start == hash_pos:
                break
        if self.keys_array_[hash_start] and self.keys_array_[hash_start].key_:
            return self.keys_array_[hash_start]
        return None

    def InsertStr(self, input_str, doc_node):
        node = self.SearchStr(input_str)
        if node:
            node.count_ += 1
            doc_node.next_ = node.next_
            node.next_ = doc_node
        else:
            p = self.InternalInsertStr(input_str)
            node = self.keys_array_[p]
            node.next_ = doc_node

    def ShowSearchStr(self, input_str):
        node = self.SearchStr(input_str)
        if node and node.next_:
            dnode = node.next_
            while dnode:
                print dnode.doc_name_
                dnode = dnode.next_

if __name__ == '__main__':
    s = Search(os.path.dirname(os.path.abspath(__file__)))
    s.PrepareCryptTable()
    s.Init()
    s.ShowSearchStr("香港回归")