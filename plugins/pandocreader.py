# -*- coding: utf-8 -*-
# vim:shiftwidth=4 expandtab

from pelican import signals
from pelican.readers import BaseReader

import re
import yaml
from subprocess import Popen, PIPE
from pelican.utils import pelican_open

# modified code of https://github.com/ntessore/pelican-pandoc-reader/
class PandocReader(BaseReader):
    enabled = True

    file_extensions = ['md', 'markdown']
    
    def __init__(self, *args, **kwargs):
        super(PandocReader, self).__init__(*args, **kwargs)
        self.pandoc = ['pandoc', '--to=html5']
        if self.settings['PANDOC_ARGS']:
            self.pandoc.extend(self.settings['PANDOC_ARGS'])


    def _pandoc_parse(self, pandoc, document):
        proc = Popen(pandoc, stdin=PIPE, stdout=PIPE)
        output = proc.communicate(document.encode('utf-8'))[0]
        return output.decode('utf-8')

    def read(self, filename):
        content = ''
        metadata = {}
        with pelican_open(filename) as text:
            frontmatter = {}
            # regex from jekyll
            m = re.match(r'\A(---\s*\n.*?\n?)^(---\s*$\n?)', text, re.U | re.M | re.S)
            if m:
                frontmatter = yaml.load(m.group(1), Loader=yaml.BaseLoader)
            # make sure frontmatter was read as a dict
            if not isinstance(frontmatter, dict):
                frontmatter = {}
            # process frontmatter into metadata
            for name, value in frontmatter.items():
                name = name.lower()
                metadata[name] = self.process_metadata(name, value)
            # pandoc is aware of yaml frontmatter since 12.0, so we pass whole document 
            content = self._pandoc_parse(self.pandoc, text)
            #print('*' * 10)
            #print(self.pandoc)
            #print('*' * 10)
            #print(content)
        return content, metadata

def add_reader(readers):
    readers.reader_classes['md'] = PandocReader

def register():
    signals.readers_init.connect(add_reader)
