#!/usr/bin/python3
# *********************************************************************        
# * Copyright (C) 2014 Jacopo Nespolo <j.nespolo@gmail.com>           *        
# *                                                                   *
# * For the license terms see the file LICENCE, distributed           *
# * along with this software.                                         *
# *********************************************************************
#
# This file is part of libbibtex
# 
# libbibtexis free software: you can redistribute it and/or modify it under the 
# terms of the GNU General Public License as published by the Free Software 
# Foundation, either version 3 of the License, or (at your option) any later 
# version.
# 
# libbibtex is distributed in the hope that it will be useful, but WITHOUT ANY 
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS 
# FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along 
# with Paper.  If not, see <http://www.gnu.org/licenses/>
#

_output_tags = ["title", "author", "journal", "volume", "page",
                "year", "month", "publisher", "doi", "url", "archiveprefix"]

_months = {"01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", 
           "06": "Jun", "07": "Jul", "08": "Aug", "09": "Sep", "10": "Oct", 
           "11": "Nov", "12": "Dec"}

"""
This map is taken from a sample from Nature. IT IS NON-STANDARD.
"""
_ris_fields = {"TY": "_type", "TI": "title", "JA": "journal",
               "VL": "volume", "IS": "issue", "SP": "page", "EP": "_end_page",
               "L3": "doi", "UR": "url"}

_ris_types = {"JOUR": "article"}


def multiple_bibtex_entries(inobj):
    '''
    Takes a file or string or list of lines and extracts bibtex entries,
    returning them as a list of Bibtex objects.
    '''
    from io import IOBase
    if isinstance(inobj, str):
        textin = inobj.splitlines()
    elif isinstance(inobj, IOBase):
        textin = inobj.readlines()
    elif isinstance(inobj, list):
        textin = inobj
    else:
        raise ValueError("inobj must be str, FileObj or list of strings.")

    N = len(textin)
    start = 0
    bibtexs = []
    while start < N:
        try:
            b, lines_consumed = Bibtex.from_bibtex(textin[start:])
        except ValueError:
            break
        start += lines_consumed
        bibtexs.append(b)
    return bibtexs


class Bibtex:
    '''
    A very simple BibTeX class that implements automatic formatting of outoput.
    Notice that no sanity checks are performed.
    '''
    def __init__(self, ref=None, bib=None, ris=None, **kwargs):
        self.fields = {}
        if bib:
            self._init_from_bibtex(bib)
        elif ris:
            self._init_from_ris(ris, kwargs)

        if ref:
            self.fields["_key"] = ref  # This will become the item's 
                                       # key (@article{ref,...})
  
    def _init_from_bibtex(self, bib):
        '''
        Parses a single extisting bibtex entry, returning the number of lines
        consumed.
        '''
        for linenumber, line in enumerate(bib):
            if "@" in line: # key line => extract type, key
                tokens = line.split("{")
                self.fields["_type"] = tokens[0].strip("@\n \t").lower()
                self.fields["_key"]  = tokens[1].strip(" ,\n")
            elif line.strip() == "}": # end of bibtex entry
                return linenumber + 1
            elif "=" not in line:
                continue
            else: # key = value pair
                tokens = line.split("=")
                tag = tokens[0].strip().lower()
                value = tokens[1].strip(', \"\'{}\n')
                self.set_tag(tag, value)
        return linenumber + 1
 
    @staticmethod
    def from_bibtex(bib):
        '''
        Static method to create a Bibtex object from a string.
        It returnes the Bibtex object and the number of lines consumed.
        '''
        out = Bibtex()
        lines = out._init_from_bibtex(bib)
        if out.fields == {}:
            raise ValueError("Empty bibtex entry.")
        return out, lines

    def _init_from_ris(self, ris, **kwargs):
        '''
        Init from ris string.
        '''
        pass


    def add_tag(self, tag):
        '''
        Add an empty tag to the Bibtex object. 
        Mostly used privately, but exposed anyways.
        '''
        if tag in self.fields.keys():
            pass
        elif tag == "author":
            self.fields[tag] = []
        else:
            self.fields[tag] = None

    def set_tag(self, tag, value):
        '''
        Set tag by tag,value pairs.
        '''
        self.add_tag(tag)
        if tag == "author":
            if type(value) is not list:
                value = value.split("and")
                value = [v.strip() for v in value]
            self.fields[tag] += value
        elif tag == "_date":
            date = value.split("/")
            self.fields["year"] = date[0]
            self.fields["month"] = _months[date[1]]
        else:
            self.fields[tag] = value
    
    def format(self, tag):
        '''
        Single field formatting.
        '''
        if tag == "author":
            return "%s = {%s}" %(tag, " and ".join(self.fields[tag]))
        else:
            return "%s = {%s}" %(tag, self.fields[tag])

    def __str__(self):
        '''
        Full formatting of the bibtex code.
        '''
        out = ["@" + self.fields["_type"] + "{" + self.fields["_key"]]
        
        for tag in _output_tags:
            try:
                out.append(self.format(tag))
            except KeyError:
                pass
        if "url" not in self.fields.keys():
            try:
                out.append(self.format("eprint"))
            except KeyError:
                pass
        out = ",\n  ".join(out)
        out += "\n}\n"
        return out

    def __repr__(self):
        return repr(self.fields)

    def as_bibitem(self):
        out = "\\bibitem{%s}\n" %self.ref
        out += ", ".join(self.fields[author]) + ",\n"
        out += self["journal"]
        out += "{\\bf %s} %s (%s).\n" %(self.fields[volume], 
                                        self.fields[page], 
                                        self.fields[year])
        return out

if __name__ == "__main__":
    '''
    Test program: pipe a bibtex into it.
    '''
    from sys import stdin
    bib = stdin.readlines()
    b = Bibtex(bib=bib)
    print (b)
    print(Bibtex.from_bibtex(bib))
    print ("MULTIPLE READS")
    bb = multiple_bibtex_entries(bib)
    for b in bb:
        print (b)
