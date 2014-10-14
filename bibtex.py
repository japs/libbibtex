#!/usr/bin/python3
# *********************************************************************        
# * Copyright (C) 2014 Jacopo Nespolo <j.nespolo@gmail.com>           *        
# *                                                                   *
# * For the license terms see the file LICENCE, distributed           *
# * along with this software.                                         *
# *********************************************************************
#
# This file is part of Paper
# 
# Paper is free software: you can redistribute it and/or modify it under the 
# terms of the GNU General Public License as published by the Free Software 
# Foundation, either version 3 of the License, or (at your option) any later 
# version.
# 
# Paper is distributed in the hope that it will be useful, but WITHOUT ANY 
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS 
# FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along 
# with Paper.  If not, see <http://www.gnu.org/licenses/>
#

output_tags = ["title", "author", "journal", "volume", "page",
               "year", "month", "publisher", "doi", "url", "archiveprefix"]

months = {"01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", 
          "06": "Jun", "07": "Jul", "08": "Aug", "09": "Sep", "10": "Oct", 
          "11": "Nov", "12": "Dec"}

class Bibtex:
    '''
    A very simple BibTeX class that implements automatic formatting of outoput.
    Notice that no sanity checks are performed.
    '''
    def __init__(self, ref=None, bib=None, ris=None):
        self.fields = {}
        if bib:
            self._init_from_bibtex(bib)
        elif ris:
            self._init_from_ris(ris)

        if ref:
            self.fields["_key"] = ref  # This will become the item's 
                                       # key (@article{ref,...})

    def _init_from_bibtex(self, bib):
        import re
        for line in bib:
            if "@" in line: # key line => extract type, key
                tokens = line.split("{")
                self.fields["_type"] = tokens[0][1:].strip().lower()
                self.fields["_key"]  = tokens[1][:-1].strip(" ,").lower()
            elif "=" not in line: # end of bibtex entry
                continue
            else: # key = value pair
                tokens = line.split("=")
                tag = tokens[0].strip().lower()
                value = tokens[1][:-1].strip(' \"\'{}')
                self.set_tag(tag, value)

    def _init_from_ris(self, ris, key_conversion=None):
        pass


    def add_tag(self, tag):
        if tag in self.fields.keys():
            pass
        elif tag == "author":
            self.fields[tag] = []
        else:
            self.fields[tag] = None

    def set_tag(self, tag, value):
        self.add_tag(tag)
        if tag == "author":
            if type(value) is not list:
                value = value.split("and")
                value = [v.strip() for v in value]
            self.fields[tag] += value
        elif tag == "_date":
            date = value.split("/")
            self.fields["year"] = date[0]
            self.fields["month"] = months[date[1]]
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
        
        for tag in output_tags:
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
    from sys import stdin
    bib = stdin.readlines()
    b = Bibtex(bib=bib)
    print (b)