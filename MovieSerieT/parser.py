#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Usage:

    >>> from parser import Parser
    >>> Renamer().rename(file)
"""

import os
import json
import re


class Parser:
    def __init__(self):
        self.types = None
        self.group = None
        self.result = None
        self.title = None
        self.excess_dico = None
        self.list_excess = ['sites', 'codec', 'resolution', 'audio', 'sub', 'group', 'excess']

        with open('info.json') as data_file:
            self.database = json.load(data_file)

    def _delchars(self, filename):
        # delete chars
        clean_site = re.sub('{}'.format(self.database['sites']), ' ', filename)
        return re.sub(r'[^a-zA-Z0-9]+', ' ', clean_site).strip()

    def _delete_element(self, filename, args, types):
        # delete element of value dict
        if types == 'serie' or types == 'movie':
            for key, value in enumerate(args):
                filename = filename.replace(args[value], '')

        elif types == 'excess':
            filename = filename.replace(args,'')
        return filename

    def _partition(self, dicto):
        # Create a new dicto with useless info
        self.excess_dico = {}
        for elements in self.list_excess:
            try:
                self.excess_dico[elements] = dicto[elements]
                del dicto[elements]
            except KeyError:
                    pass
        return self.excess_dico

    def parse(self, filename):
        self.result = {}
        excess_raw = []
        files = self._delchars(filename)

        # construct dict
        for key, value in enumerate(self.database):
            match = re.findall(self.database[value], filename)
            try:
                if value == 'episode' or value == 'season':
                    self.result[value] = str(match[0])
                    self.types = True
                elif value == 'group':
                    self.group = True
                else:
                    self.result[value] = match[0]
            except IndexError:
                pass

        # movie or serie
        if self.types == True:
            self.result['type'] = 'serie'
        else:
            self.result['type'] = 'movie'

        # first delete elements
        files = self._delete_element(files, self.result, self.result['type']).strip()

        # Start Process for group
        if self.group == True:
            match_group = re.findall(self.database['group'], str(files))
            self.result['group'] = match_group[0]
            files = self._delete_element(files, self.result, self.result['type']).strip()

        # Start Process for excess elements
        while re.search(r'([\s]{2,})', str(files)) != None:
            excess = re.search(r'([\s]{2,}.+)', str(files)).group().strip()
            excess_raw.append(excess)
            if len(excess_raw) == 1:
                self.result['excess'] = excess_raw[0]
            else:
                self.result['excess'] = excess_raw
            files = self._delete_element(files, excess, 'excess').strip()

        #Finish Process with result(title)
        self.result['title']= files.strip()

        self.excess_dicto = self._partition(self.result)

        return self.result, self.excess_dicto


if __name__ == '__main__':
    path = os.listdir('/Users/Jonh/Movies/Traitement')
    for files in path:
        if files.endswith('.DS_Store'):
            pass
        else:
            Parser().parse(files)
