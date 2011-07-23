#! /usr/bin/env python
# -*- coding: utf-8 -*-

#   eLyXer -- convert LyX source files to HTML output.
#
#   Copyright (C) 2009 Alex Fernández
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

# --end--
# Alex 20090308
# eLyXer main script
# http://www.nongnu.org/elyxer/


import sys




import os.path



import sys
import codecs



import sys

class Trace(object):
  "A tracing class"

  debugmode = False
  quietmode = False
  showlinesmode = False

  prefix = None

  def debug(cls, message):
    "Show a debug message"
    if not Trace.debugmode or Trace.quietmode:
      return
    Trace.show(message, sys.stdout)

  def message(cls, message):
    "Show a trace message"
    if Trace.quietmode:
      return
    if Trace.prefix and Trace.showlinesmode:
      message = Trace.prefix + message
    Trace.show(message, sys.stdout)

  def error(cls, message):
    "Show an error message"
    message = '* ' + message
    if Trace.prefix and Trace.showlinesmode:
      message = Trace.prefix + message
    Trace.show(message, sys.stderr)

  def fatal(cls, message):
    "Show an error message and terminate"
    Trace.error('FATAL: ' + message)
    exit(-1)

  def show(cls, message, channel):
    "Show a message out of a channel"
    message = message.encode('utf-8')
    channel.write(message + '\n')

  debug = classmethod(debug)
  message = classmethod(message)
  error = classmethod(error)
  fatal = classmethod(fatal)
  show = classmethod(show)



class LineReader(object):
  "Reads a file line by line"

  def __init__(self, filename):
    if isinstance(filename, file):
      self.file = filename
    else:
      self.file = codecs.open(filename, 'rU', 'utf-8')
    self.linenumber = 1
    self.lastline = None
    self.current = None
    self.mustread = True
    self.depleted = False
    try:
      self.readline()
    except UnicodeDecodeError:
      # try compressed file
      import gzip
      self.file = gzip.open(filename, 'rb')
      self.readline()

  def setstart(self, firstline):
    "Set the first line to read."
    for i in range(firstline):
      self.file.readline()
    self.linenumber = firstline

  def setend(self, lastline):
    "Set the last line to read."
    self.lastline = lastline

  def currentline(self):
    "Get the current line"
    if self.mustread:
      self.readline()
    return self.current

  def nextline(self):
    "Go to next line"
    if self.depleted:
      Trace.fatal('Read beyond file end')
    self.mustread = True

  def readline(self):
    "Read a line from file"
    self.current = self.file.readline()
    if not isinstance(self.file, codecs.StreamReaderWriter):
      self.current = self.current.decode('utf-8')
    if len(self.current) == 0:
      self.depleted = True
    self.current = self.current.rstrip('\n\r')
    self.linenumber += 1
    self.mustread = False
    Trace.prefix = 'Line ' + unicode(self.linenumber) + ': '
    if self.linenumber % 1000 == 0:
      Trace.message('Parsing')

  def finished(self):
    "Find out if the file is finished"
    if self.lastline and self.linenumber == self.lastline:
      return True
    if self.mustread:
      self.readline()
    return self.depleted

  def close(self):
    self.file.close()

class LineWriter(object):
  "Writes a file as a series of lists"

  def __init__(self, filename):
    if isinstance(filename, file):
      self.file = filename
      self.filename = None
    else:
      self.file = codecs.open(filename, 'w', "utf-8")
      self.filename = filename

  def write(self, strings):
    "Write a list of strings"
    for string in strings:
      if not isinstance(string, basestring):
        Trace.error('Not a string: ' + unicode(string) + ' in ' + unicode(strings))
        return
      self.writestring(string)

  def writestring(self, string):
    "Write a string"
    if self.file == sys.stdout:
      string = string.encode('utf-8')
    self.file.write(string)

  def writeline(self, line):
    "Write a line to file"
    self.writestring(line + '\n')

  def close(self):
    self.file.close()




import os.path
import sys


class BibStylesConfig(object):
  "Configuration class from config file"

  abbrvnat = {
      
      u'@article':u'$authors. $title. <i>$journal</i>,{ {$volume:}$pages,} $month $year.{ doi: $doi.}{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'cite':u'$surname($year)', 
      u'default':u'$authors. <i>$title</i>. $publisher, $year.{ URL <a href="$url">$url</a>.}{ $note.}', 
      }

  alpha = {
      
      u'@article':u'$authors. $title.{ <i>$journal</i>{, {$volume}{($number)}}{: $pages}{, $year}.}{ <a href="$url">$url</a>.}{ <a href="$filename">$filename</a>.}{ $note.}', 
      u'cite':u'$Sur$YY', 
      u'default':u'$authors. $title.{ <i>$journal</i>,} $year.{ <a href="$url">$url</a>.}{ <a href="$filename">$filename</a>.}{ $note.}', 
      }

  authordate2 = {
      
      u'@article':u'$authors. $year. $title. <i>$journal</i>, <b>$volume</b>($number), $pages.{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'@book':u'$authors. $year. <i>$title</i>. $publisher.{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'cite':u'$surname, $year', 
      u'default':u'$authors. $year. <i>$title</i>. $publisher.{ URL <a href="$url">$url</a>.}{ $note.}', 
      }

  default = {
      
      u'@article':u'$authors: “$title”, <i>$journal</i>,{ pp. $pages,} $year.{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'@book':u'{$authors: }<i>$title</i>{ ($editor, ed.)}.{{ $publisher,} $year.}{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'@booklet':u'$authors: <i>$title</i>.{{ $publisher,} $year.}{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'@conference':u'$authors: “$title”, <i>$journal</i>,{ pp. $pages,} $year.{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'@inbook':u'$authors: <i>$title</i>.{{ $publisher,} $year.}{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'@incollection':u'$authors: <i>$title</i>{ in <i>$booktitle</i>{ ($editor, ed.)}}.{{ $publisher,} $year.}{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'@inproceedings':u'$authors: “$title”, <i>$journal</i>,{ pp. $pages,} $year.{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'@manual':u'$authors: <i>$title</i>.{{ $publisher,} $year.}{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'@mastersthesis':u'$authors: <i>$title</i>.{{ $publisher,} $year.}{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'@misc':u'$authors: <i>$title</i>.{{ $publisher,}{ $howpublished,} $year.}{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'@phdthesis':u'$authors: <i>$title</i>.{{ $publisher,} $year.}{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'@proceedings':u'$authors: “$title”, <i>$journal</i>,{ pp. $pages,} $year.{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'@techreport':u'$authors: <i>$title</i>, $year.{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'@unpublished':u'$authors: “$title”, <i>$journal</i>, $year.{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'cite':u'$index', 
      u'default':u'$authors: <i>$title</i>.{{ $publisher,} $year.}{ URL <a href="$url">$url</a>.}{ $note.}', 
      }

  defaulttags = {
      u'YY':u'??', u'authors':u'', u'surname':u'', 
      }

  ieeetr = {
      
      u'@article':u'$authors, “$title”, <i>$journal</i>, vol. $volume, no. $number, pp. $pages, $year.{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'@book':u'$authors, <i>$title</i>. $publisher, $year.{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'cite':u'$index', 
      u'default':u'$authors, “$title”. $year.{ URL <a href="$url">$url</a>.}{ $note.}', 
      }

  plain = {
      
      u'@article':u'$authors. $title.{ <i>$journal</i>{, {$volume}{($number)}}{:$pages}{, $year}.}{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'@book':u'$authors. <i>$title</i>. $publisher,{ $month} $year.{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'@incollection':u'$authors. $title.{ In <i>$booktitle</i> {($editor, ed.)}.} $publisher,{ $month} $year.{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'@inproceedings':u'$authors. $title. { <i>$booktitle</i>{, {$volume}{($number)}}{:$pages}{, $year}.}{ URL <a href="$url">$url</a>.}{ $note.}', 
      u'cite':u'$index', 
      u'default':u'{$authors. }$title.{{ $publisher,} $year.}{ URL <a href="$url">$url</a>.}{ $note.}', 
      }

  vancouver = {
      
      u'@article':u'$authors. $title. <i>$journal</i>, $year{;{<b>$volume</b>}{($number)}{:$pages}}.{ URL: <a href="$url">$url</a>.}{ $note.}', 
      u'@book':u'$authors. $title. {$publisher, }$year.{ URL: <a href="$url">$url</a>.}{ $note.}', 
      u'cite':u'$index', 
      u'default':u'$authors. $title; {$publisher, }$year.{ $howpublished.}{ URL: <a href="$url">$url</a>.}{ $note.}', 
      }

class BibTeXConfig(object):
  "Configuration class from config file"

  replaced = {
      u'--':u'—', u'..':u'.', 
      }

class ContainerConfig(object):
  "Configuration class from config file"

  endings = {
      u'Align':u'\\end_layout', u'BarredText':u'\\bar', 
      u'BoldText':u'\\series', u'Cell':u'</cell', 
      u'ChangeDeleted':u'\\change_unchanged', 
      u'ChangeInserted':u'\\change_unchanged', u'ColorText':u'\\color', 
      u'EmphaticText':u'\\emph', u'Hfill':u'\\hfill', u'Inset':u'\\end_inset', 
      u'Layout':u'\\end_layout', u'LyXFooter':u'\\end_document', 
      u'LyXHeader':u'\\end_header', u'Row':u'</row', u'ShapedText':u'\\shape', 
      u'SizeText':u'\\size', u'StrikeOut':u'\\strikeout', 
      u'TextFamily':u'\\family', u'VersalitasText':u'\\noun', 
      }

  extracttext = {
      u'allowed':[u'StringContainer',u'Constant',u'FormulaConstant',], 
      u'cloned':[u'',], 
      u'extracted':[u'PlainLayout',u'TaggedText',u'Align',u'Caption',u'TextFamily',u'EmphaticText',u'VersalitasText',u'BarredText',u'SizeText',u'ColorText',u'LangLine',u'Formula',u'Bracket',u'RawText',u'BibTag',u'FormulaNumber',u'AlphaCommand',u'EmptyCommand',u'OneParamFunction',u'SymbolFunction',u'TextFunction',u'FontFunction',u'CombiningFunction',u'DecoratingFunction',u'FormulaSymbol',u'BracketCommand',], 
      }

  startendings = {
      u'\\begin_deeper':u'\\end_deeper', u'\\begin_inset':u'\\end_inset', 
      u'\\begin_layout':u'\\end_layout', 
      }

  starts = {
      u'':u'StringContainer', u'#LyX':u'BlackBox', u'</lyxtabular':u'BlackBox', 
      u'<cell':u'Cell', u'<column':u'Column', u'<row':u'Row', 
      u'\\align':u'Align', u'\\bar':u'BarredText', 
      u'\\bar default':u'BlackBox', u'\\bar no':u'BlackBox', 
      u'\\begin_body':u'BlackBox', u'\\begin_deeper':u'DeeperList', 
      u'\\begin_document':u'BlackBox', u'\\begin_header':u'LyXHeader', 
      u'\\begin_inset Argument':u'ShortTitle', 
      u'\\begin_inset Box':u'BoxInset', u'\\begin_inset Branch':u'Branch', 
      u'\\begin_inset Caption':u'Caption', 
      u'\\begin_inset CommandInset bibitem':u'BiblioEntry', 
      u'\\begin_inset CommandInset bibtex':u'BibTeX', 
      u'\\begin_inset CommandInset citation':u'BiblioCitation', 
      u'\\begin_inset CommandInset href':u'URL', 
      u'\\begin_inset CommandInset include':u'IncludeInset', 
      u'\\begin_inset CommandInset index_print':u'PrintIndex', 
      u'\\begin_inset CommandInset label':u'Label', 
      u'\\begin_inset CommandInset line':u'LineInset', 
      u'\\begin_inset CommandInset nomencl_print':u'PrintNomenclature', 
      u'\\begin_inset CommandInset nomenclature':u'NomenclatureEntry', 
      u'\\begin_inset CommandInset ref':u'Reference', 
      u'\\begin_inset CommandInset toc':u'TableOfContents', 
      u'\\begin_inset ERT':u'ERT', u'\\begin_inset Flex':u'FlexInset', 
      u'\\begin_inset Flex Chunkref':u'NewfangledChunkRef', 
      u'\\begin_inset Flex Marginnote':u'SideNote', 
      u'\\begin_inset Flex Sidenote':u'SideNote', 
      u'\\begin_inset Flex URL':u'FlexURL', u'\\begin_inset Float':u'Float', 
      u'\\begin_inset FloatList':u'ListOf', u'\\begin_inset Foot':u'Footnote', 
      u'\\begin_inset Formula':u'Formula', 
      u'\\begin_inset FormulaMacro':u'FormulaMacro', 
      u'\\begin_inset Graphics':u'Image', 
      u'\\begin_inset Index':u'IndexReference', 
      u'\\begin_inset Info':u'InfoInset', 
      u'\\begin_inset LatexCommand bibitem':u'BiblioEntry', 
      u'\\begin_inset LatexCommand bibtex':u'BibTeX', 
      u'\\begin_inset LatexCommand cite':u'BiblioCitation', 
      u'\\begin_inset LatexCommand citealt':u'BiblioCitation', 
      u'\\begin_inset LatexCommand citep':u'BiblioCitation', 
      u'\\begin_inset LatexCommand citet':u'BiblioCitation', 
      u'\\begin_inset LatexCommand htmlurl':u'URL', 
      u'\\begin_inset LatexCommand index':u'IndexReference', 
      u'\\begin_inset LatexCommand label':u'Label', 
      u'\\begin_inset LatexCommand nomenclature':u'NomenclatureEntry', 
      u'\\begin_inset LatexCommand prettyref':u'Reference', 
      u'\\begin_inset LatexCommand printindex':u'PrintIndex', 
      u'\\begin_inset LatexCommand printnomenclature':u'PrintNomenclature', 
      u'\\begin_inset LatexCommand ref':u'Reference', 
      u'\\begin_inset LatexCommand tableofcontents':u'TableOfContents', 
      u'\\begin_inset LatexCommand url':u'URL', 
      u'\\begin_inset LatexCommand vref':u'Reference', 
      u'\\begin_inset Marginal':u'SideNote', 
      u'\\begin_inset Newline':u'NewlineInset', 
      u'\\begin_inset Newpage':u'NewPageInset', u'\\begin_inset Note':u'Note', 
      u'\\begin_inset OptArg':u'ShortTitle', 
      u'\\begin_inset Phantom':u'PhantomText', 
      u'\\begin_inset Quotes':u'QuoteContainer', 
      u'\\begin_inset Tabular':u'Table', u'\\begin_inset Text':u'InsetText', 
      u'\\begin_inset VSpace':u'VerticalSpace', u'\\begin_inset Wrap':u'Wrap', 
      u'\\begin_inset listings':u'Listing', u'\\begin_inset space':u'Space', 
      u'\\begin_layout':u'Layout', u'\\begin_layout Abstract':u'Abstract', 
      u'\\begin_layout Author':u'Author', 
      u'\\begin_layout Bibliography':u'Bibliography', 
      u'\\begin_layout Chunk':u'NewfangledChunk', 
      u'\\begin_layout Description':u'Description', 
      u'\\begin_layout Enumerate':u'ListItem', 
      u'\\begin_layout Itemize':u'ListItem', u'\\begin_layout List':u'List', 
      u'\\begin_layout LyX-Code':u'LyXCode', 
      u'\\begin_layout Plain':u'PlainLayout', 
      u'\\begin_layout Standard':u'StandardLayout', 
      u'\\begin_layout Title':u'Title', u'\\begin_preamble':u'LyXPreamble', 
      u'\\change_deleted':u'ChangeDeleted', 
      u'\\change_inserted':u'ChangeInserted', 
      u'\\change_unchanged':u'BlackBox', u'\\color':u'ColorText', 
      u'\\color inherit':u'BlackBox', u'\\color none':u'BlackBox', 
      u'\\emph default':u'BlackBox', u'\\emph off':u'BlackBox', 
      u'\\emph on':u'EmphaticText', u'\\emph toggle':u'EmphaticText', 
      u'\\end_body':u'LyXFooter', u'\\family':u'TextFamily', 
      u'\\family default':u'BlackBox', u'\\family roman':u'BlackBox', 
      u'\\hfill':u'Hfill', u'\\labelwidthstring':u'BlackBox', 
      u'\\lang':u'LangLine', u'\\length':u'InsetLength', 
      u'\\lyxformat':u'LyXFormat', u'\\lyxline':u'LyXLine', 
      u'\\newline':u'Newline', u'\\newpage':u'NewPage', 
      u'\\noindent':u'BlackBox', u'\\noun default':u'BlackBox', 
      u'\\noun off':u'BlackBox', u'\\noun on':u'VersalitasText', 
      u'\\paragraph_spacing':u'BlackBox', u'\\series bold':u'BoldText', 
      u'\\series default':u'BlackBox', u'\\series medium':u'BlackBox', 
      u'\\shape':u'ShapedText', u'\\shape default':u'BlackBox', 
      u'\\shape up':u'BlackBox', u'\\size':u'SizeText', 
      u'\\size normal':u'BlackBox', u'\\start_of_appendix':u'StartAppendix', 
      u'\\strikeout default':u'BlackBox', u'\\strikeout on':u'StrikeOut', 
      }

  string = {
      u'startcommand':u'\\', 
      }

  table = {
      u'headers':[u'<lyxtabular',u'<features',], 
      }

class EscapeConfig(object):
  "Configuration class from config file"

  chars = {
      u'\n':u'', u' -- ':u' — ', u'\'':u'’', u'---':u'—', u'`':u'‘', 
      }

  commands = {
      u'\\InsetSpace \\space{}':u' ', u'\\InsetSpace \\thinspace{}':u' ', 
      u'\\InsetSpace ~':u' ', u'\\SpecialChar \\-':u'', 
      u'\\SpecialChar \\@.':u'.', u'\\SpecialChar \\ldots{}':u'…', 
      u'\\SpecialChar \\menuseparator':u' ▷ ', 
      u'\\SpecialChar \\nobreakdash-':u'-', u'\\SpecialChar \\slash{}':u'/', 
      u'\\SpecialChar \\textcompwordmark{}':u'', u'\\backslash':u'\\', 
      }

  entities = {
      u'&':u'&amp;', u'<':u'&lt;', u'>':u'&gt;', 
      }

  html = {
      u'/>':u'>', 
      }

  iso885915 = {
      u' ':u'&nbsp;', u' ':u'&emsp;', u' ':u'&#8197;', 
      }

  nonunicode = {
      u' ':u' ', 
      }

class FormulaConfig(object):
  "Configuration class from config file"

  alphacommands = {
      u'\\AA':u'Å', u'\\AE':u'Æ', u'\\DH':u'Ð', u'\\L':u'Ł', u'\\O':u'Ø', 
      u'\\OE':u'Œ', u'\\TH':u'Þ', u'\\aa':u'å', u'\\ae':u'æ', u'\\alpha':u'α', 
      u'\\beta':u'β', u'\\delta':u'δ', u'\\dh':u'ð', u'\\epsilon':u'ϵ', 
      u'\\eta':u'η', u'\\gamma':u'γ', u'\\i':u'ı', u'\\imath':u'ı', 
      u'\\iota':u'ι', u'\\j':u'ȷ', u'\\jmath':u'ȷ', u'\\kappa':u'κ', 
      u'\\l':u'ł', u'\\lambda':u'λ', u'\\mu':u'μ', u'\\nu':u'ν', u'\\o':u'ø', 
      u'\\oe':u'œ', u'\\omega':u'ω', u'\\phi':u'φ', u'\\pi':u'π', 
      u'\\psi':u'ψ', u'\\rho':u'ρ', u'\\sigma':u'σ', u'\\ss':u'ß', 
      u'\\tau':u'τ', u'\\textcrh':u'ħ', u'\\th':u'þ', u'\\theta':u'θ', 
      u'\\upsilon':u'υ', u'\\varDelta':u'∆', u'\\varGamma':u'Γ', 
      u'\\varLambda':u'Λ', u'\\varOmega':u'Ω', u'\\varPhi':u'Φ', 
      u'\\varPi':u'Π', u'\\varPsi':u'Ψ', u'\\varSigma':u'Σ', 
      u'\\varTheta':u'Θ', u'\\varUpsilon':u'Υ', u'\\varXi':u'Ξ', 
      u'\\varepsilon':u'ε', u'\\varkappa':u'ϰ', u'\\varphi':u'φ', 
      u'\\varpi':u'ϖ', u'\\varrho':u'ϱ', u'\\varsigma':u'ς', 
      u'\\vartheta':u'ϑ', u'\\xi':u'ξ', u'\\zeta':u'ζ', 
      }

  array = {
      u'begin':u'\\begin', u'cellseparator':u'&', u'end':u'\\end', 
      u'rowseparator':u'\\\\', 
      }

  bigbrackets = {
      u'(':[u'⎛',u'⎜',u'⎝',], u')':[u'⎞',u'⎟',u'⎠',], u'[':[u'⎡',u'⎢',u'⎣',], 
      u']':[u'⎤',u'⎥',u'⎦',], 
      }

  binomialfunctions = {
      u'\\dbinom':[u'(',u')',], u'\\tbinom':[u'(',u')',], 
      }

  bracketcommands = {
      u'\\left':u'span class="symbol"', 
      u'\\left.':u'<span class="leftdot"></span>', 
      u'\\middle':u'span class="symbol"', u'\\right':u'span class="symbol"', 
      u'\\right.':u'<span class="rightdot"></span>', 
      }

  combiningfunctions = {
      u'\\"':u'̈', u'\\\'':u'́', u'\\^':u'̂', u'\\`':u'̀', u'\\acute':u'́', 
      u'\\bar':u'̄', u'\\breve':u'̆', u'\\c':u'̧', u'\\check':u'̌', 
      u'\\dddot':u'⃛', u'\\ddot':u'̈', u'\\dot':u'̇', u'\\grave':u'̀', 
      u'\\hat':u'̂', u'\\mathring':u'̊', u'\\overleftarrow':u'⃖', 
      u'\\overrightarrow':u'⃗', u'\\r':u'̥', u'\\s':u'̩', 
      u'\\textsubring':u'̥', u'\\tilde':u'̃', u'\\vec':u'⃗', u'\\~':u'̃', 
      }

  commands = {
      u'\\ ':u' ', u'\\!':u'', u'\\#':u'#', u'\\$':u'$', u'\\%':u'%', 
      u'\\&#38;':u'&', u'\\,':u' ', u'\\:':u' ', u'\\;':u' ', 
      u'\\APLdownarrowbox':u'⍗', u'\\APLleftarrowbox':u'⍇', 
      u'\\APLrightarrowbox':u'⍈', u'\\APLuparrowbox':u'⍐', u'\\Box':u'□', 
      u'\\Bumpeq':u'≎', u'\\CIRCLE':u'●', u'\\Cap':u'⋒', u'\\CheckedBox':u'☑', 
      u'\\Circle':u'○', u'\\Coloneqq':u'⩴', u'\\Corresponds':u'≙', 
      u'\\Cup':u'⋓', u'\\Delta':u'Δ', u'\\Diamond':u'◇', u'\\Downarrow':u'⇓', 
      u'\\EUR':u'€', u'\\Gamma':u'Γ', u'\\Im':u'ℑ', u'\\Join':u'⨝', 
      u'\\LEFTCIRCLE':u'◖', u'\\LEFTcircle':u'◐', u'\\Lambda':u'Λ', 
      u'\\Leftarrow':u'⇐', u'\\Lleftarrow':u'⇚', u'\\Longleftarrow':u'⟸', 
      u'\\Longleftrightarrow':u'⟺', u'\\Longrightarrow':u'⟹', u'\\Lsh':u'↰', 
      u'\\Mapsfrom':u'⇐|', u'\\Mapsto':u'|⇒', u'\\Omega':u'Ω', u'\\P':u'¶', 
      u'\\Phi':u'Φ', u'\\Pi':u'Π', u'\\Pr':u'Pr', u'\\Psi':u'Ψ', 
      u'\\RIGHTCIRCLE':u'◗', u'\\RIGHTcircle':u'◑', u'\\Re':u'ℜ', 
      u'\\Rrightarrow':u'⇛', u'\\Rsh':u'↱', u'\\S':u'§', u'\\Sigma':u'Σ', 
      u'\\Square':u'☐', u'\\Subset':u'⋐', u'\\Supset':u'⋑', u'\\Theta':u'Θ', 
      u'\\Uparrow':u'⇑', u'\\Updownarrow':u'⇕', u'\\Upsilon':u'Υ', 
      u'\\Vdash':u'⊩', u'\\Vert':u'∥', u'\\Vvdash':u'⊪', u'\\XBox':u'☒', 
      u'\\Xi':u'Ξ', u'\\Yup':u'⅄', u'\\\\':u'<br/>', u'\\_':u'_', 
      u'\\aleph':u'ℵ', u'\\amalg':u'∐', u'\\angle':u'∠', u'\\aquarius':u'♒', 
      u'\\arccos':u'arccos', u'\\arcsin':u'arcsin', u'\\arctan':u'arctan', 
      u'\\arg':u'arg', u'\\aries':u'♈', u'\\ast':u'∗', u'\\asymp':u'≍', 
      u'\\backepsilon':u'∍', u'\\backprime':u'‵', u'\\backsimeq':u'⋍', 
      u'\\backslash':u'\\', u'\\barwedge':u'⊼', u'\\because':u'∵', 
      u'\\beth':u'ℶ', u'\\between':u'≬', u'\\bigcap':u'∩', u'\\bigcirc':u'○', 
      u'\\bigcup':u'∪', u'\\bigodot':u'⊙', u'\\bigoplus':u'⊕', 
      u'\\bigotimes':u'⊗', u'\\bigsqcup':u'⊔', u'\\bigstar':u'★', 
      u'\\bigtriangledown':u'▽', u'\\bigtriangleup':u'△', u'\\biguplus':u'⊎', 
      u'\\bigvee':u'∨', u'\\bigwedge':u'∧', u'\\blacklozenge':u'⧫', 
      u'\\blacksmiley':u'☻', u'\\blacksquare':u'■', u'\\blacktriangle':u'▲', 
      u'\\blacktriangledown':u'▼', u'\\blacktriangleright':u'▶', u'\\bot':u'⊥', 
      u'\\bowtie':u'⋈', u'\\box':u'▫', u'\\boxdot':u'⊡', u'\\bullet':u'•', 
      u'\\bumpeq':u'≏', u'\\cancer':u'♋', u'\\cap':u'∩', u'\\capricornus':u'♑', 
      u'\\cdot':u'⋅', u'\\cdots':u'⋯', u'\\centerdot':u'∙', 
      u'\\checkmark':u'✓', u'\\chi':u'χ', u'\\circ':u'○', u'\\circeq':u'≗', 
      u'\\circledR':u'®', u'\\circledast':u'⊛', u'\\circledcirc':u'⊚', 
      u'\\circleddash':u'⊝', u'\\clubsuit':u'♣', u'\\coloneqq':u'≔', 
      u'\\complement':u'∁', u'\\cong':u'≅', u'\\coprod':u'∐', 
      u'\\copyright':u'©', u'\\cos':u'cos', u'\\cosh':u'cosh', u'\\cot':u'cot', 
      u'\\coth':u'coth', u'\\csc':u'csc', u'\\cup':u'∪', 
      u'\\curvearrowleft':u'↶', u'\\curvearrowright':u'↷', u'\\dag':u'†', 
      u'\\dagger':u'†', u'\\daleth':u'ℸ', u'\\dashleftarrow':u'⇠', 
      u'\\dashv':u'⊣', u'\\ddag':u'‡', u'\\ddagger':u'‡', u'\\ddots':u'⋱', 
      u'\\deg':u'deg', u'\\det':u'det', u'\\diagdown':u'╲', u'\\diagup':u'╱', 
      u'\\diamond':u'◇', u'\\diamondsuit':u'♦', u'\\dim':u'dim', 
      u'\\displaystyle':u'', u'\\div':u'÷', u'\\divideontimes':u'⋇', 
      u'\\dotdiv':u'∸', u'\\doteq':u'≐', u'\\doteqdot':u'≑', u'\\dotplus':u'∔', 
      u'\\dots':u'…', u'\\doublebarwedge':u'⌆', u'\\downarrow':u'↓', 
      u'\\downdownarrows':u'⇊', u'\\downharpoonleft':u'⇃', 
      u'\\downharpoonright':u'⇂', u'\\earth':u'♁', u'\\ell':u'ℓ', 
      u'\\emptyset':u'∅', u'\\eqcirc':u'≖', u'\\eqcolon':u'≕', u'\\eqsim':u'≂', 
      u'\\euro':u'€', u'\\exists':u'∃', u'\\exp':u'exp', 
      u'\\fallingdotseq':u'≒', u'\\female':u'♀', u'\\flat':u'♭', 
      u'\\forall':u'∀', u'\\frown':u'⌢', u'\\frownie':u'☹', u'\\gcd':u'gcd', 
      u'\\gemini':u'♊', u'\\geq)':u'≥', u'\\geqq':u'≧', u'\\geqslant':u'≥', 
      u'\\gets':u'←', u'\\gg':u'≫', u'\\ggg':u'⋙', u'\\gimel':u'ℷ', 
      u'\\gneqq':u'≩', u'\\gnsim':u'⋧', u'\\gtrdot':u'⋗', u'\\gtreqless':u'⋚', 
      u'\\gtreqqless':u'⪌', u'\\gtrless':u'≷', u'\\gtrsim':u'≳', 
      u'\\hbar':u'ℏ', u'\\heartsuit':u'♥', 
      u'\\hfill':u'<span class="hfill"> </span>', u'\\hom':u'hom', 
      u'\\hookleftarrow':u'↩', u'\\hookrightarrow':u'↪', u'\\hslash':u'ℏ', 
      u'\\idotsint':u'<span class="bigsymbol">∫⋯∫</span>', 
      u'\\iiint':u'<span class="bigsymbol">∭</span>', 
      u'\\iint':u'<span class="bigsymbol">∬</span>', u'\\imath':u'ı', 
      u'\\inf':u'inf', u'\\infty':u'∞', u'\\invneg':u'⌐', u'\\jmath':u'ȷ', 
      u'\\jupiter':u'♃', u'\\ker':u'ker', u'\\land':u'∧', 
      u'\\landupint':u'<span class="bigsymbol">∱</span>', u'\\langle':u'⟨', 
      u'\\lbrace':u'{', u'\\lbrace)':u'{', u'\\lbrack':u'[', u'\\lceil':u'⌈', 
      u'\\ldots':u'…', u'\\leadsto':u'⇝', u'\\leftarrow)':u'←', 
      u'\\leftarrowtail':u'↢', u'\\leftarrowtobar':u'⇤', 
      u'\\leftharpoondown':u'↽', u'\\leftharpoonup':u'↼', 
      u'\\leftleftarrows':u'⇇', u'\\leftleftharpoons':u'⥢', u'\\leftmoon':u'☾', 
      u'\\leftrightarrow':u'↔', u'\\leftrightarrows':u'⇆', 
      u'\\leftrightharpoons':u'⇋', u'\\leftthreetimes':u'⋋', u'\\leo':u'♌', 
      u'\\leq)':u'≤', u'\\leqq':u'≦', u'\\leqslant':u'≤', u'\\lessdot':u'⋖', 
      u'\\lesseqgtr':u'⋛', u'\\lesseqqgtr':u'⪋', u'\\lessgtr':u'≶', 
      u'\\lesssim':u'≲', u'\\lfloor':u'⌊', u'\\lg':u'lg', u'\\lhd':u'⊲', 
      u'\\libra':u'♎', u'\\lightning':u'↯', u'\\liminf':u'liminf', 
      u'\\limsup':u'limsup', u'\\ll':u'≪', u'\\lll':u'⋘', u'\\ln':u'ln', 
      u'\\lneqq':u'≨', u'\\lnot':u'¬', u'\\lnsim':u'⋦', u'\\log':u'log', 
      u'\\longleftarrow':u'⟵', u'\\longleftrightarrow':u'⟷', 
      u'\\longmapsto':u'⟼', u'\\longrightarrow':u'⟶', u'\\looparrowleft':u'↫', 
      u'\\looparrowright':u'↬', u'\\lor':u'∨', u'\\lozenge':u'◊', 
      u'\\ltimes':u'⋉', u'\\lyxlock':u'', u'\\male':u'♂', u'\\maltese':u'✠', 
      u'\\mapsfrom':u'↤', u'\\mapsto':u'↦', u'\\mathcircumflex':u'^', 
      u'\\max':u'max', u'\\measuredangle':u'∡', u'\\mercury':u'☿', 
      u'\\mho':u'℧', u'\\mid':u'∣', u'\\min':u'min', u'\\models':u'⊨', 
      u'\\mp':u'∓', u'\\multimap':u'⊸', u'\\nLeftarrow':u'⇍', 
      u'\\nLeftrightarrow':u'⇎', u'\\nRightarrow':u'⇏', u'\\nVDash':u'⊯', 
      u'\\nabla':u'∇', u'\\napprox':u'≉', u'\\natural':u'♮', u'\\ncong':u'≇', 
      u'\\nearrow':u'↗', u'\\neg':u'¬', u'\\neg)':u'¬', u'\\neptune':u'♆', 
      u'\\nequiv':u'≢', u'\\newline':u'<br/>', u'\\nexists':u'∄', 
      u'\\ngeqslant':u'≱', u'\\ngtr':u'≯', u'\\ngtrless':u'≹', u'\\ni':u'∋', 
      u'\\ni)':u'∋', u'\\nleftarrow':u'↚', u'\\nleftrightarrow':u'↮', 
      u'\\nleqslant':u'≰', u'\\nless':u'≮', u'\\nlessgtr':u'≸', u'\\nmid':u'∤', 
      u'\\nonumber':u'', u'\\not':u'¬', u'\\not<':u'≮', u'\\not=':u'≠', 
      u'\\not>':u'≯', u'\\notbackslash':u'⍀', u'\\notin':u'∉', u'\\notni':u'∌', 
      u'\\notslash':u'⌿', u'\\nparallel':u'∦', u'\\nprec':u'⊀', 
      u'\\nrightarrow':u'↛', u'\\nsim':u'≁', u'\\nsimeq':u'≄', 
      u'\\nsqsubset':u'⊏̸', u'\\nsubseteq':u'⊈', u'\\nsucc':u'⊁', 
      u'\\nsucccurlyeq':u'⋡', u'\\nsupset':u'⊅', u'\\nsupseteq':u'⊉', 
      u'\\ntriangleleft':u'⋪', u'\\ntrianglelefteq':u'⋬', 
      u'\\ntriangleright':u'⋫', u'\\ntrianglerighteq':u'⋭', u'\\nvDash':u'⊭', 
      u'\\nvdash':u'⊬', u'\\nwarrow':u'↖', u'\\odot':u'⊙', 
      u'\\officialeuro':u'€', u'\\oiiint':u'<span class="bigsymbol">∰</span>', 
      u'\\oiint':u'<span class="bigsymbol">∯</span>', 
      u'\\oint':u'<span class="bigsymbol">∮</span>', 
      u'\\ointclockwise':u'<span class="bigsymbol">∲</span>', 
      u'\\ointctrclockwise':u'<span class="bigsymbol">∳</span>', 
      u'\\ominus':u'⊖', u'\\oplus':u'⊕', u'\\oslash':u'⊘', u'\\otimes':u'⊗', 
      u'\\owns':u'∋', u'\\parallel':u'∥', u'\\partial':u'∂', u'\\perp':u'⊥', 
      u'\\pisces':u'♓', u'\\pitchfork':u'⋔', u'\\pluto':u'♇', u'\\pm':u'±', 
      u'\\pointer':u'➪', u'\\pounds':u'£', u'\\prec':u'≺', 
      u'\\preccurlyeq':u'≼', u'\\preceq':u'≼', u'\\precsim':u'≾', 
      u'\\prime':u'′', u'\\prompto':u'∝', u'\\qquad':u'  ', u'\\quad':u' ', 
      u'\\quarternote':u'♩', u'\\rangle':u'⟩', u'\\rbrace':u'}', 
      u'\\rbrace)':u'}', u'\\rbrack':u']', u'\\rceil':u'⌉', u'\\rfloor':u'⌋', 
      u'\\rhd':u'⊳', u'\\rightarrow)':u'→', u'\\rightarrowtail':u'↣', 
      u'\\rightarrowtobar':u'⇥', u'\\rightharpoondown':u'⇁', 
      u'\\rightharpoonup':u'⇀', u'\\rightharpooondown':u'⇁', 
      u'\\rightharpooonup':u'⇀', u'\\rightleftarrows':u'⇄', 
      u'\\rightleftharpoons':u'⇌', u'\\rightmoon':u'☽', 
      u'\\rightrightarrows':u'⇉', u'\\rightrightharpoons':u'⥤', 
      u'\\rightthreetimes':u'⋌', u'\\risingdotseq':u'≓', u'\\rtimes':u'⋊', 
      u'\\sagittarius':u'♐', u'\\saturn':u'♄', u'\\scorpio':u'♏', 
      u'\\scriptscriptstyle':u'', u'\\scriptstyle':u'', u'\\searrow':u'↘', 
      u'\\sec':u'sec', u'\\setminus':u'∖', u'\\sharp':u'♯', u'\\simeq':u'≃', 
      u'\\sin':u'sin', u'\\sinh':u'sinh', u'\\slash':u'∕', u'\\smile':u'⌣', 
      u'\\smiley':u'☺', u'\\spadesuit':u'♠', u'\\sphericalangle':u'∢', 
      u'\\sqcap':u'⊓', u'\\sqcup':u'⊔', u'\\sqsubset':u'⊏', 
      u'\\sqsubseteq':u'⊑', u'\\sqsupset':u'⊐', u'\\sqsupseteq':u'⊒', 
      u'\\square':u'□', u'\\star':u'⋆', u'\\subseteqq':u'⫅', 
      u'\\subsetneqq':u'⫋', u'\\succ':u'≻', u'\\succcurlyeq':u'≽', 
      u'\\succeq':u'≽', u'\\succnsim':u'⋩', u'\\succsim':u'≿', u'\\sun':u'☼', 
      u'\\sup':u'sup', u'\\supseteqq':u'⫆', u'\\supsetneqq':u'⫌', 
      u'\\surd':u'√', u'\\swarrow':u'↙', u'\\tan':u'tan', u'\\tanh':u'tanh', 
      u'\\taurus':u'♉', u'\\textasciicircum':u'^', u'\\textasciitilde':u'~', 
      u'\\textbackslash':u'\\', u'\\textendash':u'—', u'\\textgreater':u'>', 
      u'\\textless':u'<', u'\\textordfeminine':u'ª', 
      u'\\textordmasculine':u'º', u'\\textquotedblleft':u'“', 
      u'\\textquotedblright':u'”', u'\\textregistered':u'®', 
      u'\\textstyle':u'', u'\\texttrademark':u'™', u'\\therefore':u'∴', 
      u'\\top':u'⊤', u'\\triangle':u'△', u'\\triangleleft':u'⊲', 
      u'\\trianglelefteq':u'⊴', u'\\triangleq':u'≜', u'\\triangleright':u'▷', 
      u'\\trianglerighteq':u'⊵', u'\\twoheadleftarrow':u'↞', 
      u'\\twoheadrightarrow':u'↠', u'\\twonotes':u'♫', u'\\udot':u'⊍', 
      u'\\unlhd':u'⊴', u'\\unrhd':u'⊵', u'\\unrhl':u'⊵', u'\\uparrow':u'↑', 
      u'\\updownarrow':u'↕', u'\\upharpoonleft':u'↿', u'\\upharpoonright':u'↾', 
      u'\\uplus':u'⊎', u'\\upuparrows':u'⇈', u'\\uranus':u'♅', u'\\vDash':u'⊨', 
      u'\\varclubsuit':u'♧', u'\\vardiamondsuit':u'♦', u'\\varheartsuit':u'♥', 
      u'\\varnothing':u'∅', u'\\varspadesuit':u'♤', u'\\vdash':u'⊢', 
      u'\\vdots':u'⋮', u'\\vee':u'∨', u'\\vee)':u'∨', u'\\veebar':u'⊻', 
      u'\\vert':u'∣', u'\\virgo':u'♍', u'\\wedge':u'∧', u'\\wedge)':u'∧', 
      u'\\wp':u'℘', u'\\wr':u'≀', u'\\yen':u'¥', u'\\{':u'{', u'\\|':u'∥', 
      u'\\}':u'}', 
      }

  decoratedcommand = {
      
      }

  decoratingfunctions = {
      u'\\overleftarrow':u'⟵', u'\\overrightarrow':u'⟶', u'\\widehat':u'^', 
      }

  definingfunctions = {
      u'\\newcommand':u'[$n!][$1][$2][$3][$4][$5][$6][$7][$8][$9]{$d}', 
      u'\\renewcommand':u'[$n!][$1][$2][$3][$4][$5][$6][$7][$8][$9]{$d}', 
      }

  endings = {
      u'bracket':u'}', u'complex':u'\\]', u'endafter':u'}', 
      u'endbefore':u'\\end{', u'squarebracket':u']', 
      }

  environments = {
      u'align':[u'r',u'l',], u'eqnarray':[u'r',u'c',u'l',], 
      u'gathered':[u'l',u'l',], 
      }

  fontfunctions = {
      u'\\boldsymbol':u'b', u'\\mathbb':u'span class="blackboard"', 
      u'\\mathbb{A}':u'𝔸', u'\\mathbb{B}':u'𝔹', u'\\mathbb{C}':u'ℂ', 
      u'\\mathbb{D}':u'𝔻', u'\\mathbb{E}':u'𝔼', u'\\mathbb{F}':u'𝔽', 
      u'\\mathbb{G}':u'𝔾', u'\\mathbb{H}':u'ℍ', u'\\mathbb{J}':u'𝕁', 
      u'\\mathbb{K}':u'𝕂', u'\\mathbb{L}':u'𝕃', u'\\mathbb{N}':u'ℕ', 
      u'\\mathbb{O}':u'𝕆', u'\\mathbb{P}':u'ℙ', u'\\mathbb{Q}':u'ℚ', 
      u'\\mathbb{R}':u'ℝ', u'\\mathbb{S}':u'𝕊', u'\\mathbb{T}':u'𝕋', 
      u'\\mathbb{W}':u'𝕎', u'\\mathbb{Z}':u'ℤ', u'\\mathbf':u'b', 
      u'\\mathcal':u'span class="script"', 
      u'\\mathfrak':u'span class="fraktur"', u'\\mathfrak{C}':u'ℭ', 
      u'\\mathfrak{F}':u'𝔉', u'\\mathfrak{H}':u'ℌ', u'\\mathfrak{I}':u'ℑ', 
      u'\\mathfrak{R}':u'ℜ', u'\\mathfrak{Z}':u'ℨ', u'\\mathit':u'i', 
      u'\\mathring{A}':u'Å', u'\\mathring{U}':u'Ů', u'\\mathring{a}':u'å', 
      u'\\mathring{u}':u'ů', u'\\mathring{w}':u'ẘ', u'\\mathring{y}':u'ẙ', 
      u'\\mathrm':u'span class="mathrm"', u'\\mathscr':u'span class="script"', 
      u'\\mathscr{B}':u'ℬ', u'\\mathscr{E}':u'ℰ', u'\\mathscr{F}':u'ℱ', 
      u'\\mathscr{H}':u'ℋ', u'\\mathscr{I}':u'ℐ', u'\\mathscr{L}':u'ℒ', 
      u'\\mathscr{M}':u'ℳ', u'\\mathscr{R}':u'ℛ', 
      u'\\mathsf':u'span class="mathsf"', u'\\mathtt':u'tt', 
      }

  hybridfunctions = {
      
      u'\\binom':[u'{$1}{$2}',u'f2{(}f0{f1{$1}f1{$2}}f2{)}',u'span class="binom"',u'span class="binomstack"',u'span class="bigsymbol"',], 
      u'\\boxed':[u'{$1}',u'f0{$1}',u'span class="boxed"',], 
      u'\\cfrac':[u'[$p!]{$1}{$2}',u'f0{f3{(}f1{$1}f3{)/(}f2{$2}f3{)}}',u'span class="fullfraction"',u'span class="numerator align-$p"',u'span class="denominator"',u'span class="ignored"',], 
      u'\\color':[u'{$p!}{$1}',u'f0{$1}',u'span style="color: $p;"',], 
      u'\\colorbox':[u'{$p!}{$1}',u'f0{$1}',u'span class="colorbox" style="background: $p;"',], 
      u'\\dfrac':[u'{$1}{$2}',u'f0{f3{(}f1{$1}f3{)/(}f2{$2}f3{)}}',u'span class="fullfraction"',u'span class="numerator"',u'span class="denominator"',u'span class="ignored"',], 
      u'\\fbox':[u'{$1}',u'f0{$1}',u'span class="fbox"',], 
      u'\\fcolorbox':[u'{$p!}{$q!}{$1}',u'f0{$1}',u'span class="boxed" style="border-color: $p; background: $q;"',], 
      u'\\frac':[u'{$1}{$2}',u'f0{f3{(}f1{$1}f3{)/(}f2{$2}f3{)}}',u'span class="fraction"',u'span class="numerator"',u'span class="denominator"',u'span class="ignored"',], 
      u'\\framebox':[u'[$p!][$q!]{$1}',u'f0{$1}',u'span class="framebox align-$q" style="width: $p;"',], 
      u'\\href':[u'[$o]{$u!}{$t!}',u'f0{$t}',u'a href="$u"',], 
      u'\\hspace':[u'{$p!}',u'f0{ }',u'span class="hspace" style="width: $p;"',], 
      u'\\leftroot':[u'{$p!}',u'f0{ }',u'span class="leftroot" style="width: $p;px"',], 
      u'\\nicefrac':[u'{$1}{$2}',u'f0{f1{$1}⁄f2{$2}}',u'span class="fraction"',u'sup class="numerator"',u'sub class="denominator"',u'span class="ignored"',], 
      u'\\raisebox':[u'{$p!}{$1}',u'f0{$1}',u'span class="raisebox" style="vertical-align: $p;"',], 
      u'\\renewenvironment':[u'{$1!}{$2!}{$3!}',u'',], 
      u'\\sqrt':[u'[$0]{$1}',u'f0{f1{$0}f2{√}f4{(}f3{$1}f4{)}}',u'span class="sqrt"',u'sup class="root"',u'span class="radical"',u'span class="root"',u'span class="ignored"',], 
      u'\\stackrel':[u'{$1}{$2}',u'f0{f1{$1}f2{$2}}',u'span class="stackrel"',u'span class="upstackrel"',u'span class="downstackrel"',], 
      u'\\textcolor':[u'{$p!}{$1}',u'f0{$1}',u'span style="color: $p;"',], 
      u'\\unit':[u'[$0]{$1}',u'$0f0{$1.font}',u'span class="unit"',], 
      u'\\unitfrac':[u'[$0]{$1}{$2}',u'$0f0{f1{$1.font}⁄f2{$2.font}}',u'span class="fraction"',u'sup class="unit"',u'sub class="unit"',], 
      u'\\uproot':[u'{$p!}',u'f0{ }',u'span class="uproot" style="width: $p;px"',], 
      u'\\url':[u'{$u!}',u'f0{$u}',u'a href="$u"',], 
      u'\\vspace':[u'{$p!}',u'f0{ }',u'span class="vspace" style="height: $p;"',], 
      }

  labelfunctions = {
      u'\\label':u'a name="#"', 
      }

  limitcommands = {
      u'\\int':[u'<span class="bigsymbol">∫</span>',u'⌠',u'⌡',], 
      u'\\intop':[u'<span class="bigsymbol">∫</span>',u'⌠',u'⌡',], 
      u'\\lim':[u'lim',], u'\\prod':[u'∏',], u'\\smallint':[u'∫',], 
      u'\\sum':[u'<span class="bigsymbol">∑</span>',u'⎲',u'⎳',], 
      }

  modified = {
      u'\n':u'', u' ':u'', u'$':u'', u'&':u'	', u'\'':u'’', u'+':u' + ', 
      u',':u', ', u'-':u' − ', u'/':u' ⁄ ', u'<':u' &lt; ', u'=':u' = ', 
      u'>':u' &gt; ', u'@':u'', u'~':u'', 
      }

  onefunctions = {
      u'\\Big':u'span class="bigsymbol"', u'\\Bigg':u'span class="hugesymbol"', 
      u'\\bar':u'span class="bar"', u'\\begin{array}':u'span class="arraydef"', 
      u'\\big':u'span class="symbol"', u'\\bigg':u'span class="largesymbol"', 
      u'\\bigl':u'span class="bigsymbol"', u'\\bigr':u'span class="bigsymbol"', 
      u'\\ensuremath':u'span class="ensuremath"', 
      u'\\hphantom':u'span class="phantom"', 
      u'\\overbrace':u'span class="overbrace"', 
      u'\\overline':u'span class="overline"', 
      u'\\phantom':u'span class="phantom"', 
      u'\\underbrace':u'span class="underbrace"', u'\\underline':u'u', 
      u'\\vphantom':u'span class="phantom"', 
      }

  preamblefunctions = {
      u'\\setcounter':[u'{$p!}{$n!}',u'setcounter',], 
      }

  spacedcommands = {
      u'\\Leftrightarrow':u'⇔', u'\\Rightarrow':u'⇒', u'\\approx':u'≈', 
      u'\\dashrightarrow':u'⇢', u'\\equiv':u'≡', u'\\ge':u'≥', u'\\geq':u'≥', 
      u'\\implies':u' ⇒ ', u'\\in':u'∈', u'\\le':u'≤', u'\\leftarrow':u'←', 
      u'\\leq':u'≤', u'\\ne':u'≠', u'\\neq':u'≠', u'\\not\\in':u'∉', 
      u'\\propto':u'∝', u'\\rightarrow':u'→', u'\\rightsquigarrow':u'⇝', 
      u'\\sim':u'~', u'\\subset':u'⊂', u'\\subseteq':u'⊆', u'\\supset':u'⊃', 
      u'\\supseteq':u'⊇', u'\\times':u'×', u'\\to':u'→', 
      }

  starts = {
      u'beginafter':u'}', u'beginbefore':u'\\begin{', u'bracket':u'{', 
      u'command':u'\\', u'comment':u'%', u'complex':u'\\[', u'simple':u'$', 
      u'squarebracket':u'[', u'unnumbered':u'*', 
      }

  symbolfunctions = {
      u'^':u'sup', u'_':u'sub', 
      }

  textfunctions = {
      u'\\mbox':u'span class="mbox"', u'\\text':u'span class="text"', 
      u'\\textbf':u'b', u'\\textipa':u'span class="textipa"', u'\\textit':u'i', 
      u'\\textnormal':u'span class="textnormal"', 
      u'\\textrm':u'span class="textrm"', 
      u'\\textsc':u'span class="versalitas"', 
      u'\\textsf':u'span class="textsf"', u'\\textsl':u'i', u'\\texttt':u'tt', 
      u'\\textup':u'span class="normal"', 
      }

  unmodified = {
      
      u'characters':[u'.',u'*',u'€',u'(',u')',u'[',u']',u':',u'·',u'!',u';',u'|',u'§',u'"',], 
      }

class GeneralConfig(object):
  "Configuration class from config file"

  version = {
      u'date':u'2010-12-23', u'lyxformat':u'398', u'number':u'1.1.2', 
      }

class HeaderConfig(object):
  "Configuration class from config file"

  parameters = {
      u'beginpreamble':u'\\begin_preamble', u'branch':u'\\branch', 
      u'documentclass':u'\\textclass', u'endbranch':u'\\end_branch', 
      u'endpreamble':u'\\end_preamble', u'language':u'\\language', 
      u'lstset':u'\\lstset', u'outputchanges':u'\\output_changes', 
      u'paragraphseparation':u'\\paragraph_separation', 
      u'pdftitle':u'\\pdf_title', u'secnumdepth':u'\\secnumdepth', 
      u'tocdepth':u'\\tocdepth', 
      }

  styles = {
      
      u'article':[u'article',u'aastex',u'aapaper',u'acmsiggraph',u'sigplanconf',u'achemso',u'amsart',u'apa',u'arab-article',u'armenian-article',u'article-beamer',u'chess',u'dtk',u'elsarticle',u'heb-article',u'IEEEtran',u'iopart',u'kluwer',u'scrarticle-beamer',u'scrartcl',u'extarticle',u'paper',u'mwart',u'revtex4',u'spie',u'svglobal3',u'ltugboat',u'agu-dtd',u'jgrga',u'agums',u'entcs',u'egs',u'ijmpc',u'ijmpd',u'singlecol-new',u'doublecol-new',u'isprs',u'tarticle',u'jsarticle',u'jarticle',u'jss',u'literate-article',u'siamltex',u'cl2emult',u'llncs',u'svglobal',u'svjog',u'svprobth',], 
      u'book':[u'book',u'amsbook',u'scrbook',u'extbook',u'tufte-book',u'report',u'extreport',u'scrreprt',u'memoir',u'tbook',u'jsbook',u'jbook',u'mwbk',u'svmono',u'svmult',u'treport',u'jreport',u'mwrep',], 
      }

class ImageConfig(object):
  "Configuration class from config file"

  converters = {
      
      u'imagemagick':u'convert[ -density $scale][ -define $format:use-cropbox=true] "$input" "$output"', 
      u'inkscape':u'inkscape "$input" --export-png="$output"', 
      }

  cropboxformats = {
      u'.eps':u'ps', u'.pdf':u'pdf', u'.ps':u'ps', 
      }

  formats = {
      u'default':u'.png', u'vector':[u'.svg',u'.eps',], 
      }

class LayoutConfig(object):
  "Configuration class from config file"

  groupable = {
      
      u'allowed':[u'StringContainer',u'Constant',u'TaggedText',u'Align',u'TextFamily',u'EmphaticText',u'VersalitasText',u'BarredText',u'SizeText',u'ColorText',u'LangLine',u'Formula',], 
      }

class NewfangleConfig(object):
  "Configuration class from config file"

  constants = {
      u'chunkref':u'chunkref{', u'endcommand':u'}', u'endmark':u'&gt;', 
      u'startcommand':u'\\', u'startmark':u'=&lt;', 
      }

class NumberingConfig(object):
  "Configuration class from config file"

  layouts = {
      
      u'ordered':[u'Chapter',u'Section',u'Subsection',u'Subsubsection',u'Paragraph',], 
      u'roman':[u'Part',u'Book',], 
      }

  sequence = {
      u'symbols':[u'*',u'**',u'†',u'‡',u'§',u'§§',u'¶',u'¶¶',u'#',u'##',], 
      }

class StyleConfig(object):
  "Configuration class from config file"

  hspaces = {
      u'\\enskip{}':u' ', u'\\hfill{}':u'<span class="hfill"> </span>', 
      u'\\hspace*{\\fill}':u' ', u'\\hspace*{}':u'', u'\\hspace{}':u' ', 
      u'\\negthinspace{}':u'', u'\\qquad{}':u'  ', u'\\quad{}':u' ', 
      u'\\space{}':u' ', u'\\thinspace{}':u' ', u'~':u' ', 
      }

  quotes = {
      u'ald':u'»', u'als':u'›', u'ard':u'«', u'ars':u'‹', u'eld':u'“', 
      u'els':u'‘', u'erd':u'”', u'ers':u'’', u'fld':u'«', u'fls':u'‹', 
      u'frd':u'»', u'frs':u'›', u'gld':u'„', u'gls':u'‚', u'grd':u'“', 
      u'grs':u'‘', u'pld':u'„', u'pls':u'‚', u'prd':u'”', u'prs':u'’', 
      u'sld':u'”', u'srd':u'”', 
      }

  referenceformats = {
      u'eqref':u'(@↕)', u'pageref':u'#↕', u'ref':u'@↕', 
      u'vpageref':u'on-page#↕', u'vref':u'@on-page#↕', 
      }

  size = {
      u'ignoredtexts':[u'col',u'text',u'line',u'page',u'theight',u'pheight',], 
      }

  vspaces = {
      u'bigskip':u'<div class="bigskip"> </div>', 
      u'defskip':u'<div class="defskip"> </div>', 
      u'medskip':u'<div class="medskip"> </div>', 
      u'smallskip':u'<div class="smallskip"> </div>', 
      u'vfill':u'<div class="vfill"> </div>', 
      }

class TOCConfig(object):
  "Configuration class from config file"

  extractplain = {
      
      u'allowed':[u'StringContainer',u'Constant',u'TaggedText',u'Align',u'TextFamily',u'EmphaticText',u'VersalitasText',u'BarredText',u'SizeText',u'ColorText',u'LangLine',u'Formula',], 
      u'cloned':[u'',], u'extracted':[u'',], 
      }

  extracttitle = {
      u'allowed':[u'StringContainer',u'Constant',u'Space',], 
      u'cloned':[u'TextFamily',u'EmphaticText',u'VersalitasText',u'BarredText',u'SizeText',u'ColorText',u'LangLine',u'Formula',], 
      u'extracted':[u'PlainLayout',u'TaggedText',u'Align',u'Caption',u'StandardLayout',], 
      }

class TagConfig(object):
  "Configuration class from config file"

  barred = {
      u'under':u'u', 
      }

  family = {
      u'sans':u'span class="sans"', u'typewriter':u'tt', 
      }

  flex = {
      u'CharStyle:Code':u'span class="code"', 
      u'CharStyle:MenuItem':u'span class="menuitem"', 
      u'Code':u'span class="code"', u'MenuItem':u'span class="menuitem"', 
      u'Noun':u'span class="noun"', u'Strong':u'span class="strong"', 
      }

  group = {
      u'layouts':[u'Quotation',u'Quote',], 
      }

  layouts = {
      u'Center':u'div', u'Chapter':u'h?', u'Date':u'h2', u'Paragraph':u'div', 
      u'Part':u'h1', u'Quotation':u'blockquote', u'Quote':u'blockquote', 
      u'Section':u'h?', u'Subsection':u'h?', u'Subsubsection':u'h?', 
      }

  listitems = {
      u'Enumerate':u'ol', u'Itemize':u'ul', 
      }

  notes = {
      u'Comment':u'', u'Greyedout':u'span class="greyedout"', u'Note':u'', 
      }

  shaped = {
      u'italic':u'i', u'slanted':u'i', u'smallcaps':u'span class="versalitas"', 
      }

class TranslationConfig(object):
  "Configuration class from config file"

  constants = {
      u'Appendix':u'Appendix', u'Book':u'Book', u'Chapter':u'Chapter', 
      u'Paragraph':u'Paragraph', u'Part':u'Part', u'Section':u'Section', 
      u'Subsection':u'Subsection', u'Subsubsection':u'Subsubsection', 
      u'abstract':u'Abstract', u'bibliography':u'Bibliography', 
      u'figure':u'figure', u'float-algorithm':u'Algorithm ', 
      u'float-figure':u'Figure ', u'float-listing':u'Listing ', 
      u'float-table':u'Table ', u'float-tableau':u'Tableau ', 
      u'footnotes':u'Footnotes', u'generated-by':u'Document generated by ', 
      u'generated-on':u' on ', u'index':u'Index', 
      u'jsmath-enable':u'Please enable JavaScript on your browser.', 
      u'jsmath-requires':u' requires JavaScript to correctly process the mathematics on this page. ', 
      u'jsmath-warning':u'Warning: ', u'list-algorithm':u'List of Algorithms', 
      u'list-figure':u'List of Figures', u'list-table':u'List of Tables', 
      u'list-tableau':u'List of Tableaux', u'main-page':u'Main page', 
      u'next':u'Next', u'nomenclature':u'Nomenclature', 
      u'on-page':u' on page ', u'prev':u'Previous', 
      u'references':u'References', u'toc':u'Table of Contents', 
      u'toc-for':u'Contents for ', u'up':u'Up', 
      }

  languages = {
      u'american':u'en', u'british':u'en', u'deutsch':u'de', u'dutch':u'nl', 
      u'english':u'en', u'french':u'fr', u'ngerman':u'de', u'spanish':u'es', 
      }






class CommandLineParser(object):
  "A parser for runtime options"

  def __init__(self, options):
    self.options = options

  def parseoptions(self, args):
    "Parse command line options"
    if len(args) == 0:
      return None
    while len(args) > 0 and args[0].startswith('--'):
      key, value = self.readoption(args)
      if not key:
        return 'Option ' + value + ' not recognized'
      if not value:
        return 'Option ' + key + ' needs a value'
      setattr(self.options, key, value)
    return None

  def readoption(self, args):
    "Read the key and value for an option"
    arg = args[0][2:]
    del args[0]
    if '=' in arg:
      return self.readequals(arg, args)
    key = arg.replace('-', '')
    if not hasattr(self.options, key):
      return None, key
    current = getattr(self.options, key)
    if isinstance(current, bool):
      return key, True
    # read value
    if len(args) == 0:
      return key, None
    if args[0].startswith('"'):
      initial = args[0]
      del args[0]
      return key, self.readquoted(args, initial)
    value = args[0]
    del args[0]
    if isinstance(current, list):
      current.append(value)
      return key, current
    return key, value

  def readquoted(self, args, initial):
    "Read a value between quotes"
    value = initial[1:]
    while len(args) > 0 and not args[0].endswith('"') and not args[0].startswith('--'):
      value += ' ' + args[0]
      del args[0]
    if len(args) == 0 or args[0].startswith('--'):
      return None
    value += ' ' + args[0:-1]
    return value

  def readequals(self, arg, args):
    "Read a value with equals"
    split = arg.split('=', 1)
    key = split[0]
    if not hasattr(self.options, key):
      return None, key
    value = split[1]
    if not value.startswith('"'):
      return key, value
    return key, self.readquoted(args, value)



class Options(object):
  "A set of runtime options"

  instance = None

  location = None
  nocopy = False
  copyright = False
  debug = False
  quiet = False
  version = False
  hardversion = False
  versiondate = False
  html = False
  help = False
  showlines = True
  unicode = False
  iso885915 = False
  css = []
  title = None
  directory = None
  destdirectory = None
  toc = False
  toctarget = ''
  forceformat = None
  lyxformat = False
  target = None
  splitpart = None
  memory = True
  lowmem = False
  nobib = False
  converter = 'imagemagick'
  raw = False
  jsmath = None
  mathjax = None
  nofooter = False
  template = None
  noconvert = False
  notoclabels = False
  letterfoot = True
  numberfoot = False
  symbolfoot = False
  hoverfoot = True
  marginfoot = False
  endfoot = False
  supfoot = True
  alignfoot = False
  footnotes = None
  imageformat = None
  copyimages = False
  embedcss = []

  # DCB : Add some stuff for syntax highlighting
  defaultbrush = None

  branches = dict()

  def parseoptions(self, args):
    "Parse command line options"
    Options.location = args[0]
    del args[0]
    parser = CommandLineParser(Options)
    result = parser.parseoptions(args)
    if result:
      Trace.error(result)
      self.usage()
    if Options.help:
      self.usage()
    if Options.version:
      self.showversion()
    if Options.hardversion:
      self.showhardversion()
    if Options.versiondate:
      self.showversiondate()
    if Options.lyxformat:
      self.showlyxformat()
    if Options.splitpart:
      try:
        Options.splitpart = int(Options.splitpart)
        if Options.splitpart <= 0:
          Trace.error('--splitpart requires a number bigger than zero')
          self.usage()
      except:
        Trace.error('--splitpart needs a numeric argument, not ' + Options.splitpart)
        self.usage()
    if Options.lowmem or Options.toc:
      Options.memory = False
    self.parsefootnotes()
    if Options.forceformat and not Options.imageformat:
      Options.imageformat = Options.forceformat
    if Options.imageformat == 'copy':
      Options.copyimages = True
    if Options.css == []:
      Options.css = ['http://elyxer.nongnu.org/lyx.css']
    # set in Trace if necessary
    for param in dir(Options):
      if hasattr(Trace, param + 'mode'):
        setattr(Trace, param + 'mode', getattr(self, param))

  def usage(self):
    "Show correct usage"
    Trace.error('Usage: ' + os.path.basename(Options.location) + ' [options] [filein] [fileout]')
    Trace.error('Convert LyX input file "filein" to HTML file "fileout".')
    Trace.error('If filein (or fileout) is not given use standard input (or output).')
    Trace.error('Main program of the eLyXer package (http://elyxer.nongnu.org/).')
    self.showoptions()

  def parsefootnotes(self):
    "Parse footnotes options."
    if not Options.footnotes:
      return
    Options.marginfoot = False
    Options.letterfoot = False
    options = Options.footnotes.split(',')
    for option in options:
      footoption = option + 'foot'
      if hasattr(Options, footoption):
        setattr(Options, footoption, True)
      else:
        Trace.error('Unknown footnotes option: ' + option)
    if not Options.endfoot and not Options.marginfoot and not Options.hoverfoot:
      Options.hoverfoot = True
    if not Options.numberfoot and not Options.symbolfoot:
      Options.letterfoot = True

  def showoptions(self):
    "Show all possible options"
    Trace.error('  Common options:')
    Trace.error('    --help:                 show this online help')
    Trace.error('    --quiet:                disables all runtime messages')
    Trace.error('')
    Trace.error('  Advanced options:')
    Trace.error('    --debug:                enable debugging messages (for developers)')
    Trace.error('    --version:              show version number and release date')
    Trace.error('    --lyxformat:            return the highest LyX version supported')
    Trace.error('  Options for HTML output:')
    Trace.error('    --title "title":        set the generated page title')
    Trace.error('    --css "file.css":       use a custom CSS file')
    Trace.error('    --embedcss "file.css":  embed styles from a CSS file into the output')
    Trace.error('    --html:                 output HTML 4.0 instead of the default XHTML')
    Trace.error('    --unicode:              full Unicode output')
    Trace.error('    --iso885915:            output a document with ISO-8859-15 encoding')
    Trace.error('    --nofooter:             remove the footer "generated by eLyXer"')
    Trace.error('    --defaultbrush:         the default SyntaxHighlighter brush to use for listings')
    Trace.error('  Options for image output:')
    Trace.error('    --directory "img_dir":  look for images in the specified directory')
    Trace.error('    --destdirectory "dest": put converted images into this directory')
    Trace.error('    --imageformat ".ext":   image output format, or "copy" to copy images')
    Trace.error('    --noconvert:            do not convert images, use in original locations')
    Trace.error('    --converter "inkscape": use an alternative program to convert images')
    Trace.error('  Options for footnote display:')
    Trace.error('    --numberfoot:           mark footnotes with numbers instead of letters')
    Trace.error('    --symbolfoot:           mark footnotes with symbols (*, **...)')
    Trace.error('    --hoverfoot:            show footnotes as hovering text (default)')
    Trace.error('    --marginfoot:           show footnotes with numbers instead of letters')
    Trace.error('    --endfoot:              show footnotes at the end of the page')
    Trace.error('    --supfoot:              use superscript for footnote markers (default)')
    Trace.error('    --alignfoot:            use aligned text for footnote markers')
    Trace.error('    --footnotes "options":  specify several comma-separated footnotes options')
    Trace.error('      Available options are: "number", "symbol", "hover", "margin", "end",')
    Trace.error('        "sup", "align"')
    Trace.error('  Advanced output options:')
    Trace.error('    --splitpart "depth":    split the resulting webpage at the given depth')
    Trace.error('    --toc:                  create a table of contents')
    Trace.error('    --target "frame":       make all links point to the given frame')
    Trace.error('    --toctarget "page":     generate a TOC that points to the given page')
    Trace.error('    --notoclabels:          omit the part labels in the TOC, such as Chapter')
    Trace.error('    --lowmem:               do the conversion on the fly (conserve memory)')
    Trace.error('    --raw:                  generate HTML without header or footer.')
    Trace.error('    --jsmath "URL":         use jsMath from the given URL to display equations')
    Trace.error('    --mathjax "URL":        use MathJax from the given URL to display equations')
    Trace.error('    --template "file":      use a template, put everything in <!--$content-->')
    Trace.error('    --copyright:            add a copyright notice at the bottom')
    Trace.error('    --nocopy (deprecated):  no effect, maintained for backwards compatibility')
    sys.exit()

  def showversion(self):
    "Return the current eLyXer version string"
    string = 'eLyXer version ' + GeneralConfig.version['number']
    string += ' (' + GeneralConfig.version['date'] + ')'
    Trace.error(string)
    sys.exit()

  def showhardversion(self):
    "Return just the version string"
    Trace.message(GeneralConfig.version['number'])
    sys.exit()

  def showversiondate(self):
    "Return just the version dte"
    Trace.message(GeneralConfig.version['date'])
    sys.exit()

  def showlyxformat(self):
    "Return just the lyxformat parameter"
    Trace.message(GeneralConfig.version['lyxformat'])
    sys.exit()

class BranchOptions(object):
  "A set of options for a branch"

  def __init__(self, name):
    self.name = name
    self.options = {'color':'#ffffff'}

  def set(self, key, value):
    "Set a branch option"
    if not key.startswith(ContainerConfig.string['startcommand']):
      Trace.error('Invalid branch option ' + key)
      return
    key = key.replace(ContainerConfig.string['startcommand'], '')
    self.options[key] = value

  def isselected(self):
    "Return if the branch is selected"
    if not 'selected' in self.options:
      return False
    return self.options['selected'] == '1'

  def __unicode__(self):
    "String representation"
    return 'options for ' + self.name + ': ' + unicode(self.options)













import gettext





class DocumentParameters(object):
  "Global parameters for the document."

  pdftitle = None
  indentstandard = False
  tocdepth = 10
  startinglevel = 0
  maxdepth = 10
  language = None
  bibliography = None
  outputchanges = False
  displaymode = False



class Translator(object):
  "Reads the configuration file and tries to find a translation."
  "Otherwise falls back to the messages in the config file."

  instance = None

  def translate(cls, key):
    "Get the translated message for a key."
    return cls.instance.getmessage(key)

  translate = classmethod(translate)

  def __init__(self):
    self.translation = None
    self.first = True

  def findtranslation(self):
    "Find the translation for the document language."
    self.langcodes = None
    if not DocumentParameters.language:
      Trace.error('No language in document')
      return
    if not DocumentParameters.language in TranslationConfig.languages:
      Trace.error('Unknown language ' + DocumentParameters.language)
      return
    if TranslationConfig.languages[DocumentParameters.language] == 'en':
      return
    langcodes = [TranslationConfig.languages[DocumentParameters.language]]
    try:
      self.translation = gettext.translation('elyxer', None, langcodes)
    except IOError:
      Trace.error('No translation for ' + unicode(langcodes))

  def getmessage(self, key):
    "Get the translated message for the given key."
    if self.first:
      self.findtranslation()
      self.first = False
    message = self.getuntranslated(key)
    if not self.translation:
      return message
    try:
      message = self.translation.ugettext(message)
    except IOError:
      pass
    return message

  def getuntranslated(self, key):
    "Get the untranslated message."
    if not key in TranslationConfig.constants:
      Trace.error('Cannot translate ' + key)
      return key
    return TranslationConfig.constants[key]

Translator.instance = Translator()



class NumberCounter(object):
  "A counter for numbers (by default)."
  "The type can be changed to return letters, roman numbers..."

  name = None
  value = None
  mode = None
  master = None

  letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
  symbols = NumberingConfig.sequence['symbols']
  romannumerals = [
      ('M', 1000), ('CM', 900), ('D', 500), ('CD', 400), ('C', 100),
      ('XC', 90), ('L', 50), ('XL', 40), ('X', 10), ('IX', 9), ('V', 5),
      ('IV', 4), ('I', 1)
      ]

  def __init__(self, name):
    "Give a name to the counter."
    self.name = name

  def setmode(self, mode):
    "Set the counter mode. Can be changed at runtime."
    self.mode = mode
    return self

  def init(self, value):
    "Set an initial value."
    self.value = value

  def increase(self):
    "Increase the counter value and return the counter."
    if not self.value:
      self.value = 0
    self.value += 1
    return self

  def gettext(self):
    "Get the next value as a text string."
    return unicode(self.value)

  def getletter(self):
    "Get the next value as a letter."
    return self.getsequence(self.letters)

  def getsymbol(self):
    "Get the next value as a symbol."
    return self.getsequence(self.symbols)

  def getsequence(self, sequence):
    "Get the next value from a sequence."
    return sequence[(self.value - 1) % len(sequence)]

  def getroman(self):
    "Get the next value as a roman number."
    result = ''
    number = self.value
    for numeral, value in self.romannumerals:
      if number >= value:
        result += numeral * (number / value)
        number = number % value
    return result

  def getvalue(self):
    "Get the current value as configured in the current mode."
    if not self.mode or self.mode in ['text', '1']:
      return self.gettext()
    if self.mode == 'A':
      return self.getletter()
    if self.mode == 'a':
      return self.getletter().lower()
    if self.mode == 'I':
      return self.getroman()
    if self.mode == '*':
      return self.getsymbol()
    Trace.error('Unknown counter mode ' + self.mode)
    return self.gettext()

  def getnext(self):
    "Get the next value as configured: increase() and getvalue()."
    return self.increase().getvalue()

  def reset(self):
    "Reset the counter."
    self.value = 0

  def __unicode__(self):
    "Return a printable representation."
    result = 'Counter ' + self.name
    if self.mode:
      result += ' in mode ' + self.mode
    return result

class DependentCounter(NumberCounter):
  "A counter which depends on another one (the master)."

  def setmaster(self, master):
    "Set the master counter."
    self.master = master
    self.last = self.master.getvalue()
    return self

  def increase(self):
    "Increase or, if the master counter has changed, restart."
    if self.last != self.master.getvalue():
      self.reset()
    NumberCounter.increase(self)
    self.last = self.master.getvalue()
    return self

  def getvalue(self):
    "Get the value of the combined counter: master.dependent."
    return self.master.getvalue() + '.' + NumberCounter.getvalue(self)

class NumberGenerator(object):
  "A number generator for unique sequences and hierarchical structures. Used in:"
  "  * ordered part numbers: Chapter 3, Section 5.3."
  "  * unique part numbers: Footnote 15, Bibliography cite [15]."
  "  * chaptered part numbers: Figure 3.15, Equation (8.3)."
  "  * unique roman part numbers: Part I, Book IV."

  chaptered = None
  generator = None

  romanlayouts = [x.lower() for x in NumberingConfig.layouts['roman']]
  orderedlayouts = [x.lower() for x in NumberingConfig.layouts['ordered']]

  counters = dict()
  appendix = None

  def deasterisk(self, type):
    "Remove the possible asterisk in a layout type."
    return type.replace('*', '')

  def isunique(self, type):
    "Find out if the layout type corresponds to a unique part."
    return self.isroman(type)

  def isroman(self, type):
    "Find out if the layout type should have roman numeration."
    return self.deasterisk(type).lower() in self.romanlayouts

  def isinordered(self, type):
    "Find out if the layout type corresponds to an (un)ordered part."
    return self.deasterisk(type).lower() in self.orderedlayouts

  def isnumbered(self, type):
    "Find out if the type for a layout corresponds to a numbered layout."
    if '*' in type:
      return False
    if self.isroman(type):
      return True
    if not self.isinordered(type):
      return False
    if self.getlevel(type) > DocumentParameters.maxdepth:
      return False
    return True

  def isunordered(self, type):
    "Find out if the type contains an asterisk, basically."
    return '*' in type

  def getlevel(self, type):
    "Get the level that corresponds to a layout type."
    if self.isunique(type):
      return 0
    if not self.isinordered(type):
      Trace.error('Unknown layout type ' + type)
      return 0
    type = self.deasterisk(type).lower()
    level = self.orderedlayouts.index(type) + 1
    return level - DocumentParameters.startinglevel

  def getparttype(self, type):
    "Obtain the type for the part: without the asterisk, "
    "and switched to Appendix if necessary."
    if NumberGenerator.appendix and self.getlevel(type) == 1:
      return 'Appendix'
    return self.deasterisk(type)

  def generate(self, type):
    "Generate a number for a layout type."
    "Unique part types such as Part or Book generate roman numbers: Part I."
    "Ordered part types return dot-separated tuples: Chapter 5, Subsection 2.3.5."
    "Everything else generates unique numbers: Bibliography [1]."
    "Each invocation results in a new number."
    return self.getcounter(type).getnext()

  def getcounter(self, type):
    "Get the counter for the given type."
    type = type.lower()
    if not type in self.counters:
      self.counters[type] = self.create(type)
    return self.counters[type]

  def create(self, type):
    "Create a counter for the given type."
    if self.isnumbered(type) and self.getlevel(type) > 1:
      index = self.orderedlayouts.index(type)
      above = self.orderedlayouts[index - 1]
      master = self.getcounter(above)
      return self.createdependent(type, master)
    counter = NumberCounter(type)
    if self.isroman(type):
      counter.setmode('I')
    return counter

  def getdependentcounter(self, type, master):
    "Get (or create) a counter of the given type that depends on another."
    if not type in self.counters or not self.counters[type].master:
      self.counters[type] = self.createdependent(type, master)
    return self.counters[type]

  def createdependent(self, type, master):
    "Create a dependent counter given the master."
    return DependentCounter(type).setmaster(master)

  def startappendix(self):
    "Start appendices here."
    firsttype = self.orderedlayouts[DocumentParameters.startinglevel]
    counter = self.getcounter(firsttype)
    counter.setmode('A').reset()
    NumberGenerator.appendix = True

class ChapteredGenerator(NumberGenerator):
  "Generate chaptered numbers, as in Chapter.Number."
  "Used in equations, figures: Equation (5.3), figure 8.15."

  def generate(self, type):
    "Generate a number which goes with first-level numbers (chapters). "
    "For the article classes a unique number is generated."
    if DocumentParameters.startinglevel > 0:
      return NumberGenerator.generator.generate(type)
    chapter = self.getcounter('Chapter')
    return self.getdependentcounter(type, chapter).getnext()


NumberGenerator.chaptered = ChapteredGenerator()
NumberGenerator.generator = NumberGenerator()






class Parser(object):
  "A generic parser"

  def __init__(self):
    self.begin = 0
    self.parameters = dict()

  def parseheader(self, reader):
    "Parse the header"
    header = reader.currentline().split()
    reader.nextline()
    self.begin = reader.linenumber
    return header

  def parseparameter(self, reader):
    "Parse a parameter"
    if reader.currentline().strip().startswith('<'):
      key, value = self.parsexml(reader)
      self.parameters[key] = value
      return
    split = reader.currentline().strip().split(' ', 1)
    reader.nextline()
    if len(split) == 0:
      return
    key = split[0]
    if len(split) == 1:
      self.parameters[key] = True
      return
    if not '"' in split[1]:
      self.parameters[key] = split[1].strip()
      return
    doublesplit = split[1].split('"')
    self.parameters[key] = doublesplit[1]

  def parsexml(self, reader):
    "Parse a parameter in xml form: <param attr1=value...>"
    strip = reader.currentline().strip()
    reader.nextline()
    if not strip.endswith('>'):
      Trace.error('XML parameter ' + strip + ' should be <...>')
    split = strip[1:-1].split()
    if len(split) == 0:
      Trace.error('Empty XML parameter <>')
      return None, None
    key = split[0]
    del split[0]
    if len(split) == 0:
      return key, dict()
    attrs = dict()
    for attr in split:
      if not '=' in attr:
        Trace.error('Erroneous attribute for ' + key + ': ' + attr)
        attr += '="0"'
      parts = attr.split('=')
      attrkey = parts[0]
      value = parts[1].split('"')[1]
      attrs[attrkey] = value
    return key, attrs

  def parseending(self, reader, process):
    "Parse until the current ending is found"
    if not self.ending:
      Trace.error('No ending for ' + unicode(self))
      return
    while not reader.currentline().startswith(self.ending):
      process()

  def parsecontainer(self, reader, contents):
    container = self.factory.createcontainer(reader)
    if container:
      container.parent = self.parent
      contents.append(container)

  def __unicode__(self):
    "Return a description"
    return self.__class__.__name__ + ' (' + unicode(self.begin) + ')'

class LoneCommand(Parser):
  "A parser for just one command line"

  def parse(self,reader):
    "Read nothing"
    return []

class TextParser(Parser):
  "A parser for a command and a bit of text"

  stack = []

  def __init__(self, container):
    Parser.__init__(self)
    self.ending = None
    if container.__class__.__name__ in ContainerConfig.endings:
      self.ending = ContainerConfig.endings[container.__class__.__name__]
    self.endings = []

  def parse(self, reader):
    "Parse lines as long as they are text"
    TextParser.stack.append(self.ending)
    self.endings = TextParser.stack + [ContainerConfig.endings['Layout'],
        ContainerConfig.endings['Inset'], self.ending]
    contents = []
    while not self.isending(reader):
      self.parsecontainer(reader, contents)
    return contents

  def isending(self, reader):
    "Check if text is ending"
    current = reader.currentline().split()
    if len(current) == 0:
      return False
    if current[0] in self.endings:
      if current[0] in TextParser.stack:
        TextParser.stack.remove(current[0])
      else:
        TextParser.stack = []
      return True
    return False

class ExcludingParser(Parser):
  "A parser that excludes the final line"

  def parse(self, reader):
    "Parse everything up to (and excluding) the final line"
    contents = []
    self.parseending(reader, lambda: self.parsecontainer(reader, contents))
    return contents

class BoundedParser(ExcludingParser):
  "A parser bound by a final line"

  def parse(self, reader):
    "Parse everything, including the final line"
    contents = ExcludingParser.parse(self, reader)
    # skip last line
    reader.nextline()
    return contents

class BoundedDummy(Parser):
  "A bound parser that ignores everything"

  def parse(self, reader):
    "Parse the contents of the container"
    self.parseending(reader, lambda: reader.nextline())
    # skip last line
    reader.nextline()
    return []

class StringParser(Parser):
  "Parses just a string"

  def parseheader(self, reader):
    "Do nothing, just take note"
    self.begin = reader.linenumber + 1
    return []

  def parse(self, reader):
    "Parse a single line"
    contents = reader.currentline()
    reader.nextline()
    return contents

class InsetParser(BoundedParser):
  "Parses a LyX inset"

  def parse(self, reader):
    "Parse inset parameters into a dictionary"
    startcommand = ContainerConfig.string['startcommand']
    while reader.currentline() != '' and not reader.currentline().startswith(startcommand):
      self.parseparameter(reader)
    return BoundedParser.parse(self, reader)






class ContainerOutput(object):
  "The generic HTML output for a container."

  def gethtml(self, container):
    "Show an error."
    Trace.error('gethtml() not implemented for ' + unicode(self))

  def isempty(self):
    "Decide if the output is empty: by default, not empty."
    return False

class EmptyOutput(ContainerOutput):

  def gethtml(self, container):
    "Return empty HTML code."
    return []

  def isempty(self):
    "This output is particularly empty."
    return True

class FixedOutput(ContainerOutput):
  "Fixed output"

  def gethtml(self, container):
    "Return constant HTML code"
    return container.html

class ContentsOutput(ContainerOutput):
  "Outputs the contents converted to HTML"

  def gethtml(self, container):
    "Return the HTML code"
    html = []
    if container.contents == None:
      return html
    for element in container.contents:
      if not hasattr(element, 'gethtml'):
        Trace.error('No html in ' + element.__class__.__name__ + ': ' + unicode(element))
        return html
      html += element.gethtml()
    return html

class TaggedOutput(ContentsOutput):
  "Outputs an HTML tag surrounding the contents."

  tag = None
  breaklines = False
  empty = False

  def settag(self, tag, breaklines=False, empty=False):
    "Set the value for the tag and other attributes."
    self.tag = tag
    if breaklines:
      self.breaklines = breaklines
    if empty:
      self.empty = empty
    return self

  def setbreaklines(self, breaklines):
    "Set the value for breaklines."
    self.breaklines = breaklines
    return self

  def gethtml(self, container):
    "Return the HTML code."
    if self.empty:
      return [self.selfclosing(container)]
    html = [self.open(container)]
    html += ContentsOutput.gethtml(self, container)
    html.append(self.close(container))
    return html

  def open(self, container):
    "Get opening line."
    if not self.checktag():
      return ''
    open = '<' + self.tag + '>'
    if self.breaklines:
      return open + '\n'
    return open

  def close(self, container):
    "Get closing line."
    if not self.checktag():
      return ''
    close = '</' + self.tag.split()[0] + '>'
    if self.breaklines:
      return '\n' + close + '\n'
    return close

  def selfclosing(self, container):
    "Get self-closing line."
    if not self.checktag():
      return ''
    selfclosing = '<' + self.tag + '/>'
    if self.breaklines:
      return selfclosing + '\n'
    return selfclosing

  def checktag(self):
    "Check that the tag is valid."
    if not self.tag:
      Trace.error('No tag in ' + unicode(container))
      return False
    if self.tag == '':
      return False
    return True

class FilteredOutput(ContentsOutput):
  "Returns the output in the contents, but filtered:"
  "some strings are replaced by others."

  def __init__(self):
    "Initialize the filters."
    self.filters = []

  def addfilter(self, original, replacement):
    "Add a new filter: replace the original by the replacement."
    self.filters.append((original, replacement))

  def gethtml(self, container):
    "Return the HTML code"
    result = []
    html = ContentsOutput.gethtml(self, container)
    for line in html:
      result.append(self.filter(line))
    return result

  def filter(self, line):
    "Filter a single line with all available filters."
    for original, replacement in self.filters:
      if original in line:
        line = line.replace(original, replacement)
    return line

class StringOutput(ContainerOutput):
  "Returns a bare string as output"

  def gethtml(self, container):
    "Return a bare string"
    return [container.string]









class Cloner(object):
  "An object used to clone other objects."

  def clone(cls, original):
    "Return an exact copy of an object."
    "The original object must have an empty constructor."
    return cls.create(original.__class__)

  def create(cls, type):
    "Create an object of a given class."
    clone = type.__new__(type)
    clone.__init__()
    return clone

  clone = classmethod(clone)
  create = classmethod(create)

class ContainerExtractor(object):
  "A class to extract certain containers."

  def __init__(self, config):
    "The config parameter is a map containing three lists: allowed, copied and extracted."
    "Each of the three is a list of class names for containers."
    "Allowed containers are included as is into the result."
    "Cloned containers are cloned and placed into the result."
    "Extracted containers are looked into."
    "All other containers are silently ignored."
    self.allowed = config['allowed']
    self.cloned = config['cloned']
    self.extracted = config['extracted']

  def extract(self, container):
    "Extract a group of selected containers from a container."
    list = []
    locate = lambda c: c.__class__.__name__ in self.allowed + self.cloned
    recursive = lambda c: c.__class__.__name__ in self.extracted
    process = lambda c: self.process(c, list)
    container.recursivesearch(locate, recursive, process)
    return list

  def process(self, container, list):
    "Add allowed containers, clone cloned containers and add the clone."
    name = container.__class__.__name__
    if name in self.allowed:
      list.append(container)
    elif name in self.cloned:
      list.append(self.safeclone(container))
    else:
      Trace.error('Unknown container class ' + name)

  def safeclone(self, container):
    "Return a new container with contents only in a safe list, recursively."
    clone = Cloner.clone(container)
    clone.output = container.output
    clone.contents = self.extract(container)
    return clone






class Position(object):
  "A position in a text to parse"

  def __init__(self):
    self.endinglist = EndingList()

  def checkbytemark(self):
    "Check for a Unicode byte mark and skip it."
    if self.finished():
      return
    if ord(self.current()) == 0xfeff:
      self.skipcurrent()

  def skip(self, string):
    "Skip a string"
    Trace.error('Unimplemented skip()')

  def identifier(self):
    "Return an identifier for the current position."
    Trace.error('Unimplemented identifier()')
    return 'Error'

  def isout(self):
    "Find out if we are out of the position yet."
    Trace.error('Unimplemented isout()')
    return True

  def current(self):
    "Return the current character"
    Trace.error('Unimplemented current()')
    return ''

  def extract(self, length):
    "Extract the next string of the given length, or None if not enough text."
    Trace.error('Unimplemented extract()')
    return None

  def checkfor(self, string):
    "Check for a string at the given position."
    return string == self.extract(len(string))

  def checkforlower(self, string):
    "Check for a string in lower case."
    extracted = self.extract(len(string))
    if not extracted:
      return False
    return string.lower() == self.extract(len(string)).lower()

  def finished(self):
    "Find out if the current formula has finished"
    if self.isout():
      self.endinglist.checkpending()
      return True
    return self.endinglist.checkin(self)

  def skipcurrent(self):
    "Return the current character and skip it."
    current = self.current()
    self.skip(current)
    return current

  def next(self):
    "Advance the position and return the next character."
    self.skipcurrent()
    return self.current()

  def checkskip(self, string):
    "Check for a string at the given position; if there, skip it"
    if not self.checkfor(string):
      return False
    self.skip(string)
    return True

  def glob(self, currentcheck):
    "Glob a bit of text that satisfies a check"
    glob = ''
    while not self.finished() and currentcheck(self.current()):
      glob += self.current()
      self.skip(self.current())
    return glob

  def globalpha(self):
    "Glob a bit of alpha text"
    return self.glob(lambda current: current.isalpha())

  def globnumber(self):
    "Glob a row of digits."
    return self.glob(lambda current: current.isdigit())

  def checkidentifier(self):
    "Check if the current character belongs to an identifier."
    return self.isidentifier(self.current())

  def isidentifier(self, char):
    "Return if the given character is alphanumeric or _."
    if char.isalnum() or char == '_':
      return True
    return False

  def globidentifier(self):
    "Glob alphanumeric and _ symbols."
    return self.glob(lambda current: self.isidentifier(current))

  def skipspace(self):
    "Skip all whitespace at current position"
    return self.glob(lambda current: current.isspace())

  def globincluding(self, magicchar):
    "Glob a bit of text up to (including) the magic char."
    glob = self.glob(lambda current: current != magicchar) + magicchar
    self.skip(magicchar)
    return glob

  def globexcluding(self, magicchar):
    "Glob a bit of text up until (excluding) the magic char."
    return self.glob(lambda current: current != magicchar)

  def pushending(self, ending, optional = False):
    "Push a new ending to the bottom"
    self.endinglist.add(ending, optional)

  def popending(self, expected = None):
    "Pop the ending found at the current position"
    ending = self.endinglist.pop(self)
    if expected and expected != ending:
      Trace.error('Expected ending ' + expected + ', got ' + ending)
    self.skip(ending)
    return ending

  def error(self, message):
    "Show an error message and the position identifier."
    Trace.error(message + ': ' + self.identifier())

class TextPosition(Position):
  "A parse position based on a raw text."

  def __init__(self, text):
    "Create the position from some text."
    Position.__init__(self)
    self.pos = 0
    self.text = text
    self.checkbytemark()

  def skip(self, string):
    "Skip a string of characters."
    self.pos += len(string)

  def identifier(self):
    "Return a sample of the remaining text."
    length = 30
    if self.pos + length > len(self.text):
      length = len(self.text) - self.pos - 1
    return '*' + self.text[self.pos:self.pos + length]

  def isout(self):
    "Find out if we are out of the text yet."
    return self.pos >= len(self.text)

  def current(self):
    "Return the current character, assuming we are not out."
    return self.text[self.pos]

  def extract(self, length):
    "Extract the next string of the given length, or None if not enough text."
    if self.pos + length > len(self.text):
      return None
    return self.text[self.pos : self.pos + length]

class FilePosition(Position):
  "A parse position based on an underlying file."

  def __init__(self, filename):
    "Create the position from a file."
    Position.__init__(self)
    self.reader = LineReader(filename)
    self.number = 1
    self.pos = 0
    self.checkbytemark()

  def skip(self, string):
    "Skip a string of characters."
    length = len(string)
    while self.pos + length > len(self.reader.currentline()):
      length -= len(self.reader.currentline()) - self.pos + 1
      self.nextline()
    self.pos += length

  def nextline(self):
    "Go to the next line."
    self.reader.nextline()
    self.number += 1
    self.pos = 0

  def identifier(self):
    "Return the current line and line number in the file."
    before = self.reader.currentline()[:self.pos - 1]
    after = self.reader.currentline()[self.pos:]
    return 'line ' + unicode(self.number) + ': ' + before + '*' + after

  def isout(self):
    "Find out if we are out of the text yet."
    if self.pos > len(self.reader.currentline()):
      if self.pos > len(self.reader.currentline()) + 1:
        Trace.error('Out of the line ' + self.reader.currentline() + ': ' + unicode(self.pos))
      self.nextline()
    return self.reader.finished()

  def current(self):
    "Return the current character, assuming we are not out."
    if self.pos == len(self.reader.currentline()):
      return '\n'
    if self.pos > len(self.reader.currentline()):
      Trace.error('Out of the line ' + self.reader.currentline() + ': ' + unicode(self.pos))
      return '*'
    return self.reader.currentline()[self.pos]

  def extract(self, length):
    "Extract the next string of the given length, or None if not enough text."
    if self.pos + length > len(self.reader.currentline()):
      return None
    return self.reader.currentline()[self.pos : self.pos + length]

class EndingList(object):
  "A list of position endings"

  def __init__(self):
    self.endings = []

  def add(self, ending, optional):
    "Add a new ending to the list"
    self.endings.append(PositionEnding(ending, optional))

  def checkin(self, pos):
    "Search for an ending"
    if self.findending(pos):
      return True
    return False

  def pop(self, pos):
    "Remove the ending at the current position"
    if pos.isout():
      Trace.error('No ending out of bounds')
      return ''
    ending = self.findending(pos)
    if not ending:
      Trace.error('No ending at ' + pos.current())
      return ''
    for each in reversed(self.endings):
      self.endings.remove(each)
      if each == ending:
        return each.ending
      elif not each.optional:
        Trace.error('Removed non-optional ending ' + each)
    Trace.error('No endings left')
    return ''

  def findending(self, pos):
    "Find the ending at the current position"
    if len(self.endings) == 0:
      return None
    for index, ending in enumerate(reversed(self.endings)):
      if ending.checkin(pos):
        return ending
      if not ending.optional:
        return None
    return None

  def checkpending(self):
    "Check if there are any pending endings"
    if len(self.endings) != 0:
      Trace.error('Pending ' + unicode(self) + ' left open')

  def __unicode__(self):
    "Printable representation"
    string = 'endings ['
    for ending in self.endings:
      string += unicode(ending) + ','
    if len(self.endings) > 0:
      string = string[:-1]
    return string + ']'

class PositionEnding(object):
  "An ending for a parsing position"

  def __init__(self, ending, optional):
    self.ending = ending
    self.optional = optional

  def checkin(self, pos):
    "Check for the ending"
    return pos.checkfor(self.ending)

  def __unicode__(self):
    "Printable representation"
    string = 'Ending ' + self.ending
    if self.optional:
      string += ' (optional)'
    return string



class Container(object):
  "A container for text and objects in a lyx file"

  partkey = None
  parent = None
  begin = None

  def __init__(self):
    self.contents = list()

  def process(self):
    "Process contents"
    pass

  def gethtml(self):
    "Get the resulting HTML"
    html = self.output.gethtml(self)
    if isinstance(html, basestring):
      Trace.error('Raw string ' + html)
      html = [html]
    return self.escapeall(html)

  def escapeall(self, lines):
    "Escape all lines in an array according to the output options."
    result = []
    for line in lines:
      if Options.html:
        line = self.escape(line, EscapeConfig.html)
      if Options.iso885915:
        line = self.escape(line, EscapeConfig.iso885915)
        line = self.escapeentities(line)
      elif not Options.unicode:
        line = self.escape(line, EscapeConfig.nonunicode)
      result.append(line)
    return result

  def escape(self, line, replacements = EscapeConfig.entities):
    "Escape a line with replacements from a map"
    pieces = replacements.keys()
    # do them in order
    pieces.sort()
    for piece in pieces:
      if piece in line:
        line = line.replace(piece, replacements[piece])
    return line

  def escapeentities(self, line):
    "Escape all Unicode characters to HTML entities."
    result = ''
    pos = TextPosition(line)
    while not pos.finished():
      if ord(pos.current()) > 128:
        codepoint = hex(ord(pos.current()))
        if codepoint == '0xd835':
          codepoint = hex(ord(pos.next()) + 0xf800)
        result += '&#' + codepoint[1:] + ';'
      else:
        result += pos.current()
      pos.skipcurrent()
    return result

  def searchall(self, type):
    "Search for all embedded containers of a given type"
    list = []
    self.searchprocess(type, lambda container: list.append(container))
    return list

  def searchremove(self, type):
    "Search for all containers of a type and remove them"
    list = self.searchall(type)
    for container in list:
      container.parent.contents.remove(container)
    return list

  def searchprocess(self, type, process):
    "Search for elements of a given type and process them"
    self.locateprocess(lambda container: isinstance(container, type), process)

  def locateprocess(self, locate, process):
    "Search for all embedded containers and process them"
    for container in self.contents:
      container.locateprocess(locate, process)
      if locate(container):
        process(container)

  def recursivesearch(self, locate, recursive, process):
    "Perform a recursive search in the container."
    for container in self.contents:
      if recursive(container):
        container.recursivesearch(locate, recursive, process)
      if locate(container):
        process(container)

  def extracttext(self):
    "Extract all text from allowed containers."
    result = ''
    constants = ContainerExtractor(ContainerConfig.extracttext).extract(self)
    for constant in constants:
      result += constant.string
    return result

  def group(self, index, group, isingroup):
    "Group some adjoining elements into a group"
    if index >= len(self.contents):
      return
    if hasattr(self.contents[index], 'grouped'):
      return
    while index < len(self.contents) and isingroup(self.contents[index]):
      self.contents[index].grouped = True
      group.contents.append(self.contents[index])
      self.contents.pop(index)
    self.contents.insert(index, group)

  def remove(self, index):
    "Remove a container but leave its contents"
    container = self.contents[index]
    self.contents.pop(index)
    while len(container.contents) > 0:
      self.contents.insert(index, container.contents.pop())

  def tree(self, level = 0):
    "Show in a tree"
    Trace.debug("  " * level + unicode(self))
    for container in self.contents:
      container.tree(level + 1)

  def getparameter(self, name):
    "Get the value of a parameter, if present."
    if not name in self.parameters:
      return None
    return self.parameters[name]

  def getparameterlist(self, name):
    "Get the value of a comma-separated parameter as a list."
    paramtext = self.getparameter(name)
    if not paramtext:
      return []
    return paramtext.split(',')

  def hasemptyoutput(self):
    "Check if the parent's output is empty."
    current = self.parent
    while current:
      if current.output.isempty():
        return True
      current = current.parent
    return False

  def __unicode__(self):
    "Get a description"
    if not self.begin:
      return self.__class__.__name__
    return self.__class__.__name__ + '@' + unicode(self.begin)

class BlackBox(Container):
  "A container that does not output anything"

  def __init__(self):
    self.parser = LoneCommand()
    self.output = EmptyOutput()
    self.contents = []

class LyXFormat(BlackBox):
  "Read the lyxformat command"

  def process(self):
    "Show warning if version < 276"
    version = int(self.header[1])
    if version < 276:
      Trace.error('Warning: unsupported old format version ' + str(version))
    if version > int(GeneralConfig.version['lyxformat']):
      Trace.error('Warning: unsupported new format version ' + str(version))

class StringContainer(Container):
  "A container for a single string"

  parsed = None

  def __init__(self):
    self.parser = StringParser()
    self.output = StringOutput()
    self.string = ''

  def process(self):
    "Replace special chars from the contents."
    if self.parsed:
      self.string = self.replacespecial(self.parsed)
      self.parsed = None

  def replacespecial(self, line):
    "Replace all special chars from a line"
    replaced = self.escape(line, EscapeConfig.entities)
    replaced = self.changeline(replaced)
    if ContainerConfig.string['startcommand'] in replaced and len(replaced) > 1:
      # unprocessed commands
      if self.begin:
        message = 'Unknown command at ' + unicode(self.begin) + ': '
      else:
        message = 'Unknown command: '
      Trace.error(message + replaced.strip())
    return replaced

  def changeline(self, line):
    line = self.escape(line, EscapeConfig.chars)
    if not ContainerConfig.string['startcommand'] in line:
      return line
    line = self.escape(line, EscapeConfig.commands)
    return line

  def extracttext(self):
    "Return all text."
    return self.string
  
  def __unicode__(self):
    "Return a printable representation."
    result = 'StringContainer'
    if self.begin:
      result += '@' + unicode(self.begin)
    ellipsis = '...'
    if len(self.string.strip()) <= 15:
      ellipsis = ''
    return result + ' (' + self.string.strip()[:15] + ellipsis + ')'

class Constant(StringContainer):
  "A constant string"

  def __init__(self, text):
    self.contents = []
    self.string = text
    self.output = StringOutput()

  def __unicode__(self):
    return 'Constant: ' + self.string

class TaggedText(Container):
  "Text inside a tag"

  output = None

  def __init__(self):
    self.parser = TextParser(self)
    self.output = TaggedOutput()

  def complete(self, contents, tag, breaklines=False):
    "Complete the tagged text and return it"
    self.contents = contents
    self.output.tag = tag
    self.output.breaklines = breaklines
    return self

  def constant(self, text, tag, breaklines=False):
    "Complete the tagged text with a constant"
    constant = Constant(text)
    return self.complete([constant], tag, breaklines)

  def __unicode__(self):
    "Return a printable representation."
    if not hasattr(self.output, 'tag'):
      return 'Emtpy tagged text'
    if not self.output.tag:
      return 'Tagged <unknown tag>'
    return 'Tagged <' + self.output.tag + '>'






class ContainerSize(object):
  "The size of a container."

  width = None
  height = None
  maxwidth = None
  maxheight = None
  scale = None

  def set(self, width = None, height = None):
    "Set the proper size with width and height."
    self.setvalue('width', width)
    self.setvalue('height', height)
    return self

  def setmax(self, maxwidth = None, maxheight = None):
    "Set max width and/or height."
    self.setvalue('maxwidth', maxwidth)
    self.setvalue('maxheight', maxheight)
    return self

  def readparameters(self, container):
    "Read some size parameters off a container."
    self.setparameter(container, 'width')
    self.setparameter(container, 'height')
    self.setparameter(container, 'scale')
    self.checkvalidheight(container)
    return self

  def setparameter(self, container, name):
    "Read a size parameter off a container, and set it if present."
    value = container.getparameter(name)
    self.setvalue(name, value)

  def setvalue(self, name, value):
    "Set the value of a parameter name, only if it's valid."
    value = self.processparameter(value)
    if value:
      setattr(self, name, value)

  def checkvalidheight(self, container):
    "Check if the height parameter is valid; otherwise erase it."
    heightspecial = container.getparameter('height_special')
    if self.height and self.extractnumber(self.height) == '1' and heightspecial == 'totalheight':
      self.height = None

  def processparameter(self, value):
    "Do the full processing on a parameter."
    if not value:
      return None
    if self.extractnumber(value) == '0':
      return None
    for ignored in StyleConfig.size['ignoredtexts']:
      if ignored in value:
        value = value.replace(ignored, '')
    return value

  def extractnumber(self, text):
    "Extract the first number in the given text."
    result = ''
    decimal = False
    for char in text:
      if char.isdigit():
        result += char
      elif char == '.' and not decimal:
        result += char
        decimal = True
      else:
        return result
    return result

  def checkimage(self, width, height):
    "Check image dimensions, set them if possible."
    if width:
      self.maxwidth = unicode(width) + 'px'
      if self.scale and not self.width:
        self.width = self.scalevalue(width)
    if height:
      self.maxheight = unicode(height) + 'px'
      if self.scale and not self.height:
        self.height = self.scalevalue(height)
    if self.width and not self.height:
      self.height = 'auto'
    if self.height and not self.width:
      self.width = 'auto'

  def scalevalue(self, value):
    "Scale the value according to the image scale and return it as unicode."
    scaled = value * int(self.scale) / 100
    return unicode(int(scaled)) + 'px'

  def removepercentwidth(self):
    "Remove percent width if present, to set it at the figure level."
    if not self.width:
      return None
    if not '%' in self.width:
      return None
    width = self.width
    self.width = None
    if self.height == 'auto':
      self.height = None
    return width

  def addstyle(self, container):
    "Add the proper style attribute to the output tag."
    if not isinstance(container.output, TaggedOutput):
      Trace.error('No tag to add style, in ' + unicode(container))
    if not self.width and not self.height and not self.maxwidth and not self.maxheight:
      # nothing to see here; move along
      return
    tag = ' style="'
    tag += self.styleparameter('width')
    tag += self.styleparameter('maxwidth')
    tag += self.styleparameter('height')
    tag += self.styleparameter('maxheight')
    if tag[-1] == ' ':
      tag = tag[:-1]
    tag += '"'
    container.output.tag += tag

  def styleparameter(self, name):
    "Get the style for a single parameter."
    value = getattr(self, name)
    if value:
      return name.replace('max', 'max-') + ': ' + value + '; '
    return ''



class QuoteContainer(Container):
  "A container for a pretty quote"

  def __init__(self):
    self.parser = BoundedParser()
    self.output = FixedOutput()

  def process(self):
    "Process contents"
    self.type = self.header[2]
    if not self.type in StyleConfig.quotes:
      Trace.error('Quote type ' + self.type + ' not found')
      self.html = ['"']
      return
    self.html = [StyleConfig.quotes[self.type]]

class LyXLine(Container):
  "A Lyx line"

  def __init__(self):
    self.parser = LoneCommand()
    self.output = FixedOutput()

  def process(self):
    self.html = ['<hr class="line" />']

class EmphaticText(TaggedText):
  "Text with emphatic mode"

  def process(self):
    self.output.tag = 'i'

class ShapedText(TaggedText):
  "Text shaped (italic, slanted)"

  def process(self):
    self.type = self.header[1]
    if not self.type in TagConfig.shaped:
      Trace.error('Unrecognized shape ' + self.header[1])
      self.output.tag = 'span'
      return
    self.output.tag = TagConfig.shaped[self.type]

class VersalitasText(TaggedText):
  "Text in versalitas"

  def process(self):
    self.output.tag = 'span class="versalitas"'

class ColorText(TaggedText):
  "Colored text"

  def process(self):
    self.color = self.header[1]
    self.output.tag = 'span class="' + self.color + '"'

class SizeText(TaggedText):
  "Sized text"

  def process(self):
    self.size = self.header[1]
    self.output.tag = 'span class="' + self.size + '"'

class BoldText(TaggedText):
  "Bold text"

  def process(self):
    self.output.tag = 'b'

class TextFamily(TaggedText):
  "A bit of text from a different family"

  def process(self):
    "Parse the type of family"
    self.type = self.header[1]
    if not self.type in TagConfig.family:
      Trace.error('Unrecognized family ' + type)
      self.output.tag = 'span'
      return
    self.output.tag = TagConfig.family[self.type]

class Hfill(TaggedText):
  "Horizontall fill"

  def process(self):
    self.output.tag = 'span class="hfill"'

class BarredText(TaggedText):
  "Text with a bar somewhere"

  def process(self):
    "Parse the type of bar"
    self.type = self.header[1]
    if not self.type in TagConfig.barred:
      Trace.error('Unknown bar type ' + self.type)
      self.output.tag = 'span'
      return
    self.output.tag = TagConfig.barred[self.type]

class LangLine(BlackBox):
  "A line with language information"

  def process(self):
    self.lang = self.header[1]

class InsetLength(BlackBox):
  "A length measure inside an inset."

  def process(self):
    self.length = self.header[1]

class Space(Container):
  "A space of several types"

  def __init__(self):
    self.parser = InsetParser()
    self.output = FixedOutput()
  
  def process(self):
    self.type = self.header[2]
    if self.type not in StyleConfig.hspaces:
      Trace.error('Unknown space type ' + self.type)
      self.html = [' ']
      return
    self.html = [StyleConfig.hspaces[self.type]]
    length = self.getlength()
    if not length:
      return
    self.output = TaggedOutput().settag('span class="hspace"', False)
    ContainerSize().set(length).addstyle(self)

  def getlength(self):
    "Get the space length from the contents or parameters."
    if len(self.contents) == 0 or not isinstance(self.contents[0], InsetLength):
      return None
    return self.contents[0].length

class VerticalSpace(Container):
  "An inset that contains a vertical space."

  def __init__(self):
    self.parser = InsetParser()
    self.output = FixedOutput()

  def process(self):
    "Set the correct tag"
    self.type = self.header[2]
    if self.type not in StyleConfig.vspaces:
      self.output = TaggedOutput().settag('div class="vspace" style="height: ' + self.type + ';"', True)
      return
    self.html = [StyleConfig.vspaces[self.type]]

class Align(Container):
  "Bit of aligned text"

  def __init__(self):
    self.parser = ExcludingParser()
    self.output = TaggedOutput().setbreaklines(True)

  def process(self):
    self.output.tag = 'div class="' + self.header[1] + '"'

class Newline(Container):
  "A newline"

  def __init__(self):
    self.parser = LoneCommand()
    self.output = FixedOutput()

  def process(self):
    "Process contents"
    self.html = ['<br/>\n']

class NewPage(Newline):
  "A new page"

  def process(self):
    "Process contents"
    self.html = ['<p><br/>\n</p>\n']

class Separator(Container):
  "A separator string which is not extracted by extracttext()."

  def __init__(self, constant):
    self.output = FixedOutput()
    self.contents = []
    self.html = [constant]

class StrikeOut(TaggedText):
  "Striken out text."

  def process(self):
    "Set the output tag to strike."
    self.output.tag = 'strike'

class StartAppendix(BlackBox):
  "Mark to start an appendix here."
  "From this point on, all chapters become appendices."

  def process(self):
    "Activate the special numbering scheme for appendices, using letters."
    NumberGenerator.generator.startappendix()

class ERT(Container):
  "Evil Red Text"

  def __init__(self):
    self.parser = InsetParser()
    self.output = EmptyOutput()






class Link(Container):
  "A link to another part of the document"

  anchor = None
  url = None
  type = None
  page = None
  target = None
  destination = None
  title = None

  def __init__(self):
    "Initialize the link, add target if configured."
    self.contents = []
    self.parser = InsetParser()
    self.output = LinkOutput()
    if Options.target:
      self.target = Options.target

  def complete(self, text, anchor = None, url = None, type = None, title = None):
    "Complete the link."
    self.contents = [Constant(text)]
    if anchor:
      self.anchor = anchor
    if url:
      self.url = url
    if type:
      self.type = type
    if title:
      self.title = title
    return self

  def computedestination(self):
    "Use the destination link to fill in the destination URL."
    if not self.destination:
      return
    self.url = ''
    if self.destination.anchor:
      self.url = '#' + self.destination.anchor
    if self.destination.page:
      self.url = self.destination.page + self.url

  def setmutualdestination(self, destination):
    "Set another link as destination, and set its destination to this one."
    self.destination = destination
    destination.destination = self

  def __unicode__(self):
    "Return a printable representation."
    result = 'Link'
    if self.anchor:
      result += ' #' + self.anchor
    if self.url:
      result += ' to ' + self.url
    return result

class URL(Link):
  "A clickable URL"

  def process(self):
    "Read URL from parameters"
    target = self.escape(self.getparameter('target'))
    self.url = target
    type = self.getparameter('type')
    if type:
      self.url = self.escape(type) + target
    name = self.getparameter('name')
    if not name:
      name = target
    self.contents = [Constant(name)]

class FlexURL(URL):
  "A flexible URL"

  def process(self):
    "Read URL from contents"
    self.url = self.extracttext()

class LinkOutput(ContainerOutput):
  "A link pointing to some destination"
  "Or an anchor (destination)"

  def gethtml(self, link):
    "Get the HTML code for the link"
    type = link.__class__.__name__
    if link.type:
      type = link.type
    tag = 'a class="' + type + '"'
    if link.anchor:
      tag += ' name="' + link.anchor + '"'
    if link.destination:
      link.computedestination()
    if link.url:
      tag += ' href="' + link.url + '"'
    if link.target:
      tag += ' target="' + link.target + '"'
    if link.title:
      tag += ' title="' + link.title + '"'
    return TaggedOutput().settag(tag).gethtml(link)








class Postprocessor(object):
  "Postprocess a container keeping some context"

  stages = []

  def __init__(self):
    self.stages = StageDict(Postprocessor.stages, self)
    self.current = None
    self.last = None

  def postprocess(self, next):
    "Postprocess a container and its contents."
    self.postrecursive(self.current)
    result = self.postcurrent(next)
    self.last = self.current
    self.current = next
    return result

  def postrecursive(self, container):
    "Postprocess the container contents recursively"
    if not hasattr(container, 'contents'):
      return
    if len(container.contents) == 0:
      return
    if hasattr(container, 'postprocess'):
      if not container.postprocess:
        return
    postprocessor = Postprocessor()
    contents = []
    for element in container.contents:
      post = postprocessor.postprocess(element)
      if post:
        contents.append(post)
    # two rounds to empty the pipeline
    for i in range(2):
      post = postprocessor.postprocess(None)
      if post:
        contents.append(post)
    container.contents = contents

  def postcurrent(self, next):
    "Postprocess the current element taking into account next and last."
    stage = self.stages.getstage(self.current)
    if not stage:
      return self.current
    return stage.postprocess(self.last, self.current, next)

class StageDict(object):
  "A dictionary of stages corresponding to classes"

  def __init__(self, classes, postprocessor):
    "Instantiate an element from each class and store as a dictionary"
    instances = self.instantiate(classes, postprocessor)
    self.stagedict = dict([(x.processedclass, x) for x in instances])

  def instantiate(self, classes, postprocessor):
    "Instantiate an element from each class"
    stages = [x.__new__(x) for x in classes]
    for element in stages:
      element.__init__()
      element.postprocessor = postprocessor
    return stages

  def getstage(self, element):
    "Get the stage for a given element, if the type is in the dict"
    if not element.__class__ in self.stagedict:
      return None
    return self.stagedict[element.__class__]



class Label(Link):
  "A label to be referenced"

  names = dict()
  lastlayout = None

  def __init__(self):
    Link.__init__(self)
    self.lastnumbered = None

  def process(self):
    "Process a label container."
    key = self.getparameter('name')
    self.create(' ', key)
    self.lastnumbered = Label.lastlayout

  def create(self, text, key, type = 'Label'):
    "Create the label for a given key."
    self.key = key
    self.complete(text, anchor = key, type = type)
    Label.names[key] = self
    if key in Reference.references:
      for reference in Reference.references[key]:
        reference.destination = self
    return self

  def labelnumber(self):
    "Get the number for the latest numbered container seen."
    numbered = self.numbered(self)
    if numbered and numbered.partkey and numbered.partkey.number:
      return numbered.partkey.number
    return ''

  def numbered(self, container):
    "Get the numbered container for the label."
    if container.partkey:
      return container
    if not container.parent:
      if self.lastnumbered:
        return self.lastnumbered
      return None
    return self.numbered(container.parent)

  def __unicode__(self):
    "Return a printable representation."
    if not hasattr(self, 'key'):
      return 'Unnamed label'
    return 'Label ' + self.key

class Reference(Link):
  "A reference to a label."

  references = dict()
  key = 'none'

  def process(self):
    "Read the reference and set the arrow."
    self.key = self.getparameter('reference')
    if self.key in Label.names:
      self.direction = u'↑'
      label = Label.names[self.key]
    else:
      self.direction = u'↓'
      label = Label().complete(' ', self.key, 'preref')
    self.destination = label
    self.format()
    if not self.key in Reference.references:
      Reference.references[self.key] = []
    Reference.references[self.key].append(self)

  def format(self):
    "Format the reference contents."
    formats = StyleConfig.referenceformats
    formatkey = self.getparameter('LatexCommand')
    if not formatkey:
      formatkey = 'ref'
    if not formatkey in formats:
      Trace.error('Unknown reference format ' + formatkey)
      formatstring = u'↕'
    else:
      formatstring = formats[formatkey]
    formatstring = formatstring.replace(u'↕', self.direction)
    if '@' in formatstring:
      formatstring = formatstring.replace('@', self.destination.labelnumber())
    formatstring = formatstring.replace('#', '1')
    if 'on-page' in formatstring:
      formatstring = formatstring.replace('on-page', Translator.translate('on-page'))
    self.contents = [Constant(formatstring)]

  def __unicode__(self):
    "Return a printable representation."
    return 'Reference ' + self.key















class HeaderParser(Parser):
  "Parses the LyX header"

  def parse(self, reader):
    "Parse header parameters into a dictionary, return the preamble."
    contents = []
    self.parseending(reader, lambda: self.parseline(reader, contents))
    # skip last line
    reader.nextline()
    return contents

  def parseline(self, reader, contents):
    "Parse a single line as a parameter or as a start"
    line = reader.currentline()
    if line.startswith(HeaderConfig.parameters['branch']):
      self.parsebranch(reader)
      return
    elif line.startswith(HeaderConfig.parameters['lstset']):
      LstParser().parselstset(reader)
      return
    elif line.startswith(HeaderConfig.parameters['beginpreamble']):
      contents.append(self.factory.createcontainer(reader))
      return
    # no match
    self.parseparameter(reader)

  def parsebranch(self, reader):
    "Parse all branch definitions."
    branch = reader.currentline().split()[1]
    reader.nextline()
    subparser = HeaderParser().complete(HeaderConfig.parameters['endbranch'])
    subparser.parse(reader)
    options = BranchOptions(branch)
    for key in subparser.parameters:
      options.set(key, subparser.parameters[key])
    Options.branches[branch] = options

  def complete(self, ending):
    "Complete the parser with the given ending."
    self.ending = ending
    return self

class PreambleParser(Parser):
  "A parser for the LyX preamble."

  preamble = []

  def parse(self, reader):
    "Parse the full preamble with all statements."
    self.ending = HeaderConfig.parameters['endpreamble']
    self.parseending(reader, lambda: self.parsepreambleline(reader))
    return []

  def parsepreambleline(self, reader):
    "Parse a single preamble line."
    PreambleParser.preamble.append(reader.currentline())
    reader.nextline()

class LstParser(object):
  "Parse global and local lstparams."

  globalparams = dict()

  def parselstset(self, reader):
    "Parse a declaration of lstparams in lstset."
    paramtext = self.extractlstset(reader)
    if not '{' in paramtext:
      Trace.error('Missing opening bracket in lstset: ' + paramtext)
      return
    lefttext = paramtext.split('{')[1]
    croppedtext = lefttext[:-1]
    LstParser.globalparams = self.parselstparams(croppedtext)

  def extractlstset(self, reader):
    "Extract the global lstset parameters."
    paramtext = ''
    while not reader.finished():
      paramtext += reader.currentline()
      reader.nextline()
      if paramtext.endswith('}'):
        return paramtext
    Trace.error('Could not find end of \\lstset settings; aborting')

  def parsecontainer(self, container):
    "Parse some lstparams from a container."
    container.lstparams = LstParser.globalparams.copy()
    paramlist = container.getparameterlist('lstparams')
    container.lstparams.update(self.parselstparams(paramlist))

  def parselstparams(self, paramlist):
    "Process a number of lstparams from a list."
    paramdict = dict()
    for param in paramlist:
      if not '=' in param:
        if len(param.strip()) > 0:
          Trace.error('Invalid listing parameter ' + param)
      else:
        key, value = param.split('=', 1)
        paramdict[key] = value
    return paramdict





import datetime



import os
import codecs


class BulkFile(object):
  "A file to treat in bulk"

  encodings = ['utf-8','Cp1252']

  def __init__(self, filename):
    self.filename = filename
    self.temp = self.filename + '.temp'

  def readall(self):
    "Read the whole file"
    for encoding in BulkFile.encodings:
      try:
        return self.readcodec(encoding)
      except UnicodeDecodeError:
        pass
    Trace.error('No suitable encoding for ' + self.filename)
    return []

  def readcodec(self, encoding):
    "Read the whole file with the given encoding"
    filein = codecs.open(self.filename, 'rU', encoding)
    lines = filein.readlines()
    result = []
    for line in lines:
      result.append(line.strip('\r\n')) # + '\n')
    filein.close()
    return result

  def getfiles(self):
    "Get reader and writer for a file name"
    reader = LineReader(self.filename)
    writer = LineWriter(self.temp)
    return reader, writer

  def swaptemp(self):
    "Swap the temp file for the original"
    os.chmod(self.temp, os.stat(self.filename).st_mode)
    os.rename(self.temp, self.filename)

  def __unicode__(self):
    "Get the unicode representation"
    return 'file ' + self.filename



class HTMLTemplate(object):
  "A template for HTML generation."

  current = None

  def getheader(self):
    "Get the header (before content) of the template."
    return []

  def convertheader(self):
    "Convert the header and all variables."
    return self.convert(self.getheader())

  def convertfooter(self):
    "Convert the footer and all variables."
    return self.convert(self.getfooter())

  def convert(self, html):
    "Convert a bit of HTML replacing all variables."
    varmap = VariableMap()
    for index, line in enumerate(html):
      if '<!--$' in line:
        html[index] = varmap.replace(line)
    return html

  def getfooter(self):
    "Get the footer (after content) of the template."
    return []

  def get(cls):
    "Choose the right HTML template."
    if not cls.current:
      if Options.raw:
        cls.current = RawTemplate()
      elif Options.template:
        cls.current = FileTemplate().read()
      else:
        cls.current = DefaultTemplate()
    return cls.current

  get = classmethod(get)

class RawTemplate(HTMLTemplate):
  "The template for raw output."

  def getheader(self):
    "Get the raw header."
    return ['<!--starthtml-->\n']

  def getfooter(self):
    "Get the raw footer."
    return ['\n\n<!--endhtml-->']

class FileTemplate(HTMLTemplate):
  "A template read from a file."

  divider = '<!--$content-->'

  def read(self):
    "Read the file, separate header and footer."
    self.header = []
    lines = []
    for line in self.templatelines():
      if FileTemplate.divider == line:
        self.header = lines
        lines = []
      else:
        lines.append(line)
    if self.header == []:
      Trace.error('No ' + FileTemplate.divider + ' in template')
      self.header = lines
      lines = []
    self.footer = lines
    return self

  def templatelines(self):
    "Read all lines in the template, separate content into its own line."
    template = BulkFile(Options.template).readall()
    for line in template:
      if not FileTemplate.divider in line:
        yield line
      else:
        split = line.split(FileTemplate.divider)
        for part in split[:-1]:
          yield part
          yield FileTemplate.divider
        yield split[-1]

  def getheader(self):
    "Return the header (before content)."
    return self.header

  def getfooter(self):
    "Return the footer (after the content)."
    return self.footer

class DefaultTemplate(HTMLTemplate):
  "The default HTML template when not configured."

  def getheader(self):
    "Get the default header (before content)."
    html = []
    if not Options.html:
      html.append(u'<?xml version="1.0" encoding="<!--$encoding-->"?>\n')
      html.append(u'<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n')
      html.append(u'<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">\n')
    else:
      html.append(u'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n')
      html.append(u'<html lang="en">\n')
    html.append(u'<head>\n')
    html.append(u'<meta http-equiv="Content-Type" content="text/html; charset=<!--$encoding-->"/>\n')
    html.append(u'<meta name="generator" content="http://www.nongnu.org/elyxer/"/>\n')
    html.append(u'<meta name="create-date" content="<!--$date-->"/>\n')
    html += self.getcss()
    html.append(u'<title><!--$title--></title>\n')
    if Options.jsmath:
      html.append(u'<script type="text/javascript" src="<!--$jsmath-->/plugins/noImageFonts.js"></script>\n')
      html.append(u'<script type="text/javascript" src="<!--$jsmath-->/easy/load.js"></script>\n')
    if Options.mathjax:
      html.append(u'<script type="text/javascript" src="<!--$mathjax-->/MathJax.js">\n')
      html.append(u'  //  Load MathJax and get it running\n')
      html.append(u'  MathJax.Hub.Config({ jax: ["input/TeX"],\n') # output/HTML-CSS
      html.append(u'  config: ["MMLorHTML.js"],\n')
      html.append(u'  extensions: ["TeX/AMSmath.js","TeX/AMSsymbols.js"],\n')
      html.append(u'  "HTML-CSS": { imageFont: null }\n')
      html.append(u'  });\n')
      html.append(u'</script>\n')
    html.append('</head>\n')
    html.append('<body>\n')
    html.append('<div id="globalWrapper">\n')
    if Options.jsmath or Options.mathjax:
      if Options.mathjax:
        html.append(u'<script type="math/tex">\n')
        html.append(u'\\newcommand{\\lyxlock}{}\n')
        html.append(u'</script>\n')
      html.append(u'<noscript>\n')
      html.append(u'<div class="warning">\n')
      html.append(Translator.translate('jsmath-warning'))
      if Options.jsmath:
        html.append(u'<a href="http://www.math.union.edu/locate/jsMath">jsMath</a>')
      if Options.mathjax:
        html.append(u'<a href="http://www.mathjax.org/">MathJax</a>')
      html.append(Translator.translate('jsmath-requires'))
      html.append(Translator.translate('jsmath-enable') + '\n')
      html.append(u'</div><hr/>\n')
      html.append(u'</noscript>\n')
    return html

  def getcss(self):
    "Get the CSS headers, both linked and embedded."
    html = []
    for cssdoc in Options.css:
      if cssdoc != '':
        html.append(u'<link rel="stylesheet" href="' + cssdoc + '" type="text/css" media="all"/>\n')
    for cssfile in Options.embedcss:
      html.append(u'<style type="text/css">\n')
      html += BulkFile(cssfile).readall()
      html.append(u'</style>\n')
    return html

  def getfooter(self):
    "Get the default footer (after content)."
    html = []
    html.append('\n')
    footer = self.createfooter()
    if len(footer) > 0:
      html.append('<hr class="footer"/>\n')
      html += footer
    html.append('</div>\n')
    html.append('</body>\n')
    html.append('</html>\n')
    return html

  def createfooter(self):
    "Create the footer proper."
    html = []
    if Options.copyright:
      html.append('<div class="footer">\nCopyright (C) <!--$year--> <!--$author-->\n</div>\n')
    if Options.nofooter:
      return html
    html.append('<div class="footer" id="generated-by">\n')
    html.append(Translator.translate('generated-by'))
    html.append('<a href="http://elyxer.nongnu.org/">eLyXer <!--$version--></a>')
    html.append(Translator.translate('generated-on'))
    html.append('<span class="create-date"><!--$datetime--></span>\n')
    html.append('</div>\n')
    return html

class VariableMap(object):
  "A map with all replacement variables."

  def __init__(self):
    self.variables = dict()
    self.variables['title'] = DocumentTitle().getvalue()
    self.variables['author'] = DocumentAuthor().getvalue()
    self.variables['version'] = GeneralConfig.version['number'] + ' (' \
        + GeneralConfig.version['date'] + ')'
    self.variables['year'] = unicode(datetime.date.today().year)
    self.variables['date'] = datetime.date.today().isoformat()
    self.variables['datetime'] = datetime.datetime.now().isoformat()
    self.variables['css'] = Options.css[0]
    if Options.iso885915:
      self.variables['encoding'] = 'ISO-8859-1'
    else:
      self.variables['encoding'] = 'UTF-8'
    if Options.jsmath:
      self.variables['jsmath'] = Options.jsmath
    if Options.mathjax:
      self.variables['mathjax'] = Options.mathjax

  def replace(self, line):
    "Replace all variables in a line."
    result = ''
    pos = TextPosition(line)
    while not pos.finished():
      if pos.checkskip('<!--$'):
        result += self.getvalue(pos)
      else:
        result += pos.skipcurrent()
    return result

  def getvalue(self, pos):
    "Get the value of the variable at the given position."
    value = ''
    key = pos.globalpha()
    if not key in self.variables:
      Trace.error('Template variable ' + key + ' not found')
    else:
      value = self.variables[key]
    if not pos.checkskip('-->'):
      Trace.error('Weird template format in ' + line)
    return value

class DocumentTitle(object):
  "The title of the whole document."

  title = None

  def getvalue(self):
    "Return the correct title from the option or the PDF title."
    if Options.title:
      return Options.title
    if DocumentTitle.title:
      return DocumentTitle.title
    if DocumentParameters.pdftitle:
      return DocumentParameters.pdftitle
    return 'Converted document'

class DocumentAuthor(object):
  "The author of the document."

  author = ''

  def appendauthor(cls, authorline):
    "Append a line with author information."
    cls.author += authorline

  appendauthor = classmethod(appendauthor)

  def getvalue(self):
    "Get the document author."
    return DocumentAuthor.author

class HeaderOutput(ContainerOutput):
  "Returns the HTML headers"

  def gethtml(self, container):
    "Return a constant header"
    return HTMLTemplate.get().convertheader()

class FooterOutput(ContentsOutput):
  "Return the HTML code for the footer"

  def gethtml(self, container):
    "Footer HTML"
    contents = ContentsOutput.gethtml(self, container)
    return contents + HTMLTemplate.get().convertfooter()






class PartKey(object):
  "A key to identify a given document part (chapter, section...)."

  partkey = None
  tocentry = None
  anchortext = None
  number = None
  filename = None
  showtitle = False
  header = False

  def __init__(self):
    self.level = 0

  def createindex(self, partkey):
    "Create a part key for an index page."
    self.partkey = partkey
    self.tocentry = partkey
    self.filename = partkey
    return self

  def createfloat(self, partkey, number):
    "Create a part key for a float."
    self.partkey = partkey
    self.number = number
    self.tocentry = partkey
    self.showtitle = True
    return self

  def createformula(self, number):
    "Create the part key for a formula."
    self.number = number
    self.partkey = 'formula-' + number
    self.tocentry = '(' + number + ')'
    return self

  def createheader(self, headorfooter):
    "Create the part key for a header or footer."
    self.partkey = headorfooter
    self.tocentry = None
    self.header = True
    return self

  def createanchor(self, partkey):
    "Create an anchor for the page."
    self.partkey = partkey
    self.tocentry = partkey
    self.header = True
    return self

  def addtoclabel(self, container):
    "Create the label for the TOC, and add it to the container."
    labeltext = ''
    if self.anchortext:
      labeltext = self.anchortext
      container.contents.insert(0, Separator(u' '))
    label = Label().create(labeltext, self.partkey, type='toc')
    container.contents.insert(0, label)

  def __unicode__(self):
    "Return a printable representation."
    return 'Part key for ' + self.partkey

class LayoutPartKey(PartKey):
  "The part key for a layout."

  generator = NumberGenerator()

  def create(self, layout):
    "Set the layout for which we are creating the part key."
    self.processtype(layout.type)
    return self

  def processtype(self, type):
    "Process the layout type."
    self.level = self.generator.getlevel(type)
    self.number = self.generator.generate(type)
    anchortype = self.getanchortype(type)
    self.partkey = 'toc-' + anchortype + '-' + self.number
    self.tocentry = self.gettocentry(type)
    self.showtitle = True
    self.filename = self.getfilename(type)
    if self.generator.isnumbered(type):
      if not self.tocentry:
        self.tocentry = ''
      else:
        self.tocentry += ' '
      self.tocentry += self.number
      self.anchortext = self.getanchortext(type)

  def getanchortype(self, type):
    "Get the type for the anchor."
    parttype = self.generator.getparttype(type)
    if self.generator.isunordered(type):
      parttype += '-'
    return parttype

  def gettocentry(self, type):
    "Get the entry for the TOC: Chapter, Section..."
    if Options.notoclabels:
      return ''
    return Translator.translate(self.generator.getparttype(type))

  def addtotocentry(self, text):
    "Add some text to the tocentry; create if None."
    if not self.tocentry:
      self.tocentry = ''
    self.tocentry += text

  def getanchortext(self, type):
    "Get the text for the anchor given to a layout type."
    if self.generator.isunique(type):
      return self.tocentry + '.'
    return self.number

  def getfilename(self, type):
    "Get the filename to be used if splitpart is active."
    if self.level == Options.splitpart and self.generator.isnumbered(type):
      return self.number
    if self.level <= Options.splitpart:
      return self.partkey.replace('toc-', '')
    return None

  def needspartkey(self, layout):
    "Find out if a layout needs a part key."
    if self.generator.isunique(layout.type):
      return True
    return self.generator.isinordered(layout.type)

  def __unicode__(self):
    "Get a printable representation."
    return 'Part key for layout ' + self.tocentry

class PartKeyGenerator(object):
  "Number a layout with the relevant attributes."

  partkeyed = []
  layoutpartkey = LayoutPartKey()

  def forlayout(cls, layout):
    "Get the part key for a layout."
    if layout.hasemptyoutput():
      return None
    if not cls.layoutpartkey.needspartkey(layout):
      return None
    Label.lastlayout = layout
    cls.partkeyed.append(layout)
    return LayoutPartKey().create(layout)

  def forindex(cls, index):
    "Get the part key for an index or nomenclature."
    if index.hasemptyoutput():
      return None
    cls.partkeyed.append(index)
    return PartKey().createindex(index.name)

  forlayout = classmethod(forlayout)
  forindex = classmethod(forindex)




import unicodedata








class FormulaParser(Parser):
  "Parses a formula"

  def parseheader(self, reader):
    "See if the formula is inlined"
    self.begin = reader.linenumber + 1
    if reader.currentline().find(FormulaConfig.starts['simple']) > 0:
      return ['inline']
    if reader.currentline().find(FormulaConfig.starts['complex']) > 0:
      return ['block']
    if reader.currentline().find(FormulaConfig.starts['unnumbered']) > 0:
      return ['block']
    return ['numbered']
  
  def parse(self, reader):
    "Parse the formula until the end"
    formula = self.parseformula(reader)
    while not reader.currentline().startswith(self.ending):
      stripped = reader.currentline().strip()
      if len(stripped) > 0:
        Trace.error('Unparsed formula line ' + stripped)
      reader.nextline()
    reader.nextline()
    return formula

  def parseformula(self, reader):
    "Parse the formula contents"
    simple = FormulaConfig.starts['simple']
    if simple in reader.currentline():
      rest = reader.currentline().split(simple, 1)[1]
      if simple in rest:
        # formula is $...$
        return self.parsesingleliner(reader, simple, simple)
      # formula is multiline $...$
      return self.parsemultiliner(reader, simple, simple)
    if FormulaConfig.starts['complex'] in reader.currentline():
      # formula of the form \[...\]
      return self.parsemultiliner(reader, FormulaConfig.starts['complex'],
          FormulaConfig.endings['complex'])
    beginbefore = FormulaConfig.starts['beginbefore']
    beginafter = FormulaConfig.starts['beginafter']
    if beginbefore in reader.currentline():
      if reader.currentline().strip().endswith(beginafter):
        current = reader.currentline().strip()
        endsplit = current.split(beginbefore)[1].split(beginafter)
        startpiece = beginbefore + endsplit[0] + beginafter
        endbefore = FormulaConfig.endings['endbefore']
        endafter = FormulaConfig.endings['endafter']
        endpiece = endbefore + endsplit[0] + endafter
        return startpiece + self.parsemultiliner(reader, startpiece, endpiece) + endpiece
      Trace.error('Missing ' + beginafter + ' in ' + reader.currentline())
      return ''
    begincommand = FormulaConfig.starts['command']
    beginbracket = FormulaConfig.starts['bracket']
    if begincommand in reader.currentline() and beginbracket in reader.currentline():
      endbracket = FormulaConfig.endings['bracket']
      return self.parsemultiliner(reader, beginbracket, endbracket)
    Trace.error('Formula beginning ' + reader.currentline() + ' is unknown')
    return ''

  def parsesingleliner(self, reader, start, ending):
    "Parse a formula in one line"
    line = reader.currentline().strip()
    if not start in line:
      Trace.error('Line ' + line + ' does not contain formula start ' + start)
      return ''
    if not line.endswith(ending):
      Trace.error('Formula ' + line + ' does not end with ' + ending)
      return ''
    index = line.index(start)
    rest = line[index + len(start):-len(ending)]
    reader.nextline()
    return rest

  def parsemultiliner(self, reader, start, ending):
    "Parse a formula in multiple lines"
    formula = ''
    line = reader.currentline()
    if not start in line:
      Trace.error('Line ' + line.strip() + ' does not contain formula start ' + start)
      return ''
    index = line.index(start)
    line = line[index + len(start):].strip()
    while not line.endswith(ending):
      formula += line + '\n'
      reader.nextline()
      line = reader.currentline()
    formula += line[:-len(ending)]
    reader.nextline()
    return formula

class MacroParser(FormulaParser):
  "A parser for a formula macro."

  def parseheader(self, reader):
    "See if the formula is inlined"
    self.begin = reader.linenumber + 1
    return ['inline']
  
  def parse(self, reader):
    "Parse the formula until the end"
    formula = self.parsemultiliner(reader, self.parent.start, self.ending)
    reader.nextline()
    return formula
  








class FormulaBit(Container):
  "A bit of a formula"

  type = None
  original = ''

  def __init__(self):
    "The formula bit type can be 'alpha', 'number', 'font'."
    self.contents = []
    self.output = ContentsOutput()

  def setfactory(self, factory):
    "Set the internal formula factory."
    self.factory = factory
    return self

  def add(self, bit):
    "Add any kind of formula bit already processed"
    self.contents.append(bit)
    self.original += bit.original
    bit.parent = self

  def skiporiginal(self, string, pos):
    "Skip a string and add it to the original formula"
    self.original += string
    if not pos.checkskip(string):
      Trace.error('String ' + string + ' not at ' + pos.identifier())

  def clone(self):
    "Return a copy of itself."
    return self.factory.parseformula(self.original)

  def __unicode__(self):
    "Get a string representation"
    return self.__class__.__name__ + ' read in ' + self.original

class TaggedBit(FormulaBit):
  "A tagged string in a formula"

  def constant(self, constant, tag):
    "Set the constant and the tag"
    self.output = TaggedOutput().settag(tag)
    self.add(FormulaConstant(constant))
    return self

  def complete(self, contents, tag):
    "Set the constant and the tag"
    self.contents = contents
    self.output = TaggedOutput().settag(tag)
    return self

class FormulaConstant(Constant):
  "A constant string in a formula"

  def __init__(self, string):
    "Set the constant string"
    Constant.__init__(self, string)
    self.original = string
    self.type = None

  def clone(self):
    "Return a copy of itself."
    return FormulaConstant(self.original)

  def __unicode__(self):
    "Return a printable representation."
    return 'Formula constant: ' + self.string

class RawText(FormulaBit):
  "A bit of text inside a formula"

  def detect(self, pos):
    "Detect a bit of raw text"
    return pos.current().isalpha()

  def parsebit(self, pos):
    "Parse alphabetic text"
    alpha = pos.globalpha()
    self.add(FormulaConstant(alpha))
    self.type = 'alpha'

class FormulaSymbol(FormulaBit):
  "A symbol inside a formula"

  modified = FormulaConfig.modified
  unmodified = FormulaConfig.unmodified['characters']

  def detect(self, pos):
    "Detect a symbol"
    if pos.current() in FormulaSymbol.unmodified:
      return True
    if pos.current() in FormulaSymbol.modified:
      return True
    return False

  def parsebit(self, pos):
    "Parse the symbol"
    if pos.current() in FormulaSymbol.unmodified:
      self.addsymbol(pos.current(), pos)
      return
    if pos.current() in FormulaSymbol.modified:
      self.addsymbol(FormulaSymbol.modified[pos.current()], pos)
      return
    Trace.error('Symbol ' + pos.current() + ' not found')

  def addsymbol(self, symbol, pos):
    "Add a symbol"
    self.skiporiginal(pos.current(), pos)
    self.contents.append(FormulaConstant(symbol))

class FormulaNumber(FormulaBit):
  "A string of digits in a formula"

  def detect(self, pos):
    "Detect a digit"
    return pos.current().isdigit()

  def parsebit(self, pos):
    "Parse a bunch of digits"
    digits = pos.glob(lambda current: current.isdigit())
    self.add(FormulaConstant(digits))
    self.type = 'number'

class Comment(FormulaBit):
  "A LaTeX comment: % to the end of the line."

  start = FormulaConfig.starts['comment']

  def detect(self, pos):
    "Detect the %."
    return pos.current() == self.start

  def parsebit(self, pos):
    "Parse to the end of the line."
    self.original += pos.globincluding('\n')

class WhiteSpace(FormulaBit):
  "Some white space inside a formula."

  def detect(self, pos):
    "Detect the white space."
    return pos.current().isspace()

  def parsebit(self, pos):
    "Parse all whitespace."
    self.original += pos.skipspace()

  def __unicode__(self):
    "Return a printable representation."
    return 'Whitespace: *' + self.original + '*'

class Bracket(FormulaBit):
  "A {} bracket inside a formula"

  start = FormulaConfig.starts['bracket']
  ending = FormulaConfig.endings['bracket']

  def __init__(self):
    "Create a (possibly literal) new bracket"
    FormulaBit.__init__(self)
    self.inner = None

  def detect(self, pos):
    "Detect the start of a bracket"
    return pos.checkfor(self.start)

  def parsebit(self, pos):
    "Parse the bracket"
    self.parsecomplete(pos, self.innerformula)
    return self

  def parsetext(self, pos):
    "Parse a text bracket"
    self.parsecomplete(pos, self.innertext)
    return self

  def parseliteral(self, pos):
    "Parse a literal bracket"
    self.parsecomplete(pos, self.innerliteral)
    return self

  def parsecomplete(self, pos, innerparser):
    "Parse the start and end marks"
    if not pos.checkfor(self.start):
      Trace.error('Bracket should start with ' + self.start + ' at ' + pos.identifier())
      return None
    self.skiporiginal(self.start, pos)
    pos.pushending(self.ending)
    innerparser(pos)
    self.original += pos.popending(self.ending)

  def innerformula(self, pos):
    "Parse a whole formula inside the bracket"
    while self.factory.detectany(pos):
      self.add(self.factory.parseany(pos))
      for ignored in self.factory.clearignored(pos):
        self.add(ignored)
    if pos.finished():
      return
    if pos.current() != self.ending:
      Trace.error('No formula in bracket at ' + pos.identifier())
    return

  def innertext(self, pos):
    "Parse some text inside the bracket, following textual rules."
    specialchars = FormulaConfig.symbolfunctions.keys()
    specialchars.append(FormulaConfig.starts['command'])
    specialchars.append(FormulaConfig.starts['bracket'])
    specialchars.append(Comment.start)
    while not pos.finished():
      if pos.current() in specialchars:
        if self.factory.detectany(pos):
          self.add(self.factory.parseany(pos))
          if pos.checkskip(' '):
            self.original += ' '
      else:
        self.add(FormulaConstant(pos.skipcurrent()))

  def innerliteral(self, pos):
    "Parse a literal inside the bracket, which does not generate HTML."
    self.literal = ''
    while not pos.current() == self.ending:
      if pos.current() == self.start:
        self.parseliteral(pos)
      else:
        self.literal += pos.skipcurrent()
    self.original += self.literal

class SquareBracket(Bracket):
  "A [] bracket inside a formula"

  start = FormulaConfig.starts['squarebracket']
  ending = FormulaConfig.endings['squarebracket']

  def clone(self):
    "Return a new square bracket with the same contents."
    bracket = SquareBracket()
    bracket.contents = self.contents
    return bracket



class MathsProcessor(object):
  "A processor for a maths construction inside the FormulaProcessor."

  def process(self, contents, index):
    "Process an element inside a formula."
    Trace.error('Unimplemented process() in ' + unicode(self))

  def __unicode__(self):
    "Return a printable description."
    return 'Maths processor ' + self.__class__.__name__

class FormulaProcessor(object):
  "A processor specifically for formulas."

  processors = []

  def process(self, bit):
    "Process the contents of every formula bit, recursively."
    self.processcontents(bit)
    self.processinsides(bit)
    self.traversewhole(bit)

  def processcontents(self, bit):
    "Process the contents of a formula bit."
    if not isinstance(bit, FormulaBit):
      return
    bit.process()
    for element in bit.contents:
      self.processcontents(element)

  def processinsides(self, bit):
    "Process the insides (limits, brackets) in a formula bit."
    if not isinstance(bit, FormulaBit):
      return
    for index, element in enumerate(bit.contents):
      for processor in self.processors:
        processor.process(bit.contents, index)
      # continue with recursive processing
      self.processinsides(element)

  def traversewhole(self, formula):
    "Traverse over the contents to alter variables and space units."
    last = None
    for bit, contents in self.traverse(formula):
      if bit.type == 'alpha':
        self.italicize(bit, contents)
      elif bit.type == 'font' and last and last.type == 'number':
        bit.contents.insert(0, FormulaConstant(u' '))
      last = bit

  def traverse(self, bit):
    "Traverse a formula and yield a flattened structure of (bit, list) pairs."
    for element in bit.contents:
      if hasattr(element, 'type') and element.type:
        yield (element, bit.contents)
      elif isinstance(element, FormulaBit):
        for pair in self.traverse(element):
          yield pair

  def italicize(self, bit, contents):
    "Italicize the given bit of text."
    index = contents.index(bit)
    contents[index] = TaggedBit().complete([bit], 'i')




class Formula(Container):
  "A LaTeX formula"

  def __init__(self):
    self.parser = FormulaParser()
    self.output = TaggedOutput().settag('span class="formula"')

  def process(self):
    "Convert the formula to tags"
    if self.header[0] == 'inline':
      DocumentParameters.displaymode = False
    else:
      DocumentParameters.displaymode = True
      self.output.settag('div class="formula"', True)
    if Options.jsmath:
      if self.header[0] != 'inline':
        self.output = TaggedOutput().settag('div class="math"')
      else:
        self.output = TaggedOutput().settag('span class="math"')
      self.contents = [Constant(self.parsed)]
      return
    if Options.mathjax:
      self.output.tag = 'span class="MathJax_Preview"'
      tag = 'script type="math/tex'
      if self.header[0] != 'inline':
        tag += ';mode=display'
      self.contents = [TaggedText().constant(self.parsed, tag + '"', True)]
      return
    whole = FormulaFactory().parseformula(self.parsed)
    FormulaProcessor().process(whole)
    whole.parent = self
    self.contents = [whole]

  def parse(self, pos):
    "Parse using a parse position instead of self.parser."
    if pos.checkskip('$$'):
      self.parsedollarblock(pos)
    elif pos.checkskip('$'):
      self.parsedollarinline(pos)
    elif pos.checkskip('\\('):
      self.parseinlineto(pos, '\\)')
    elif pos.checkskip('\\['):
      self.parseblockto(pos, '\\]')
    else:
      pos.error('Unparseable formula')
    self.process()
    return self

  def parsedollarinline(self, pos):
    "Parse a $...$ formula."
    self.header = ['inline']
    self.parsedollar(pos)

  def parsedollarblock(self, pos):
    "Parse a $$...$$ formula."
    self.header = ['block']
    self.parsedollar(pos)
    if not pos.checkskip('$'):
      pos.error('Formula should be $$...$$, but last $ is missing.')

  def parsedollar(self, pos):
    "Parse to the next $."
    pos.pushending('$')
    self.parsed = pos.globexcluding('$')
    pos.popending('$')

  def parseinlineto(self, pos, limit):
    "Parse a \\(...\\) formula."
    self.header = ['inline']
    self.parseupto(pos, limit)

  def parseblockto(self, pos, limit):
    "Parse a \\[...\\] formula."
    self.header = ['block']
    self.parseupto(pos, limit)

  def parseupto(self, pos, limit):
    "Parse a formula that ends with the given command."
    pos.pushending(limit)
    self.parsed = pos.glob(lambda current: True)
    pos.popending(limit)

  def __unicode__(self):
    "Return a printable representation."
    if self.partkey and self.partkey.number:
      return 'Formula (' + self.partkey.number + ')'
    return 'Unnumbered formula'

class WholeFormula(FormulaBit):
  "Parse a whole formula"

  def detect(self, pos):
    "Check in the factory"
    return self.factory.detectany(pos)

  def parsebit(self, pos):
    "Parse with any formula bit"
    while self.factory.detectany(pos):
      bit = self.factory.parseany(pos)
      self.add(bit)
      for ignored in self.factory.clearignored(pos):
        self.add(ignored)

class FormulaFactory(object):
  "Construct bits of formula"

  # bit types will be appended later
  types = [FormulaSymbol, RawText, FormulaNumber, Bracket]
  ignoredtypes = [Comment, WhiteSpace]
  defining = False

  def __init__(self):
    "Initialize the map of instances."
    self.instances = dict()

  def detectany(self, pos):
    "Detect if there is a next bit"
    if pos.finished():
      return False
    for type in FormulaFactory.types:
      if self.detecttype(type, pos):
        return True
    return False

  def detecttype(self, type, pos):
    "Detect a bit of a given type."
    self.clearignored(pos)
    if pos.finished():
      return False
    return self.instance(type).detect(pos)

  def instance(self, type):
    "Get an instance of the given type."
    if not type in self.instances or not self.instances[type]:
      self.instances[type] = self.create(type)
    return self.instances[type]

  def create(self, type):
    "Create a new formula bit of the given type."
    return Cloner.create(type).setfactory(self)

  def clearignored(self, pos):
    "Clear all ignored types."
    ignored = []
    while not pos.finished():
      cleared = self.clearany(pos)
      if not cleared:
        return ignored
      ignored.append(cleared)
    return ignored

  def clearany(self, pos):
    "Cleary any ignored type."
    for type in self.ignoredtypes:
      if self.instance(type).detect(pos):
        return self.parsetype(type, pos)
    return None

  def parseany(self, pos):
    "Parse any formula bit at the current location."
    for type in FormulaFactory.types:
      if self.detecttype(type, pos):
        return self.parsetype(type, pos)
    Trace.error('Unrecognized formula at ' + pos.identifier())
    return FormulaConstant(pos.skipcurrent())

  def parsetype(self, type, pos):
    "Parse the given type and return it."
    bit = self.instance(type)
    self.instances[type] = None
    returnedbit = bit.parsebit(pos)
    if returnedbit:
      return returnedbit.setfactory(self)
    return bit

  def parseformula(self, formula):
    "Parse a string of text that contains a whole formula."
    pos = TextPosition(formula)
    whole = self.create(WholeFormula)
    if whole.detect(pos):
      whole.parsebit(pos)
      return whole
    # no formula found
    if not pos.finished():
      Trace.error('Unknown formula at: ' + pos.identifier())
      whole.add(TaggedBit().constant(formula, 'span class="unknown"'))
    return whole



class FormulaCommand(FormulaBit):
  "A LaTeX command inside a formula"

  types = []
  start = FormulaConfig.starts['command']

  def detect(self, pos):
    "Find the current command."
    return pos.checkfor(FormulaCommand.start)

  def parsebit(self, pos):
    "Parse the command."
    command = self.extractcommand(pos)
    bit = self.parsewithcommand(command, pos)
    if bit:
      return bit
    if command.startswith('\\up') or command.startswith('\\Up'):
      upgreek = self.parseupgreek(command, pos)
      if upgreek:
        return upgreek
    if not self.factory.defining:
      Trace.error('Unknown command ' + command)
    self.output = TaggedOutput().settag('span class="unknown"')
    self.add(FormulaConstant(command))
    return None

  def parsewithcommand(self, command, pos):
    "Parse the command type once we have the command."
    for type in FormulaCommand.types:
      if command in type.commandmap:
        return self.parsecommandtype(command, type, pos)
    return None

  def parsecommandtype(self, command, type, pos):
    "Parse a given command type."
    bit = self.factory.create(type)
    bit.setcommand(command)
    bit.parsebit(pos)
    return bit

  def extractcommand(self, pos):
    "Extract the command from the current position."
    if not pos.checkskip(FormulaCommand.start):
      Trace.error('Missing command start ' + start)
      return
    if pos.current().isalpha():
      # alpha command
      command = FormulaCommand.start + pos.globalpha()
      # skip mark of short command
      pos.checkskip('*')
      return command
    # symbol command
    return FormulaCommand.start + pos.skipcurrent()

  def parseupgreek(self, command, pos):
    "Parse the Greek \\up command.."
    if len(command) < 4:
      return None
    if command.startswith('\\up'):
      upcommand = '\\' + command[3:]
    elif pos.checkskip('\\Up'):
      upcommand = '\\' + command[3:4].upper() + command[4:]
    else:
      Trace.error('Impossible upgreek command: ' + command)
      return
    upgreek = self.parsewithcommand(upcommand, pos)
    if upgreek:
      upgreek.type = 'font'
    return upgreek

class CommandBit(FormulaCommand):
  "A formula bit that includes a command"

  def setcommand(self, command):
    "Set the command in the bit"
    self.command = command
    self.original += command
    self.translated = self.commandmap[self.command]
 
  def parseparameter(self, pos):
    "Parse a parameter at the current position"
    if not self.factory.detectany(pos):
      Trace.error('No parameter found at: ' + pos.identifier())
      return None
    parameter = self.factory.parseany(pos)
    self.add(parameter)
    return parameter

  def parsesquare(self, pos):
    "Parse a square bracket"
    if not self.factory.detecttype(SquareBracket, pos):
      return None
    bracket = self.factory.parsetype(SquareBracket, pos)
    self.add(bracket)
    return bracket

  def parseliteral(self, pos):
    "Parse a literal bracket."
    if not self.factory.detecttype(Bracket, pos):
      Trace.error('No literal parameter found at: ' + pos.identifier())
      return None
    bracket = Bracket().setfactory(self.factory)
    self.add(bracket.parseliteral(pos))
    return bracket.literal

  def parsesquareliteral(self, pos):
    "Parse a square bracket literally."
    if not self.factory.detecttype(SquareBracket, pos):
      return None
    bracket = SquareBracket().setfactory(self.factory)
    self.add(bracket.parseliteral(pos))
    return bracket.literal

class EmptyCommand(CommandBit):
  "An empty command (without parameters)"

  commandmap = FormulaConfig.commands

  def parsebit(self, pos):
    "Parse a command without parameters"
    self.contents = [FormulaConstant(self.translated)]

class SpacedCommand(CommandBit):
  "An empty command which should have math spacing in formulas."

  commandmap = FormulaConfig.spacedcommands

  def parsebit(self, pos):
    "Place as contents the command translated and spaced."
    self.contents = [FormulaConstant(u' ' + self.translated + u' ')]

class AlphaCommand(EmptyCommand):
  "A command without paramters whose result is alphabetical"

  commandmap = FormulaConfig.alphacommands

  def parsebit(self, pos):
    "Parse the command and set type to alpha"
    EmptyCommand.parsebit(self, pos)
    self.type = 'alpha'

class OneParamFunction(CommandBit):
  "A function of one parameter"

  commandmap = FormulaConfig.onefunctions
  simplified = False

  def parsebit(self, pos):
    "Parse a function with one parameter"
    self.output = TaggedOutput().settag(self.translated)
    self.parseparameter(pos)
    self.simplifyifpossible()

  def simplifyifpossible(self):
    "Try to simplify to a single character."
    if self.original in self.commandmap:
      self.output = FixedOutput()
      self.html = [self.commandmap[self.original]]
      self.simplified = True

class SymbolFunction(CommandBit):
  "Find a function which is represented by a symbol (like _ or ^)"

  commandmap = FormulaConfig.symbolfunctions

  def detect(self, pos):
    "Find the symbol"
    return pos.current() in SymbolFunction.commandmap

  def parsebit(self, pos):
    "Parse the symbol"
    self.setcommand(pos.current())
    pos.skip(self.command)
    self.output = TaggedOutput().settag(self.translated)
    self.parseparameter(pos)

class TextFunction(CommandBit):
  "A function where parameters are read as text."

  commandmap = FormulaConfig.textfunctions

  def parsebit(self, pos):
    "Parse a text parameter"
    self.output = TaggedOutput().settag(self.translated)
    if not self.factory.detecttype(Bracket, pos):
      Trace.error('No parameter for ' + unicode(self))
    bracket = Bracket().setfactory(self.factory).parsetext(pos)
    self.add(bracket)

  def process(self):
    "Set the type to font"
    self.type = 'font'

class LabelFunction(CommandBit):
  "A function that acts as a label"

  commandmap = FormulaConfig.labelfunctions

  def parsebit(self, pos):
    "Parse a literal parameter"
    self.key = self.parseliteral(pos)

  def process(self):
    "Add an anchor with the label contents."
    self.type = 'font'
    self.label = Label().create(' ', self.key, type = 'eqnumber')
    self.contents = [self.label]
    # store as a Label so we know it's been seen
    Label.names[self.key] = self.label

class FontFunction(OneParamFunction):
  "A function of one parameter that changes the font"

  commandmap = FormulaConfig.fontfunctions

  def process(self):
    "Simplify if possible using a single character."
    self.type = 'font'
    self.simplifyifpossible()

FormulaFactory.types += [FormulaCommand, SymbolFunction]
FormulaCommand.types = [
    AlphaCommand, EmptyCommand, OneParamFunction, FontFunction, LabelFunction,
    TextFunction, SpacedCommand,
    ]









class ParameterDefinition(object):
  "The definition of a parameter in a hybrid function."
  "[] parameters are optional, {} parameters are mandatory."
  "Each parameter has a one-character name, like {$1} or {$p}."
  "A parameter that ends in ! like {$p!} is a literal."
  "Example: [$1]{$p!} reads an optional parameter $1 and a literal mandatory parameter p."

  parambrackets = [('[', ']'), ('{', '}')]

  def __init__(self):
    self.name = None
    self.literal = False
    self.optional = False
    self.value = None
    self.literalvalue = None

  def parse(self, pos):
    "Parse a parameter definition: [$0], {$x}, {$1!}..."
    for (opening, closing) in ParameterDefinition.parambrackets:
      if pos.checkskip(opening):
        if opening == '[':
          self.optional = True
        if not pos.checkskip('$'):
          Trace.error('Wrong parameter name ' + pos.current())
          return None
        self.name = pos.skipcurrent()
        if pos.checkskip('!'):
          self.literal = True
        if not pos.checkskip(closing):
          Trace.error('Wrong parameter closing ' + pos.skipcurrent())
          return None
        return self
    Trace.error('Wrong character in parameter template: ' + pos.skipcurrent())
    return None

  def read(self, pos, function):
    "Read the parameter itself using the definition."
    if self.literal:
      if self.optional:
        self.literalvalue = function.parsesquareliteral(pos)
      else:
        self.literalvalue = function.parseliteral(pos)
      if self.literalvalue:
        self.value = FormulaConstant(self.literalvalue)
    elif self.optional:
      self.value = function.parsesquare(pos)
    else:
      self.value = function.parseparameter(pos)

  def __unicode__(self):
    "Return a printable representation."
    result = 'param ' + self.name
    if self.value:
      result += ': ' + unicode(self.value)
    else:
      result += ' (empty)'
    return result

class ParameterFunction(CommandBit):
  "A function with a variable number of parameters defined in a template."
  "The parameters are defined as a parameter definition."

  def readparams(self, readtemplate, pos):
    "Read the params according to the template."
    self.params = dict()
    for paramdef in self.paramdefs(readtemplate):
      paramdef.read(pos, self)
      self.params['$' + paramdef.name] = paramdef

  def paramdefs(self, readtemplate):
    "Read each param definition in the template"
    pos = TextPosition(readtemplate)
    while not pos.finished():
      paramdef = ParameterDefinition().parse(pos)
      if paramdef:
        yield paramdef

  def getparam(self, name):
    "Get a parameter as parsed."
    if not name in self.params:
      return None
    return self.params[name]

  def getvalue(self, name):
    "Get the value of a parameter."
    return self.getparam(name).value

  def getliteralvalue(self, name):
    "Get the literal value of a parameter."
    param = self.getparam(name)
    if not param or not param.literalvalue:
      return None
    return param.literalvalue

  def getintvalue(self, name):
    "Get the value of a literal parameter as an int."
    value = self.getliteralvalue(name)
    if not value:
      return 0
    return int(value)

class HybridFunction(ParameterFunction):
  """
  A parameter function where the output is also defined using a template.
  The template can use a number of functions; each function has an associated tag.
  Example: [f0{$1},span class="fbox"] defines a function f0 which corresponds to
  a span of class fbox, yielding <span class="fbox">$1</span>.
  Literal parameters can be used in tags definitions: [f0{$1},span style="color: $p;"]
  yields <span style="color: $p;">$1</span>, where $p is a literal parameter.
  """

  commandmap = FormulaConfig.hybridfunctions

  def parsebit(self, pos):
    "Parse a function with [] and {} parameters"
    readtemplate = self.translated[0]
    writetemplate = self.translated[1]
    self.readparams(readtemplate, pos)
    self.contents = self.writeparams(writetemplate)

  def writeparams(self, writetemplate):
    "Write all params according to the template"
    return self.writepos(TextPosition(writetemplate))

  def writepos(self, pos):
    "Write all params as read in the parse position."
    result = []
    while not pos.finished():
      if pos.checkskip('$'):
        param = self.writeparam(pos)
        if param:
          result.append(param)
      elif pos.checkskip('f'):
        function = self.writefunction(pos)
        if function:
          result.append(function)
      else:
        result.append(FormulaConstant(pos.skipcurrent()))
    return result

  def writeparam(self, pos):
    "Write a single param of the form $0, $x..."
    name = '$' + pos.skipcurrent()
    if not name in self.params:
      Trace.error('Unknown parameter ' + name)
      return None
    if not self.params[name]:
      return None
    if pos.checkskip('.'):
      self.params[name].value.type = pos.globalpha()
    return self.params[name].value

  def writefunction(self, pos):
    "Write a single function f0,...,fn."
    tag = self.readtag(pos)
    if not tag:
      return None
    if not pos.checkskip('{'):
      Trace.error('Function should be defined in {}')
      return None
    pos.pushending('}')
    contents = self.writepos(pos)
    pos.popending()
    if len(contents) == 0:
      return None
    function = TaggedBit().complete(contents, tag)
    function.type = None
    return function

  def readtag(self, pos):
    "Get the tag corresponding to the given index. Does parameter substitution."
    if not pos.current().isdigit():
      Trace.error('Function should be f0,...,f9: f' + pos.current())
      return None
    index = int(pos.skipcurrent())
    if 2 + index > len(self.translated):
      Trace.error('Function f' + unicode(index) + ' is not defined')
      return None
    tag = self.translated[2 + index]
    if not '$' in tag:
      return tag
    for variable in self.params:
      if variable in tag:
        param = self.params[variable]
        if not param.literal:
          Trace.error('Parameters in tag ' + tag + ' should be literal: {' + variable + '!}')
          continue
        if param.literalvalue:
          value = param.literalvalue
        else:
          value = ''
        tag = tag.replace(variable, value)
    return tag

FormulaCommand.types += [HybridFunction]



class MathMacro(object):
  "A math macro: command, parameters, default values, definition."

  macros = dict()

  def __init__(self):
    self.newcommand = None
    self.parameternumber = 0
    self.defaults = []
    self.definition = None

  def instantiate(self):
    "Return an instance of the macro."
    return self.definition.clone()

class MacroParameter(FormulaBit):
  "A parameter from a macro."

  def detect(self, pos):
    "Find a macro parameter: #n."
    return pos.checkfor('#')

  def parsebit(self, pos):
    "Parse the parameter: #n."
    if not pos.checkskip('#'):
      Trace.error('Missing parameter start #.')
      return
    self.number = int(pos.skipcurrent())
    self.original = '#' + unicode(self.number)
    self.contents = [TaggedBit().constant('#' + unicode(self.number), 'span class="unknown"')]

class DefiningFunction(ParameterFunction):
  "Read a function that defines a new command (a macro)."

  commandmap = FormulaConfig.definingfunctions

  def parsebit(self, pos):
    "Parse a function with [] and {} parameters."
    if self.factory.detecttype(Bracket, pos):
      newcommand = self.parseliteral(pos)
    elif self.factory.detecttype(FormulaCommand, pos):
      newcommand = self.factory.create(FormulaCommand).extractcommand(pos)
    else:
      Trace.error('Unknown formula bit in defining function at ' + pos.identifier())
      return
    template = self.translated
    self.factory.defining = True
    self.readparams(template, pos)
    self.factory.defining = False
    self.contents = []
    macro = MathMacro()
    macro.newcommand = newcommand
    macro.parameternumber = self.getintvalue('$n')
    Trace.debug('New command ' + newcommand + ' (' + \
        unicode(macro.parameternumber) + ' parameters)')
    macro.definition = self.getvalue('$d')
    self.extractdefaults(macro)
    MathMacro.macros[newcommand] = macro

  def extractdefaults(self, macro):
    "Extract the default values for existing parameters."
    for index in range(9):
      value = self.extractdefault(index + 1)
      if not value:
        return
      macro.defaults.append(value)

  def extractdefault(self, index):
    "Extract the default value for parameter index."
    value = self.getvalue('$' + unicode(index))
    if not value:
      return None
    if len(value.contents) == 0:
      return FormulaConstant('')
    return value

class MacroFunction(CommandBit):
  "A function that was defined using a macro."

  commandmap = MathMacro.macros

  def parsebit(self, pos):
    "Parse a number of input parameters."
    self.output = FilteredOutput()
    self.values = []
    macro = self.translated
    self.parseparameters(pos, macro)
    self.completemacro(macro)

  def parseparameters(self, pos, macro):
    "Parse as many parameters as are needed."
    self.parseoptional(pos, list(macro.defaults))
    self.parsemandatory(pos, macro.parameternumber - len(macro.defaults))
    while self.factory.detecttype(Bracket, pos):
      self.values.append(self.parseparameter(pos))
    remaining = macro.parameternumber - len(self.values)
    if remaining > 0:
      self.parsenumbers(remaining, pos)
    if len(self.values) < macro.parameternumber:
      Trace.error('Missing parameters in macro ' + unicode(self))

  def parseoptional(self, pos, defaults):
    "Parse optional parameters."
    optional = []
    while self.factory.detecttype(SquareBracket, pos):
      optional.append(self.parsesquare(pos))
      if len(optional) > len(defaults):
        break
    for value in optional:
      default = defaults.pop()
      if len(value.contents) > 0:
        self.values.append(value)
      else:
        self.values.append(default)
    self.values += defaults

  def parsemandatory(self, pos, number):
    "Parse a number of mandatory parameters."
    for index in range(number):
      parameter = self.parsemacroparameter(pos, number - index)
      if not parameter:
        return
      self.values.append(parameter)

  def parsemacroparameter(self, pos, remaining):
    "Parse a macro parameter. Could be a bracket or a single letter."
    "If there are just two values remaining and there is a running number,"
    "parse as two separater numbers."
    if pos.finished():
      return None
    if self.factory.detecttype(FormulaNumber, pos):
      return self.parsenumbers(pos, remaining)
    return self.parseparameter(pos)

  def parsenumbers(self, pos, remaining):
    "Parse the remaining parameters as a running number."
    "For example, 12 would be {1}{2}."
    number = self.factory.parsetype(FormulaNumber, pos)
    if not len(number.original) == remaining:
      return number
    for digit in number.original:
      value = self.factory.create(FormulaNumber)
      value.add(FormulaConstant(digit))
      value.type = number
      self.values.append(value)
    return None

  def completemacro(self, macro):
    "Complete the macro with the parameters read."
    self.contents = [macro.instantiate()]
    replaced = [False] * len(self.values)
    for parameter in self.searchall(MacroParameter):
      index = parameter.number - 1
      if index >= len(self.values):
        Trace.error('Macro parameter index out of bounds: ' + unicode(index))
        return
      replaced[index] = True
      parameter.contents = [self.values[index].clone()]
    for index in range(len(self.values)):
      if not replaced[index]:
        self.addfilter(index, self.values[index])

  def addfilter(self, index, value):
    "Add a filter for the given parameter number and parameter value."
    original = '#' + unicode(index + 1)
    value = ''.join(self.values[0].gethtml())
    self.output.addfilter(original, value)

class FormulaMacro(Formula):
  "A math macro defined in an inset."

  def __init__(self):
    self.parser = MacroParser()
    self.output = EmptyOutput()

  def __unicode__(self):
    "Return a printable representation."
    return 'Math macro'

FormulaFactory.types += [ MacroParameter ]

FormulaCommand.types += [
    DefiningFunction, MacroFunction,
    ]






class SideNote(Container):
  "A side note that appears at the right."

  def __init__(self):
    self.parser = InsetParser()
    self.output = TaggedOutput()

  def process(self):
    "Enclose everything in a marginal span."
    self.output.settag('span class="Marginal"', True)

class FootnoteMarker(Container):
  "A marker for a footnote."

  def __init__(self):
    "Set the correct span class."
    self.contents = []
    span = 'span class="SupFootMarker"'
    if Options.alignfoot:
      span = 'span class="AlignFootMarker"'
    self.output = TaggedOutput().settag(span, False)
    mode = 'A'
    if Options.numberfoot:
      mode = '1'
    if Options.symbolfoot:
      mode = '*'
    NumberGenerator.generator.getcounter('Footnote').setmode(mode)

  def create(self):
    "Create the marker for a footnote."
    self.order = NumberGenerator.generator.generate('Footnote')
    if Options.endfoot:
      self.link = Link().complete(self.getmark(), 'footmarker-' + self.order)
    self.createcontents()
    return self

  def createanchor(self, marker):
    "Create the anchor for a footnote. Adds a link for end footnotes."
    self.order = marker.order
    if Options.endfoot:
      self.link = Link().complete(self.getmark(), 'footnote-' + self.order)
      self.link.setmutualdestination(marker.link)
    self.createcontents()
    return self

  def createcontents(self):
    "Create the contents of the marker."
    if Options.endfoot:
      self.contents = [self.link]
    else:
      self.contents = [Constant(self.getmark())]
    space = Constant(u' ')
    self.contents = [space] + self.contents + [space]

  def getmark(self):
    "Get the mark to be displayed in the marker based on the order."
    if Options.symbolfoot:
      return self.order
    else:
      return '[' + self.order + ']'

class Footnote(Container):
  "A footnote to the main text."

  def __init__(self):
    self.parser = InsetParser()
    self.output = TaggedOutput().settag('span class="FootOuter"', False)

  def process(self):
    "Add a counter for the footnote."
    "Can be numeric or a letter depending on runtime options."
    marker = FootnoteMarker().create()
    anchor = FootnoteMarker().createanchor(marker)
    notecontents = [anchor] + list(self.contents)
    self.contents = [marker]
    if Options.hoverfoot:
      self.contents.append(self.createnote(notecontents, 'span class="HoverFoot"'))
    if Options.marginfoot:
      self.contents.append(self.createnote(notecontents, 'span class="MarginFoot"'))
    if Options.endfoot:
      EndFootnotes.footnotes.append(self.createnote(notecontents, 'div class="EndFoot"'))

  def createnote(self, contents, tag):
    "Create a note with the given contents and HTML tag."
    return TaggedText().complete(contents, tag, False)

class EndFootnotes(Container):
  "The collection of footnotes at the document end."

  footnotes = []

  def __init__(self):
    "Generate all footnotes and a proper header for them all."
    self.output = ContentsOutput()
    header = TaggedText().constant(Translator.translate('footnotes'), 'h1 class="index"')
    self.contents = [header] + self.footnotes

class Note(Container):
  "A LyX note of several types"

  def __init__(self):
    self.parser = InsetParser()
    self.output = EmptyOutput()

  def process(self):
    "Hide note and comment, dim greyed out"
    self.type = self.header[2]
    if TagConfig.notes[self.type] == '':
      return
    self.output = TaggedOutput().settag(TagConfig.notes[self.type], True)



class LyXHeader(Container):
  "Reads the header, outputs the HTML header"

  def __init__(self):
    self.contents = []
    self.parser = HeaderParser()
    self.output = HeaderOutput()
    self.parameters = dict()
    self.partkey = PartKey().createheader('header')

  def process(self):
    "Find pdf title"
    DocumentParameters.pdftitle = self.getheaderparameter('pdftitle')
    documentclass = self.getheaderparameter('documentclass')
    if documentclass in HeaderConfig.styles['article']:
      DocumentParameters.startinglevel = 1
    if documentclass in HeaderConfig.styles['book']:
      DocumentParameters.bibliography = 'bibliography'
    else:
      DocumentParameters.bibliography = 'references'
    if self.getheaderparameter('paragraphseparation') == 'indent':
      DocumentParameters.indentstandard = True
    DocumentParameters.tocdepth = self.getlevel('tocdepth')
    DocumentParameters.maxdepth = self.getlevel('secnumdepth')
    DocumentParameters.language = self.getheaderparameter('language')
    if self.getheaderparameter('outputchanges') == 'true':
      DocumentParameters.outputchanges = True
    return self

  def getheaderparameter(self, configparam):
    "Get a parameter configured in HeaderConfig."
    key = HeaderConfig.parameters[configparam]
    if not key in self.parameters:
      return None
    return self.parameters[key]

  def getlevel(self, configparam):
    "Get a level read as a parameter from HeaderConfig."
    paramvalue = self.getheaderparameter(configparam)
    if not paramvalue:
      return 0
    value = int(paramvalue)
    if DocumentParameters.startinglevel == 1:
      return value
    return value + 1

class LyXPreamble(Container):
  "The preamble at the beginning of a LyX file. Parsed for macros."

  def __init__(self):
    self.parser = PreambleParser()
    self.output = EmptyOutput()

  def process(self):
    "Parse the LyX preamble, if needed."
    if len(PreambleParser.preamble) == 0:
      return
    pos = TextPosition('\n'.join(PreambleParser.preamble))
    while not pos.finished():
      if self.detectfunction(pos):
        self.parsefunction(pos)
      else:
        pos.globincluding('\n')
    PreambleParser.preamble = []

  def detectfunction(self, pos):
    "Detect a macro definition or a preamble function."
    for function in FormulaConfig.definingfunctions:
      if pos.checkfor(function):
        return True
    for function in FormulaConfig.preamblefunctions:
      if pos.checkfor(function):
        return True
    return False

  def parsefunction(self, pos):
    "Parse a macro definition or a preamble function."
    command = FormulaFactory().parsetype(FormulaCommand, pos)
    if not isinstance(command, DefiningFunction) and not isinstance(command, PreambleFunction):
      Trace.error('Did not define a macro with ' + unicode(command))

class LyXFooter(Container):
  "Reads the footer, outputs the HTML footer"

  def __init__(self):
    self.contents = []
    self.parser = BoundedDummy()
    self.output = FooterOutput()
    self.partkey = PartKey().createheader('footer')

  def process(self):
    "Include any footnotes at the end."
    if EndFootnotes.footnotes:
      endnotes = EndFootnotes()
      self.contents = [endnotes]

class PreambleFunction(ParameterFunction):
  "A function which is used in the preamble to perform some operation."

  commandmap = FormulaConfig.preamblefunctions

  def parsebit(self, pos):
    "Parse a function with [] and {} parameters."
    template = self.translated[0]
    self.readparams(template, pos)
    operation = self.translated[1]
    operate = getattr(self, operation)
    operate()

  def setcounter(self):
    "Set a global counter."
    counter = self.getliteralvalue('$p')
    value = self.getintvalue('$n')
    Trace.debug('Setting counter ' + unicode(counter) + ' to ' + unicode(value))
    NumberGenerator.generator.getcounter(counter).init(value)

FormulaCommand.types += [PreambleFunction]



class Layout(Container):
  "A layout (block of text) inside a lyx file"

  type = 'none'

  def __init__(self):
    "Initialize the layout."
    self.contents = []
    self.parser = BoundedParser()
    self.output = TaggedOutput().setbreaklines(True)

  def process(self):
    "Get the type and numerate if necessary."
    self.type = self.header[1]
    if self.type in TagConfig.layouts:
      self.output.tag = TagConfig.layouts[self.type] + ' class="' + self.type + '"'
    elif self.type.replace('*', '') in TagConfig.layouts:
      self.output.tag = TagConfig.layouts[self.type.replace('*', '')]
      self.output.tag += ' class="' +  self.type.replace('*', '-') + '"'
    else:
      self.output.tag = 'div class="' + self.type + '"'
    self.numerate()

  def numerate(self):
    "Numerate if necessary."
    partkey = PartKeyGenerator.forlayout(self)
    if partkey:
      self.partkey = partkey
      self.output.tag = self.output.tag.replace('?', unicode(partkey.level))

  def __unicode__(self):
    "Return a printable representation."
    if self.partkey:
      return 'Layout ' + self.type + ' #' + unicode(self.partkey.number)
    return 'Layout of type ' + self.type

class StandardLayout(Layout):
  "A standard layout -- can be a true div or nothing at all"

  indentation = False

  def process(self):
    self.type = 'standard'
    self.output = ContentsOutput()

  def complete(self, contents):
    "Set the contents and return it."
    self.process()
    self.contents = contents
    return self

class Title(Layout):
  "The title of the whole document"

  def process(self):
    self.type = 'title'
    self.output.tag = 'h1 class="title"'
    title = self.extracttext()
    DocumentTitle.title = title
    Trace.message('Title: ' + title)

class Author(Layout):
  "The document author"

  def process(self):
    self.type = 'author'
    self.output.tag = 'h2 class="author"'
    author = self.extracttext()
    Trace.debug('Author: ' + author)
    DocumentAuthor.appendauthor(author)

class Abstract(Layout):
  "A paper abstract"

  done = False

  def process(self):
    self.type = 'abstract'
    self.output.tag = 'div class="abstract"'
    if Abstract.done:
      return
    message = Translator.translate('abstract')
    tagged = TaggedText().constant(message, 'p class="abstract-message"', True)
    self.contents.insert(0, tagged)
    Abstract.done = True

class FirstWorder(Layout):
  "A layout where the first word is extracted"

  def extractfirstword(self):
    "Extract the first word as a list"
    return self.clonecontents(self.contents)

  def clonecontents(self, contents):
    "Extract the first word in contents."
    firstcontents = []
    while len(contents) > 0:
      if self.spaceincontainer(contents[0]):
        cloned = self.clonecontainer(contents[0])
        firstcontents.append(cloned)
        return firstcontents
      firstcontents.append(contents[0])
      del contents[0]
    return firstcontents

  def clonecontainer(self, container):
    "Clone a container including the output."
    if isinstance(container, StringContainer):
      return self.clonestring(container)
    result = Cloner.clone(container)
    result.output = container.output
    result.contents = self.clonecontents(container.contents)
    return result

  def clonestring(self, container):
    "Extract the first word from a string container."
    if not ' ' in container.string:
      Trace.error('No space in string ' + container.string)
      return container
    split = container.string.split(' ', 1)
    container.string = split[1]
    return Constant(split[0])

  def spaceincontainer(self, container):
    "Find out if the container contains a space somewhere."
    return ' ' in container.extracttext()

class Description(FirstWorder):
  "A description layout"

  def process(self):
    "Set the first word to bold"
    self.type = 'Description'
    self.output.tag = 'div class="Description"'
    firstword = self.extractfirstword()
    if not firstword:
      return
    tag = 'span class="Description-entry"'
    self.contents.insert(0, TaggedText().complete(firstword, tag))
    self.contents.insert(1, Constant(u' '))

class List(FirstWorder):
  "A list layout"

  def process(self):
    "Set the first word to bold"
    self.type = 'List'
    self.output.tag = 'div class="List"'
    firstword = self.extractfirstword()
    if not firstword:
      return
    first = TaggedText().complete(firstword, 'span class="List-entry"')
    second = TaggedText().complete(self.contents, 'span class="List-contents"')
    self.contents = [first, second]

class PlainLayout(Layout):
  "A plain layout"

  def process(self):
    "Output just as contents."
    self.output = ContentsOutput()
    self.type = 'Plain'

  def makevisible(self):
    "Make the layout visible, output as tagged text."
    self.output = TaggedOutput().settag('div class="PlainVisible"', True)

class LyXCode(Layout):
  "A bit of LyX-Code."

  def process(self):
    "Output as pre."
    self.output.tag = 'pre class="LyX-Code"'
    for newline in self.searchall(Newline):
      index = newline.parent.contents.index(newline)
      newline.parent.contents[index] = Constant('\n')

class PostLayout(object):
  "Numerate an indexed layout"

  processedclass = Layout

  def postprocess(self, last, layout, next):
    "Group layouts and/or number them."
    if layout.type in TagConfig.group['layouts']:
      return self.group(last, layout)
    if layout.partkey:
      self.number(layout)
    return layout

  def group(self, last, layout):
    "Group two layouts if they are the same type."
    if not self.isgroupable(layout) or not self.isgroupable(last) or last.type != layout.type:
      return layout
    layout.contents = last.contents + [Constant('<br/>\n')] + layout.contents
    last.contents = []
    last.output = EmptyOutput()
    return layout

  def isgroupable(self, container):
    "Check that the container can be grouped."
    if not isinstance(container, Layout):
      return False
    for element in container.contents:
      if not element.__class__.__name__ in LayoutConfig.groupable['allowed']:
        return False
    return True

  def number(self, layout):
    "Generate a number and place it before the text"
    layout.partkey.addtoclabel(layout)

class PostStandard(object):
  "Convert any standard spans in root to divs"

  processedclass = StandardLayout

  def postprocess(self, last, standard, next):
    "Switch to div, and clear if empty."
    type = 'Standard'
    if self.isempty(standard):
      standard.output = EmptyOutput()
      return standard
    if DocumentParameters.indentstandard:
      if isinstance(last, StandardLayout):
        type = 'Indented'
      else:
        type = 'Unindented'
    standard.output = TaggedOutput().settag('div class="' + type + '"', True)
    return standard

  def isempty(self, standard):
    "Find out if the standard layout is empty."
    for element in standard.contents:
      if not element.output.isempty():
        return False
    return True

class PostPlainLayout(PostLayout):
  "Numerate a plain layout"

  processedclass = PlainLayout

  def postprocess(self, last, plain, next):
    "Group plain layouts."
    if not self.istext(last) or not self.istext(plain):
      return plain
    plain.makevisible()
    return self.group(last, plain)

  def istext(self, container):
    "Find out if the container is only text."
    if not isinstance(container, PlainLayout):
      return False
    extractor = ContainerExtractor(TOCConfig.extractplain)
    text = extractor.extract(container)
    return (len(text) > 0)

class PostLyXCode(object):
  "Coalesce contiguous LyX-Code layouts."

  processedclass = LyXCode

  def postprocess(self, last, lyxcode, next):
    "Coalesce if last was also LyXCode"
    if not isinstance(last, LyXCode):
      return lyxcode
    if hasattr(last, 'first'):
      lyxcode.first = last.first
    else:
      lyxcode.first = last
    toappend = lyxcode.first.contents
    toappend.append(Constant('\n'))
    toappend += lyxcode.contents
    lyxcode.output = EmptyOutput()
    return lyxcode

Postprocessor.stages += [
    PostLayout, PostStandard, PostLyXCode, PostPlainLayout
    ]



class BiblioCitation(Container):
  "A complete bibliography citation (possibly with many cites)."

  citations = dict()

  def __init__(self):
    self.parser = InsetParser()
    self.output = TaggedOutput().settag('span class="bibcites"')
    self.contents = []

  def process(self):
    "Process the complete citation and all cites within."
    self.contents = [Constant('[')]
    keys = self.getparameterlist('key')
    for key in keys:
      self.contents += [BiblioCite().create(key), Constant(', ')]
    if len(keys) > 0:
      # remove trailing ,
      self.contents.pop()
    self.contents.append(Constant(']'))

class BiblioCite(Link):
  "Cite of a bibliography entry"

  cites = dict()

  def create(self, key):
    "Create the cite to the given key."
    self.key = key
    number = NumberGenerator.generator.generate('bibliocite')
    ref = BiblioReference().create(key, number)
    self.complete(number, 'cite-' + number, type='bibliocite')
    self.setmutualdestination(ref)
    if not key in BiblioCite.cites:
      BiblioCite.cites[key] = []
    BiblioCite.cites[key].append(self)
    return self

class Bibliography(Container):
  "A bibliography layout containing an entry"

  def __init__(self):
    self.parser = BoundedParser()
    self.output = TaggedOutput().settag('p class="biblio"', True)

class BiblioHeader(Container):
  "The header of the bibliography."

  def __init__(self):
    "Create the header for the bibliography section."
    self.type = 'biblio'
    self.output = ContentsOutput()
    self.name = Translator.translate(DocumentParameters.bibliography)
    self.contents = [TaggedText().constant(self.name, 'h1 class="biblio"', True)]

  def addtotoc(self, parent):
    "Add the bibliography header to the TOC."
    self.parent = parent
    self.partkey = PartKeyGenerator.forindex(self)
    if not self.partkey:
      return
    self.partkey.addtoclabel(self)
    while parent:
      parent.partkey = self.partkey
      parent = parent.parent

class PostBiblio(object):
  "Insert a Bibliography legend before the first item"

  processedclass = Bibliography

  def postprocess(self, last, element, next):
    "If we have the first bibliography insert a tag"
    if isinstance(last, Bibliography) or Options.nobib:
      return element
    layout = StandardLayout()
    header = BiblioHeader()
    header.addtotoc(layout)
    layout.complete([header, element])
    return layout

Postprocessor.stages += [PostBiblio]

class BiblioReference(Link):
  "A reference to a bibliographical entry."

  references = dict()

  def create(self, key, number):
    "Create the reference with the given key and number."
    self.key = key
    self.complete(number, 'biblio-' + number, type='biblioentry')
    if not key in BiblioReference.references:
      BiblioReference.references[key] = []
    BiblioReference.references[key].append(self)
    return self

class BiblioEntry(Container):
  "A bibliography entry"

  entries = dict()

  def __init__(self):
    self.parser = InsetParser()
    self.output = TaggedOutput().settag('span class="entry"')
    self.contents = []

  def process(self):
    "Process the cites for the entry's key"
    self.citeref = [Constant(NumberGenerator.generator.generate('biblioentry'))]
    self.processcites(self.getparameter('key'))

  def processcites(self, key):
    "Get all the cites of the entry"
    self.key = key
    if not key in BiblioReference.references:
      self.contents.append(Constant('[-] '))
      return
    self.contents = [Constant('[')]
    for ref in BiblioReference.references[key]:
      self.contents.append(ref)
      self.contents.append(Constant(','))
    self.contents.pop(-1)
    self.contents.append(Constant('] '))










class Processor(object):
  "Process a container and its contents."

  prestages = []
  skipfiltered = ['LyXHeader', 'LyXFooter', 'Title', 'Author', 'TableOfContents']

  def __init__(self, filtering):
    "Set filtering mode (to skip postprocessing)."
    "With filtering on, the classes in skipfiltered are not processed at all."
    self.filtering = filtering
    self.postprocessor = Postprocessor()

  def process(self, container):
    "Do the whole processing on a container."
    if self.filtering and container.__class__.__name__ in self.skipfiltered:
      return None
    container = self.preprocess(container)
    self.processcontainer(container)
    if not container:
      # do not postprocess empty containers from here
      return container
    return self.postprocess(container)

  def preprocess(self, root):
    "Preprocess a root container with all prestages."
    if not root:
      return None
    for stage in self.prestages:
      root = stage.preprocess(root)
      if not root:
        return None
    return root

  def processcontainer(self, container):
    "Process a container and its contents, recursively."
    if not container:
      return
    for element in container.contents:
      self.processcontainer(element)
    container.process()

  def postprocess(self, container):
    "Postprocess a container, unless filtering is on."
    if self.filtering:
      return container
    return self.postprocessor.postprocess(container)



class ListInset(Container):
  "An inset with a list, normally made of links."

  def __init__(self):
    self.parser = InsetParser()
    self.output = ContentsOutput()

  def sortdictionary(self, dictionary):
    "Sort all entries in the dictionary"
    keys = dictionary.keys()
    # sort by name
    keys.sort()
    return keys

  sortdictionary = classmethod(sortdictionary)

class ListOf(ListInset):
  "A list of entities (figures, tables, algorithms)"

  def process(self):
    "Parse the header and get the type"
    self.type = self.header[2]
    text = Translator.translate('list-' + self.type)
    self.contents = [TaggedText().constant(text, 'div class="tocheader"', True)]

class TableOfContents(ListInset):
  "Table of contents"

  def process(self):
    "Parse the header and get the type"
    self.create(Translator.translate('toc'))

  def create(self, heading):
    "Create a table of contents with the given heading text."
    self.output = TaggedOutput().settag('div class="fulltoc"', True)
    self.contents = [TaggedText().constant(heading, 'div class="tocheader"', True)]
    return self

  def add(self, entry):
    "Add a new entry to the TOC."
    self.contents.append(entry)

class IndexReference(Link):
  "A reference to an entry in the alphabetical index."

  name = 'none'

  def process(self):
    "Put entry in index"
    name = self.getparameter('name')
    if name:
      self.name = name.strip()
    else:
      self.name = self.extracttext()
    IndexEntry.get(self.name).addref(self)

  def __unicode__(self):
    "Return a printable representation."
    return 'Reference to ' + self.name

class IndexHeader(Link):
  "The header line for an index entry. Keeps all arrows."

  keyescapes = {'!':'', '|':'-', ' ':'-', '--':'-', ',':'', '\\':'', '@':'_', u'°':''}

  def create(self, names):
    "Create the header for the given index entry."
    self.output = TaggedOutput().settag('p class="printindex"', True)
    self.name = names[-1]
    keys = [self.escape(part, self.keyescapes) for part in names]
    self.key = '-'.join(keys)
    self.anchor = Link().complete('', 'index-' + self.key, None, 'printindex')
    self.contents = [self.anchor, Constant(self.name + ': ')]
    self.arrows = []
    return self

  def addref(self, reference):
    "Create an arrow pointing to a reference."
    reference.index = unicode(len(self.arrows))
    reference.destination = self.anchor
    reference.complete(u'↓', 'entry-' + self.key + '-' + reference.index)
    arrow = Link().complete(u'↑', type = 'IndexArrow')
    arrow.destination = reference
    if len(self.arrows) > 0:
      self.contents.append(Constant(u', '))
    self.arrows.append(arrow)
    self.contents.append(arrow)

  def __unicode__(self):
    "Return a printable representation."
    return 'Index header for ' + self.name

class IndexGroup(Container):
  "A group of entries in the alphabetical index, for an entry."

  root = None

  def create(self):
    "Create an index group."
    self.entries = dict()
    self.output = EmptyOutput()
    return self

  def findentry(self, names):
    "Find the entry with the given names."
    if self == IndexGroup.root:
      self.output = ContentsOutput()
    else:
      self.output = TaggedOutput().settag('div class="indexgroup"', True)
    lastname = names[-1]
    if not lastname in self.entries:
      self.entries[lastname] = IndexEntry().create(names)
    return self.entries[lastname]

  def sort(self):
    "Sort all entries in the group."
    for key in ListInset.sortdictionary(self.entries):
      entry = self.entries[key]
      entry.group.sort()
      self.contents.append(entry)

  def __unicode__(self):
    "Return a printable representation."
    return 'Index group'

IndexGroup.root = IndexGroup().create()

class IndexEntry(Container):
  "An entry in the alphabetical index."
  "When an index entry is of the form 'part1 ! part2 ...', "
  "a hierarchical structure in the form of an IndexGroup is constructed."
  "An index entry contains a mandatory header, and an optional group."

  def create(self, names):
    "Create an index entry with the given name."
    self.output = ContentsOutput()
    self.header = IndexHeader().create(names)
    self.group = IndexGroup().create()
    self.contents = [self.header, self.group]
    return self

  def addref(self, reference):
    "Add a reference to the entry."
    self.header.addref(reference)

  def get(cls, name):
    "Get the index entry for the given name."
    group = IndexGroup.root
    parts = IndexEntry.splitname(name)
    readparts = []
    for part in parts:
      readparts.append(part)
      entry = group.findentry(readparts)
      group = entry.group
    return entry

  def splitname(cls, name):
    "Split a name in parts divided by !."
    return [part.strip() for part in name.split('!')]

  def __unicode__(self):
    "Return a printable representation."
    return 'Index entry for ' + self.header.name

  get = classmethod(get)
  splitname = classmethod(splitname)

class PrintIndex(ListInset):
  "Command to print an index"

  def process(self):
    "Create the alphabetic index"
    self.name = Translator.translate('index')
    self.partkey = PartKeyGenerator.forindex(self)
    if not self.partkey:
      return
    self.contents = [TaggedText().constant(self.name, 'h1 class="index"')]
    self.partkey.addtoclabel(self)
    IndexGroup.root.sort()
    self.contents.append(IndexGroup.root)

class NomenclatureEntry(Link):
  "An entry of LyX nomenclature"

  entries = dict()

  def process(self):
    "Put entry in index"
    symbol = self.getparameter('symbol')
    description = self.getparameter('description')
    key = symbol.replace(' ', '-').lower()
    if key in NomenclatureEntry.entries:
      Trace.error('Duplicated nomenclature entry ' + key)
    self.complete(u'↓', 'noment-' + key)
    entry = Link().complete(u'↑', 'nom-' + key)
    entry.symbol = symbol
    entry.description = description
    self.setmutualdestination(entry)
    NomenclatureEntry.entries[key] = entry

class PrintNomenclature(ListInset):
  "Print all nomenclature entries"

  def process(self):
    "Create the nomenclature."
    self.name = Translator.translate('nomenclature')
    self.partkey = PartKeyGenerator.forindex(self)
    if not self.partkey:
      return
    self.contents = [TaggedText().constant(self.name, 'h1 class="nomenclature"')]
    self.partkey.addtoclabel(self)
    for key in self.sortdictionary(NomenclatureEntry.entries):
      entry = NomenclatureEntry.entries[key]
      contents = [entry, Constant(entry.symbol + u' ' + entry.description)]
      text = TaggedText().complete(contents, 'div class="Nomenclated"', True)
      self.contents.append(text)

class PreListInset(object):
  "Preprocess any container that contains a list inset."

  def preprocess(self, container):
    "Preprocess a container, extract any list inset and return it."
    listinsets = container.searchall(ListInset)
    if len(listinsets) == 0:
      return container
    if len(container.contents) > 1:
      return container
    return listinsets[0]

Processor.prestages += [PreListInset()]









class TableParser(BoundedParser):
  "Parse the whole table"

  headers = ContainerConfig.table['headers']

  def __init__(self):
    BoundedParser.__init__(self)
    self.columns = list()

  def parseheader(self, reader):
    "Parse table headers"
    reader.nextline()
    while self.startswithheader(reader):
      self.parseparameter(reader)
    return []

  def startswithheader(self, reader):
    "Check if the current line starts with a header line"
    for start in TableParser.headers:
      if reader.currentline().strip().startswith(start):
        return True
    return False

class TablePartParser(BoundedParser):
  "Parse a table part (row or cell)"

  def parseheader(self, reader):
    "Parse the header"
    tablekey, parameters = self.parsexml(reader)
    self.parameters = parameters
    return list()

class ColumnParser(LoneCommand):
  "Parse column properties"

  def parseheader(self, reader):
    "Parse the column definition"
    key, parameters = self.parsexml(reader)
    self.parameters = parameters
    return []



class Table(Container):
  "A lyx table"

  def __init__(self):
    self.parser = TableParser()
    self.output = TaggedOutput().settag('table', True)
    self.columns = []

  def process(self):
    "Set the columns on every row"
    index = 0
    while index < len(self.contents):
      element = self.contents[index]
      if isinstance(element, Column):
        self.columns.append(element)
        del self.contents[index]
      elif isinstance(element, BlackBox):
        del self.contents[index]
      elif isinstance(element, Row):
        element.setcolumns(self.columns)
        index += 1
      else:
        Trace.error('Unknown element type ' + element.__class__.__name__ +
            ' in table: ' + unicode(element.contents[0]))
        index += 1

class Row(Container):
  "A row in a table"

  def __init__(self):
    self.parser = TablePartParser()
    self.output = TaggedOutput().settag('tr', True)
    self.columns = list()

  def setcolumns(self, columns):
    "Process alignments for every column"
    if len(columns) != len(self.contents):
      Trace.error('Columns: ' + unicode(len(columns)) + ', cells: ' + unicode(len(self.contents)))
      return
    for index, cell in enumerate(self.contents):
      columns[index].set(cell)

class Column(Container):
  "A column definition in a table"

  def __init__(self):
    self.parser = ColumnParser()
    self.output = EmptyOutput()

  def process(self):
    "Read size parameters if present."
    self.size = ContainerSize().readparameters(self)

  def set(self, cell):
    "Set alignments in the corresponding cell"
    alignment = self.getparameter('alignment')
    if alignment == 'block':
      alignment = 'justify'
    cell.setattribute('align', alignment)
    valignment = self.getparameter('valignment')
    cell.setattribute('valign', valignment)
    self.size.addstyle(cell)

class Cell(Container):
  "A cell in a table"

  def __init__(self):
    self.parser = TablePartParser()
    self.output = TaggedOutput().settag('td', True)

  def setmulticolumn(self, span):
    "Set the cell as multicolumn"
    self.setattribute('colspan', span)

  def setattribute(self, attribute, value):
    "Set a cell attribute in the tag"
    self.output.tag += ' ' + attribute + '="' + unicode(value) + '"'

class PostTable(object):
  "Postprocess a table"

  processedclass = Table

  def postprocess(self, last, table, next):
    "Postprocess a table: long table, multicolumn rows"
    self.longtable(table)
    for row in table.contents:
      index = 0
      while index < len(row.contents):
        self.checkforplain(row, index)
        self.checkmulticolumn(row, index)
        index += 1
    return table

  def longtable(self, table):
    "Postprocess a long table, removing unwanted rows"
    features = table.getparameter('features')
    if not features:
      return
    if not 'islongtable' in features:
      return
    if features['islongtable'] != 'true':
      return
    if self.hasrow(table, 'endfirsthead'):
      self.removerows(table, 'endhead')
    if self.hasrow(table, 'endlastfoot'):
      self.removerows(table, 'endfoot')

  def hasrow(self, table, attrname):
    "Find out if the table has a row of first heads"
    for row in table.contents:
      if row.getparameter(attrname):
        return True
    return False

  def removerows(self, table, attrname):
    "Remove the head rows, since the table has first head rows."
    for row in table.contents:
      if row.getparameter(attrname):
        row.output = EmptyOutput()

  def checkforplain(self, row, index):
    "Make plain layouts visible if necessary."
    cell = row.contents[index]
    plainlayouts = cell.searchall(PlainLayout)
    if len(plainlayouts) <= 1:
      return
    for plain in plainlayouts:
      plain.makevisible()

  def checkmulticolumn(self, row, index):
    "Process a multicolumn attribute"
    cell = row.contents[index]
    mc = cell.getparameter('multicolumn')
    if not mc:
      return
    if mc != '1':
      Trace.error('Unprocessed multicolumn=' + unicode(multicolumn) +
          ' cell ' + unicode(cell))
      return
    total = 1
    index += 1
    while self.checkbounds(row, index):
      del row.contents[index]
      total += 1
    cell.setmulticolumn(total)

  def checkbounds(self, row, index):
    "Check if the index is within bounds for the row"
    if index >= len(row.contents):
      return False
    mc = row.contents[index].getparameter('multicolumn')
    if mc != '2':
      return False
    return True

Postprocessor.stages.append(PostTable)




import struct
import sys
import os
import shutil



import os
import os.path
import codecs


class Path(object):
  "Represents a generic path"

  def exists(self):
    "Check if the file exists"
    return os.path.exists(self.path)

  def open(self):
    "Open the file as readonly binary"
    return codecs.open(self.path, 'rb')

  def getmtime(self):
    "Return last modification time"
    return os.path.getmtime(self.path)

  def hasexts(self, exts):
    "Check if the file has one of the given extensions."
    for ext in exts:
      if self.hasext(ext):
        return True
    return False

  def hasext(self, ext):
    "Check if the file has the given extension"
    return self.getext() == ext

  def getext(self):
    "Get the current extension of the file."
    base, ext = os.path.splitext(self.path)
    return ext

  def __unicode__(self):
    "Return a unicode string representation"
    return self.path

  def __eq__(self, path):
    "Compare to another path"
    if not hasattr(path, 'path'):
      return False
    return self.path == path.path

class InputPath(Path):
  "Represents an input file"

  def __init__(self, url):
    "Create the input path based on url"
    self.url = url
    self.path = url
    if not os.path.isabs(url):
      self.path = os.path.join(Options.directory, url)

class OutputPath(Path):
  "Represents an output file"

  def __init__(self, inputpath):
    "Create the output path based on an input path"
    self.url = inputpath.url
    if os.path.isabs(self.url):
      self.url = os.path.basename(self.url)
    self.path = os.path.join(Options.destdirectory, self.url)
  
  def changeext(self, ext):
    "Change extension to the given one"
    base, oldext = os.path.splitext(self.path)
    self.path = base + ext
    base, oldext = os.path.splitext(self.url)
    self.url = base + ext

  def exists(self):
    "Check if the file exists"
    return os.path.exists(self.path)

  def createdirs(self):
    "Create any intermediate directories that don't exist"
    dir = os.path.dirname(self.path)
    if len(dir) > 0 and not os.path.exists(dir):
      os.makedirs(dir)

  def removebackdirs(self):
    "Remove any occurrences of ../ (or ..\ on Windows)"
    self.path = os.path.normpath(self.path)
    backdir = '..' + os.path.sep
    while self.path.startswith(backdir):
      Trace.debug('Backdir in: ' + self.path)
      self.path = self.path[len(backdir):]
    while self.url.startswith('../'):
      Trace.debug('Backdir in: ' + self.url)
      self.url = self.url[len('../'):]



class Image(Container):
  "An embedded image"

  defaultformat = ImageConfig.formats['default']
  size = None
  copy = None

  def __init__(self):
    self.parser = InsetParser()
    self.output = TaggedOutput()
    self.type = 'embedded'

  def process(self):
    "Place the url, convert the image if necessary."
    self.origin = InputPath(self.getparameter('filename'))
    self.destination = self.getdestination(self.origin)
    self.size = ContainerSize().readparameters(self)
    if self.origin.exists():
      ImageConverter.instance.convert(self)
    else:
      Trace.error('Image ' + unicode(self.origin) + ' not found')
    self.setsize()
    self.settag()

  def getdestination(self, origin):
    "Convert origin path to destination path."
    "Changes extension of destination to output image format."
    destination = OutputPath(origin)
    if Options.noconvert:
      return destination
    self.convertformat(destination)
    destination.removebackdirs()
    return destination

  def convertformat(self, destination):
    "Convert the format of the destination image."
    if Options.copyimages:
      return
    imageformat = '.jpg'
    forcedest = Image.defaultformat
    if Options.imageformat:
      imageformat = Options.imageformat
      forcedest = Options.imageformat
    if not destination.hasext(imageformat):
      destination.changeext(forcedest)

  def setsize(self):
    "Set the size attributes width and height."
    width, height = ImageFile(self.destination).getdimensions()
    self.size.checkimage(width, height)

  def scalevalue(self, value):
    "Scale the value according to the image scale and return it as unicode."
    scaled = value * int(self.size.scale) / 100
    return unicode(int(scaled)) + 'px'

  def settag(self):
    "Set the output tag for the image."
    tag = 'img class="' + self.type + '"'
    if self.origin.exists():
      url = self.destination.url
    else:
      url = self.origin.url
    alt = Translator.translate('figure') + ' ' + url
    tag += ' src="' + url + '" alt="' + alt + '"'
    emptytag = True
    if self.destination.hasext('.svg'):
      self.contents = [Constant(alt)]
      tag = 'object class="' + self.type + '" data="' + url + '"'
      emptytag = False
    self.output.settag(tag, True, empty=emptytag)
    self.size.addstyle(self)

class ImageConverter(object):
  "A converter from one image file to another."

  vectorformats = ImageConfig.formats['vector']
  cropboxformats = ImageConfig.cropboxformats

  active = True
  instance = None

  def convert(self, image):
    "Convert an image to PNG"
    if not ImageConverter.active or Options.noconvert:
      return
    if image.origin.path == image.destination.path:
      return
    if image.destination.exists():
      if image.origin.getmtime() <= image.destination.getmtime():
        # file has not changed; do not convert
        return
    image.destination.createdirs()
    if Options.copyimages:
      Trace.debug('Copying ' + image.origin.path + ' to ' + image.destination.path)
      shutil.copy2(image.origin.path, image.destination.path)
      return
    converter, command = self.buildcommand(image)
    try:
      Trace.debug(converter + ' command: "' + command + '"')
      result = os.system(command.encode(sys.getfilesystemencoding()))
      if result != 0:
        Trace.error(converter + ' not installed; images will not be processed')
        ImageConverter.active = False
        return
      Trace.message('Converted ' + unicode(image.origin) + ' to ' +
          unicode(image.destination))
    except OSError, exception:
      Trace.error('Error while converting image ' + unicode(image.origin)
          + ': ' + unicode(exception))

  def buildcommand(self, image):
    "Build the command to convert the image."
    if not Options.converter in ImageConfig.converters:
      Trace.error('Converter ' + Options.converter + ' not configured.')
      ImageConverter.active = False
      return ''
    command = ImageConfig.converters[Options.converter]
    params = self.getparams(image)
    for param in params:
      command = command.replace('$' + param, unicode(params[param]))
    # remove unwanted options
    while '[' in command and ']' in command:
      command = self.removeparam(command)
    return Options.converter, command

  def removeparam(self, command):
    "Remove an unwanted param."
    if command.index('[') > command.index(']'):
      Trace.error('Converter command should be [...$...]: ' + command)
      exit()
    before = command[:command.index('[')]
    after = command[command.index(']') + 1:]
    between = command[command.index('[') + 1:command.index(']')]
    if '$' in between:
      return before + after
    return before + between + after

  def getparams(self, image):
    "Get the parameters for ImageMagick conversion"
    params = dict()
    params['input'] = image.origin
    params['output'] = image.destination
    if image.origin.hasexts(self.vectorformats):
      scale = 100
      if image.size.scale:
        scale = image.size.scale
        # descale
        image.size.scale = None
      params['scale'] = scale
    if image.origin.getext() in self.cropboxformats:
      params['format'] = self.cropboxformats[image.origin.getext()]
    return params

ImageConverter.instance = ImageConverter()

class ImageFile(object):
  "A file corresponding to an image (JPG or PNG)"

  dimensions = dict()

  def __init__(self, path):
    "Create the file based on its path"
    self.path = path

  def getdimensions(self):
    "Get the dimensions of a JPG or PNG image"
    if not self.path.exists():
      return None, None
    if unicode(self.path) in ImageFile.dimensions:
      return ImageFile.dimensions[unicode(self.path)]
    dimensions = (None, None)
    if self.path.hasext('.png'):
      dimensions = self.getpngdimensions()
    elif self.path.hasext('.jpg'):
      dimensions = self.getjpgdimensions()
    elif self.path.hasext('.svg'):
      dimensions = self.getsvgdimensions()
    ImageFile.dimensions[unicode(self.path)] = dimensions
    return dimensions

  def getpngdimensions(self):
    "Get the dimensions of a PNG image"
    pngfile = self.path.open()
    pngfile.seek(16)
    width = self.readlong(pngfile)
    height = self.readlong(pngfile)
    pngfile.close()
    return (width, height)

  def getjpgdimensions(self):
    "Get the dimensions of a JPEG image"
    jpgfile = self.path.open()
    start = self.readword(jpgfile)
    if start != int('ffd8', 16):
      Trace.error(unicode(self.path) + ' not a JPEG file')
      return (None, None)
    self.skipheaders(jpgfile, ['ffc0', 'ffc2'])
    self.seek(jpgfile, 3)
    height = self.readword(jpgfile)
    width = self.readword(jpgfile)
    jpgfile.close()
    return (width, height)

  def getsvgdimensions(self):
    "Get the dimensions of a SVG image."
    return (None, None)

  def skipheaders(self, file, hexvalues):
    "Skip JPEG headers until one of the parameter headers is found"
    headervalues = [int(value, 16) for value in hexvalues]
    header = self.readword(file)
    safetycounter = 0
    while header not in headervalues and safetycounter < 30:
      length = self.readword(file)
      if length == 0:
        Trace.error('End of file ' + file.name)
        return
      self.seek(file, length - 2)
      header = self.readword(file)
      safetycounter += 1

  def readlong(self, file):
    "Read a long (32-bit) value from file"
    return self.readformat(file, '>L', 4)

  def readword(self, file):
    "Read a 16-bit value from file"
    return self.readformat(file, '>H', 2)

  def readformat(self, file, format, bytes):
    "Read any format from file"
    read = file.read(bytes)
    if read == '':
      Trace.error('EOF reached')
      return 0
    tuple = struct.unpack(format, read)
    return tuple[0]

  def seek(self, file, bytes):
    "Seek forward, just by reading the given number of bytes"
    file.read(bytes)






class ListItem(Container):
  "An element in a list"

  type = 'none'

  def __init__(self):
    "Create a list item."
    self.parser = BoundedParser()
    self.output = ContentsOutput()

  def process(self):
    "Set the correct type and contents."
    self.type = self.header[1]
    tag = TaggedText().complete(self.contents, 'li', True)
    self.contents = [tag]

  def __unicode__(self):
    return self.type + ' item @ ' + unicode(self.begin)

class DeeperList(Container):
  "A nested list"

  def __init__(self):
    "Create a nested list element."
    self.parser = BoundedParser()
    self.output = ContentsOutput()
    self.contents = []

  def process(self):
    "Create the deeper list"
    if len(self.contents) == 0:
      Trace.error('Empty deeper list')
      return

  def __unicode__(self):
    result = 'deeper list @ ' + unicode(self.begin) + ': ['
    for element in self.contents:
      result += unicode(element) + ', '
    return result[:-2] + ']'

class PendingList(object):
  "A pending list"

  def __init__(self):
    self.contents = []
    self.type = None

  def additem(self, item):
    "Add a list item"
    self.contents += item.contents
    if not self.type:
      self.type = item.type

  def adddeeper(self, deeper):
    "Add a deeper list item"
    if self.empty():
      self.insertfake()
    self.contents[-1].contents += deeper.contents

  def generate(self):
    "Get the resulting list"
    if not self.type:
      tag = 'ul'
    else:
      tag = TagConfig.listitems[self.type]
    text = TaggedText().complete(self.contents, tag, True)
    self.__init__()
    return text

  def isduewithitem(self, item):
    "Decide whether the pending list must be generated before the given item"
    if not self.type:
      return False
    if self.type != item.type:
      return True
    return False

  def isduewithnext(self, next):
    "Applies only if the list is finished with next item."
    if not next:
      return True
    if not isinstance(next, ListItem) and not isinstance(next, DeeperList):
      return True
    return False

  def empty(self):
    return len(self.contents) == 0

  def insertfake(self):
    "Insert a fake item"
    item = TaggedText().constant('', 'li class="nested"', True)
    self.contents = [item]
    self.type = 'Itemize'

  def __unicode__(self):
    result = 'pending ' + unicode(self.type) + ': ['
    for element in self.contents:
      result += unicode(element) + ', '
    if len(self.contents) > 0:
      result = result[:-2]
    return result + ']'

class PostListItem(object):
  "Postprocess a list item"

  processedclass = ListItem

  def postprocess(self, last, item, next):
    "Add the item to pending and return an empty item"
    if not hasattr(self.postprocessor, 'list'):
      self.postprocessor.list = PendingList()
    self.postprocessor.list.additem(item)
    if self.postprocessor.list.isduewithnext(next):
      return self.postprocessor.list.generate()
    if isinstance(next, ListItem) and self.postprocessor.list.isduewithitem(next):
      return self.postprocessor.list.generate()
    return BlackBox()

class PostDeeperList(object):
  "Postprocess a deeper list"

  processedclass = DeeperList

  def postprocess(self, last, deeper, next):
    "Append to the list in the postprocessor"
    if not hasattr(self.postprocessor, 'list'):
      self.postprocessor.list = PendingList()
    self.postprocessor.list.adddeeper(deeper)
    if self.postprocessor.list.isduewithnext(next):
      return self.postprocessor.list.generate()
    return BlackBox()

Postprocessor.stages += [PostListItem, PostDeeperList]









class Float(Container):
  "A floating inset"

  type = 'none'

  def __init__(self):
    self.parser = InsetParser()
    self.output = TaggedOutput().settag('div class="float"', True)

  def process(self):
    "Get the float type."
    self.type = self.header[2]
    self.processnumber()
    self.processfloats()
    self.processtags()

  def isparent(self):
    "Find out whether the float is the parent float or is contained in another float."
    current = self.parent
    while current:
      if isinstance(current, Float):
        return False
      current = current.parent
    return True

  def processnumber(self):
    "Number a float if it isn't numbered."
    if not self.isparent():
      # do nothing; parent will take care of numbering
      return
    number = NumberGenerator.chaptered.generate(self.type)
    entry = number
    if not Options.notoclabels:
      entry = Translator.translate('float-' + self.type) + entry
    self.partkey = PartKey().createfloat(entry, number)

  def processtags(self):
    "Process the HTML tags."
    tagged = self.embed()
    self.applywideningtag(tagged)

  def embed(self):
    "Embed the whole contents in a div."
    embeddedtag = self.getembeddedtag()
    tagged = TaggedText().complete(self.contents, embeddedtag, True)
    self.contents = [tagged]
    return tagged

  def processfloats(self):
    "Process all floats contained inside."
    floats = self.searchall(Float)
    counter = NumberCounter('subfloat').setmode('a')
    for subfloat in floats:
      subfloat.output.tag = subfloat.output.tag.replace('div', 'span')
      # number the float
      counter.increase()
      number = counter.getvalue()
      entry = '(' + number + ')'
      subfloat.partkey = PartKey().createfloat(entry, number)

  def getembeddedtag(self):
    "Get the tag for the embedded object."
    floats = self.searchall(Float)
    if len(floats) > 0:
      return 'div class="multi' + self.type + '"'
    return 'div class="' + self.type + '"'

  def applywideningtag(self, container):
    "Apply the tag to set float width, if present."
    images = self.searchall(Image)
    if len(images) != 1:
      return ''
    image = images[0]
    if not image.size:
      return
    width = image.size.removepercentwidth()
    if not width:
      return
    image.type = 'figure'
    ContainerSize().setmax(width).addstyle(container)
    image.settag()

  def searchinside(self, type):
    "Search for a given type in the contents"
    return self.searchincontents(self.contents, type)

  def searchincontents(self, contents, type):
    "Search in the given contents for the required type."
    list = []
    for element in contents:
      list += self.searchinelement(element, type)
    return list

  def searchinelement(self, element, type):
    "Search for a given type outside floats"
    if isinstance(element, Float):
      return []
    if isinstance(element, type):
      return [element]
    return self.searchincontents(element.contents, type)

  def __unicode__(self):
    "Return a printable representation"
    return 'Floating inset of type ' + self.type

class Wrap(Float):
  "A wrapped (floating) float"

  def processtags(self):
    "Add the widening tag to the parent tag."
    self.embed()
    placement = self.getparameter('placement')
    if not placement:
      placement = 'o'
    self.output.tag = 'div class="wrap-' + placement + '"'
    self.applywideningtag(self)

class Caption(Container):
  "A caption for a figure or a table"

  def __init__(self):
    self.parser = InsetParser()
    self.output = TaggedOutput().settag('div class="caption"', True)

  def create(self, message):
    "Create a caption with a given message."
    self.contents = [Constant(message)]
    return self

class Listing(Container):
  "A code listing"

  processor = None

  def __init__(self):
    self.parser = InsetParser()
    self.output = TaggedOutput().settag('div class="listing"', True)
    self.numbered = None
    # DCB : Use the default brush
    self.brush = Options.defaultbrush

  def process(self):
    "Remove all layouts"
    self.counter = 0
    self.type = 'listing'
    self.processparams()
    if Listing.processor:
      Listing.processor.preprocess(self)
    newcontents = []
    captions = []
    for container in self.contents:
      # DCB : We don't want inset captions inside the <pre/>, so we filter
      # them out and save them for later
      if container.searchall(Caption) == []:
        newcontents += self.extract(container)
      else:
        captions.insert(0, container)

    # DCB: Add highlighting via brush
    if self.brush:
      tagged = TaggedText().complete(newcontents, 'pre class="listing brush: ' + self.brush + '"', False)
    else:
      tagged = TaggedText().complete(newcontents, 'pre class="listing', False)

    self.contents = [tagged]
    # DCB: If we found an inset caption, use the last one
    if captions != []:
      self.contents.insert(0, captions[0])
    else:
      # DCB: If we had no inset captions, use any in the listings params
      if 'caption' in self.lstparams:
        text = self.lstparams['caption'][1:-1]
        self.contents.insert(0, Caption().create(text))

    # If this is HTML or XML, we need to escape leading "<" characters
    if "ml" in self.brush.lower():
      for part in self.contents:
        if isinstance(part, TaggedText):
          for line in part.contents:
            if isinstance(line, Constant):
              line.string = line.string.replace("<", "&lt;")

    if Listing.processor:
      Listing.processor.postprocess(self)

  def processparams(self):
    "Process listing parameteres."
    LstParser().parsecontainer(self)
    if 'numbers' in self.lstparams:
      self.numbered = self.lstparams['numbers']
    if 'language' in self.lstparams:
      self.brush = self.lstparams['language'].lower()

  def extract(self, container):
    "Extract the container's contents and return them"
    if isinstance(container, StringContainer):
      return self.modifystring(container)
    if isinstance(container, StandardLayout):
      return self.modifylayout(container)
    if isinstance(container, PlainLayout):
      return self.modifylayout(container)
    Trace.error('Unexpected container ' + container.__class__.__name__ +
        ' in listing')
    container.tree()
    return []

  def modifystring(self, string):
    "Modify a listing string"
    if string.string == '':
      string.string = u'​'
    return self.modifycontainer(string)

  def modifylayout(self, layout):
    "Modify a standard layout"
    if len(layout.contents) == 0:
      layout.contents = [Constant(u'​')]
    return self.modifycontainer(layout)

  def modifycontainer(self, container):
    "Modify a listing container"
    contents = [container, Constant('\n')]
    if self.numbered:
      self.counter += 1
      tag = 'span class="number-' + self.numbered + '"'
      contents.insert(0, TaggedText().constant(unicode(self.counter), tag))
    return contents

class FloatNumber(Container):
  "Holds the number for a float in the caption."

  def __init__(self):
    self.output = ContentsOutput()

  def create(self, float):
    "Create the float number."
    self.contents = [Constant(float.partkey.tocentry)]
    return self

class PostFloat(object):
  "Postprocess a float: number it and move the label"

  processedclass = Float

  def postprocess(self, last, float, next):
    "Move the label to the top and number the caption"
    number = FloatNumber().create(float)
    for caption in float.searchinside(Caption):
      self.postlabels(float, caption)
      caption.contents.insert(0, Separator(u' '))
      caption.contents.insert(0, number)
    return float

  def postlabels(self, float, caption):
    "Search for labels and move them to the top"
    labels = caption.searchremove(Label)
    if len(labels) == 0:
      labels = [Label().create(' ', float.partkey.tocentry.replace(' ', '-'))]
    float.contents = labels + float.contents

class PostWrap(PostFloat):
  "For a wrap: exactly like a float"

  processedclass = Wrap

Postprocessor.stages += [PostFloat, PostWrap]



class InsetText(Container):
  "An inset of text in a lyx file"

  def __init__(self):
    self.parser = BoundedParser()
    self.output = ContentsOutput()

class Inset(Container):
  "A generic inset in a LyX document"

  def __init__(self):
    self.contents = list()
    self.parser = InsetParser()
    self.output = TaggedOutput().setbreaklines(True)

  def process(self):
    self.type = self.header[1]
    self.output.tag = 'span class="' + self.type + '"'

  def __unicode__(self):
    return 'Inset of type ' + self.type

class NewlineInset(Newline):
  "A newline or line break in an inset"

  def __init__(self):
    self.parser = InsetParser()
    self.output = FixedOutput()

class NewPageInset(NewPage):
  "A new page command."

  def __init__(self):
    self.parser = InsetParser()
    self.output = FixedOutput()

class Branch(Container):
  "A branch within a LyX document"

  def __init__(self):
    self.parser = InsetParser()
    self.output = TaggedOutput().settag('span class="branch"', True)

  def process(self):
    "Disable inactive branches"
    self.branch = self.header[2]
    if not self.isactive():
      Trace.debug('Branch ' + self.branch + ' not active')
      self.output = EmptyOutput()

  def isactive(self):
    "Check if the branch is active"
    if not self.branch in Options.branches:
      Trace.error('Invalid branch ' + self.branch)
      return True
    branch = Options.branches[self.branch]
    return branch.isselected()

class ShortTitle(Container):
  "A short title to display (always hidden)"

  def __init__(self):
    self.parser = InsetParser()
    self.output = EmptyOutput()

class FlexInset(Container):
  "A flexible inset, generic version."

  def __init__(self):
    self.parser = InsetParser()
    self.output = TaggedOutput().settag('span', False)

  def process(self):
    "Set the correct flex tag."
    self.type = self.header[2]
    if not self.type in TagConfig.flex:
      Trace.error('Unknown Flex inset ' + self.type)
      return
    self.output.settag(TagConfig.flex[self.type], False)

class InfoInset(Container):
  "A LyX Info inset"

  def __init__(self):
    self.parser = InsetParser()
    self.output = TaggedOutput().settag('span class="Info"', False)

  def process(self):
    "Set the shortcut as text"
    self.type = self.getparameter('type')
    self.contents = [Constant(self.getparameter('arg'))]

class BoxInset(Container):
  "A box inset"

  def __init__(self):
    self.parser = InsetParser()
    self.output = TaggedOutput().settag('div', True)

  def process(self):
    "Set the correct tag"
    self.type = self.header[2]
    self.output.settag('div class="' + self.type + '"', True)
    ContainerSize().readparameters(self).addstyle(self)

class PhantomText(Container):
  "A line of invisible text (white over white)."

  def __init__(self):
    self.parser = InsetParser()
    self.output = TaggedOutput().settag('span class="phantom"', False)

class LineInset(LyXLine):
  "A LaTeX ruler, but parsed as an inset."

  def __init__(self):
    self.parser = InsetParser()
    self.output = FixedOutput()

class IncludeInset(Container):
  "A child document included within another."

  # the converter factory will be set in converter.py
  converterfactory = None
  filename = None

  def __init__(self):
    self.parser = InsetParser()
    self.output = ContentsOutput()

  def process(self):
    "Include the provided child document"
    self.filename = os.path.join(Options.directory, self.getparameter('filename'))
    Trace.debug('Child document: ' + self.filename)
    LstParser().parsecontainer(self)
    command = self.getparameter('LatexCommand')
    if command == 'verbatiminput':
      self.readverbatim()
      return
    elif command == 'lstinputlisting':
      self.readlisting()
      return
    self.processinclude()

  def processinclude(self):
    "Process a regular include: standard child document."
    self.contents = []
    olddir = Options.directory
    newdir = os.path.dirname(self.getparameter('filename'))
    if newdir != '':
      Trace.debug('Child dir: ' + newdir)
      Options.directory = os.path.join(Options.directory, newdir)
    try:
      self.convertinclude()
    finally:
      Options.directory = olddir

  def convertinclude(self):
    "Convert an included document."
    try:
      converter = IncludeInset.converterfactory.create(self)
    except:
      Trace.error('Could not read ' + self.filename + ', please check that the file exists and has read permissions.')
      return
    if self.hasemptyoutput():
      return
    converter.convert()
    self.contents = converter.getcontents()

  def readverbatim(self):
    "Read a verbatim document."
    self.contents = [TaggedText().complete(self.readcontents(), 'pre', True)]

  def readlisting(self):
    "Read a document as a listing."
    listing = Listing()
    listing.contents = self.readcontents()
    listing.parameters = self.parameters
    listing.process()
    self.contents = [listing]

  def readcontents(self):
    "Read the contents of a complete file."
    contents = list()
    lines = BulkFile(self.filename).readall()
    for line in lines:
      contents.append(Constant(line))
    return contents

  def __unicode__(self):
    "Return a printable description."
    if not self.filename:
      return 'Included unnamed file'
    return 'Included "' + self.filename + '"'






class ChangeInserted(Container):
  "A change which consists of an insertion."

  def __init__(self):
    self.parser = TextParser(self)
    if DocumentParameters.outputchanges:
      self.output = TaggedOutput().settag('span class="inserted"')
    else:
      self.output = ContentsOutput()

class ChangeDeleted(TaggedText):
  "A change which consists of a deletion."

  def __init__(self):
    self.parser = TextParser(self)
    if DocumentParameters.outputchanges:
      self.output = TaggedOutput().settag('span class="deleted"')
    else:
      self.output = EmptyOutput()









class BigSymbol(object):
  "A big symbol generator."

class BigBracket(BigSymbol):
  "A big bracket generator."

  def __init__(self, size, bracket):
    "Set the size and symbol for the bracket."
    self.size = size
    if bracket in FormulaConfig.bigbrackets:
      self.pieces = FormulaConfig.bigbrackets[bracket]
    else:
      self.pieces = [bracket, bracket]

  def getpiece(self, index):
    "Return the nth piece for the bracket."
    if len(self.pieces) == 1:
      return self.pieces[0]
    if index == 0:
      return self.pieces[0]
    if index == self.size - 1:
      return self.pieces[-1]
    return self.pieces[1]

  def getcell(self, index, align):
    "Get the bracket piece as an array cell."
    piece = self.getpiece(index)
    return TaggedBit().constant(piece, 'span class="bracket align-' + align + '"')

class CasesBrace(BigBracket):
  "A big brace used for a case statement."

  def __init__(self, size):
    "Set the size for the brace."
    self.size = size

  def getpiece(self, index):
    "Get the nth piece for the brace."
    if index == 0:
      return u'⎧'
    if index == self.size - 1:
      return u'⎩'
    if index == (self.size - 1)/2:
      return u'⎨'
    return u'⎪'



class FormulaEquation(CommandBit):
  "A simple numbered equation."

  piece = 'equation'

  def parsebit(self, pos):
    "Parse the array"
    self.output = ContentsOutput()
    self.add(self.factory.parsetype(WholeFormula, pos))

class FormulaCell(FormulaCommand):
  "An array cell inside a row"

  def setalignment(self, alignment):
    self.alignment = alignment
    self.output = TaggedOutput().settag('span class="arraycell align-' + alignment +'"', True)
    return self

  def parsebit(self, pos):
    self.factory.clearignored(pos)
    if pos.finished():
      return
    if not self.factory.detecttype(WholeFormula, pos):
      Trace.error('Unexpected end of array cell at ' + pos.identifier())
      pos.skip(pos.current())
      return
    self.add(self.factory.parsetype(WholeFormula, pos))

class FormulaRow(FormulaCommand):
  "An array row inside an array"

  cellseparator = FormulaConfig.array['cellseparator']

  def setalignments(self, alignments):
    self.alignments = alignments
    self.output = TaggedOutput().settag('span class="arrayrow"', True)
    return self

  def parsebit(self, pos):
    "Parse a whole row"
    index = 0
    pos.pushending(self.cellseparator, optional=True)
    while not pos.finished():
      alignment = self.alignments[index % len(self.alignments)]
      cell = self.factory.create(FormulaCell).setalignment(alignment)
      cell.parsebit(pos)
      self.add(cell)
      index += 1
      pos.checkskip(self.cellseparator)
    if len(self.contents) == 0:
      self.output = EmptyOutput()

class MultiRowFormula(CommandBit):
  "A formula with multiple rows."

  def parserows(self, pos):
    "Parse all rows, finish when no more row ends"
    self.rows = []
    first = True
    for row in self.iteraterows(pos):
      if first:
        first = False
      else:
        # intersparse empty rows
        self.addempty()
      row.parsebit(pos)
      self.addrow(row)

  def iteraterows(self, pos):
    "Iterate over all rows, end when no more row ends"
    rowseparator = FormulaConfig.array['rowseparator']
    while True:
      pos.pushending(rowseparator, True)
      row = self.factory.create(FormulaRow)
      yield row.setalignments(self.alignments)
      if pos.checkfor(rowseparator):
        self.original += pos.popending(rowseparator)
      else:
        return

  def addempty(self):
    "Add an empty row."
    row = FormulaRow().setalignments(self.alignments)
    for alignment in self.alignments:
      cell = self.factory.create(FormulaCell).setalignment(alignment)
      cell.add(FormulaConstant(u' '))
      row.add(cell)
    self.addrow(row)

  def addrow(self, row):
    "Add a row to the contents and to the list of rows."
    self.rows.append(row)
    self.add(row)

class FormulaArray(MultiRowFormula):
  "An array within a formula"

  piece = 'array'

  def parsebit(self, pos):
    "Parse the array"
    self.output = TaggedOutput().settag('span class="array"', True)
    self.parsealignments(pos)
    self.parserows(pos)

  def parsealignments(self, pos):
    "Parse the different alignments"
    # vertical
    self.valign = 'c'
    literal = self.parsesquareliteral(pos)
    if literal:
      self.valign = literal
    # horizontal
    literal = self.parseliteral(pos)
    self.alignments = []
    for l in literal:
      self.alignments.append(l)

class FormulaMatrix(MultiRowFormula):
  "A matrix (array with center alignment)."

  piece = 'matrix'

  def parsebit(self, pos):
    "Parse the matrix, set alignments to 'c'."
    self.output = TaggedOutput().settag('span class="array"', True)
    self.valign = 'c'
    self.alignments = ['c']
    self.parserows(pos)

class FormulaCases(MultiRowFormula):
  "A cases statement"

  piece = 'cases'

  def parsebit(self, pos):
    "Parse the cases"
    self.output = TaggedOutput().settag('span class="bracketcases"', True)
    self.alignments = ['l', 'l']
    self.parserows(pos)
    for row in self.contents:
      for cell in row.contents:
        cell.output.settag('span class="case align-l"', True)
        cell.contents.append(FormulaConstant(u' '))
    brace = CasesBrace(len(self.contents))
    for index, row in enumerate(self.rows):
      row.contents.insert(0, brace.getcell(index, 'l'))

class EquationEnvironment(MultiRowFormula):
  "A \\begin{}...\\end equation environment with rows and cells."

  def parsebit(self, pos):
    "Parse the whole environment."
    self.output = TaggedOutput().settag('span class="environment"', True)
    environment = self.piece.replace('*', '')
    if environment in FormulaConfig.environments:
      self.alignments = FormulaConfig.environments[environment]
    else:
      Trace.error('Unknown equation environment ' + self.piece)
      self.alignments = ['l']
    self.parserows(pos)

class BeginCommand(CommandBit):
  "A \\begin{}...\end command and what it entails (array, cases, aligned)"

  commandmap = {FormulaConfig.array['begin']:''}

  types = [FormulaEquation, FormulaArray, FormulaCases, FormulaMatrix]

  def parsebit(self, pos):
    "Parse the begin command"
    command = self.parseliteral(pos)
    bit = self.findbit(command)
    ending = FormulaConfig.array['end'] + '{' + command + '}'
    pos.pushending(ending)
    bit.parsebit(pos)
    self.add(bit)
    self.array = bit
    self.original += pos.popending(ending)

  def findbit(self, piece):
    "Find the command bit corresponding to the \\begin{piece}"
    for type in BeginCommand.types:
      if piece.replace('*', '') == type.piece:
        return self.factory.create(type)
    bit = self.factory.create(EquationEnvironment)
    bit.piece = piece
    return bit

FormulaCommand.types += [BeginCommand]









class BibTagParser(object):
  "A parser for BibTeX tags."

  nameseparators = ['{', '=', '"', '#']

  def __init__(self):
    self.key = None
    tags = BibStylesConfig.defaulttags
    self.tags = dict((x, BibTag().constant(tags[x])) for x in tags)

  def parse(self, pos):
    "Parse the entry between {}."
    self.type = BibTag.readexcluding(pos, self.nameseparators).strip()
    if not pos.checkskip('{'):
      pos.error('Entry should start with {')
      return
    pos.pushending('}')
    self.parsetags(pos)
    pos.popending('}')
    pos.skipspace()

  def parsetags(self, pos):
    "Parse all tags in the entry."
    pos.skipspace()
    while not pos.finished():
      if pos.checkskip('{'):
        pos.error('Unmatched {')
        return
      pos.pushending(',', True)
      self.parsetag(pos)
      if pos.checkfor(','):
        pos.popending(',')
  
  def parsetag(self, pos):
    "Parse a single tag."
    (key, value) = self.getkeyvalue(pos)
    if not value:
      self.key = key
      return
    name = key.lower()
    self.tags[name] = value
    if hasattr(self, 'dissect' + name):
      dissector = getattr(self, 'dissect' + name)
      dissector(value.extracttext())
    if not pos.finished():
      remainder = pos.globexcluding(',')
      pos.error('Ignored ' + remainder + ' before comma')

  def getkeyvalue(self, pos):
    "Parse a string of the form key=value."
    piece = BibTag.readexcluding(pos, self.nameseparators).strip()
    if pos.finished():
      return (piece, None)
    if not pos.checkskip('='):
      pos.error('Undesired character in tag name ' + piece)
      pos.skipcurrent()
      return (piece, None)
    key = piece.lower()
    pos.skipspace()
    value = self.parsevalue(pos)
    return (key, value)

  def parsevalue(self, pos):
    "Parse the value for a tag."
    tag = BibTag()
    pos.skipspace()
    if pos.checkfor(','):
      pos.error('Unexpected ,')
      return tag.error()
    tag.parse(pos)
    return tag

  def dissectauthor(self, authortag):
    "Dissect the author tag into pieces."
    authorsplit = authortag.split(' and ')
    if len(authorsplit) == 0:
      return
    authorlist = []
    for authorname in authorsplit:
      author = BibAuthor().parse(authorname)
      authorlist.append(author)
    initials = ''
    authors = ''
    if len(authorlist) == 1:
      initials = authorlist[0].surname[0:3]
      authors = unicode(authorlist[0])
    else:
      for author in authorlist:
        initials += author.surname[0:1]
        authors += unicode(author) + ', '
      authors = authors[:-2]
    self.tags['surname'] = BibTag().constant(authorlist[0].surname)
    self.tags['Sur'] = BibTag().constant(initials)
    self.tags['authors'] = BibTag().constant(authors)

  def dissectyear(self, yeartag):
    "Dissect the year tag into pieces, looking for 4 digits in a row."
    pos = TextPosition(yeartag)
    while not pos.finished():
      if pos.current().isdigit():
        number = pos.globnumber()
        if len(number) == 4:
          self.tags['YY'] = BibTag().constant(number[2:])
          return
      else:
        pos.skipcurrent()

  def dissectfile(self, filetag):
    "Extract the filename from the file tag as ':filename:FORMAT'."
    if not filetag.startswith(':'):
      return
    bits = filetag.split(':')
    if len(bits) != 3:
      return
    self.tags['filename'] = BibTag().constant(bits[1])
    self.tags['format'] = BibTag().constant(bits[2])

  def gettag(self, key):
    "Get the tag for a given key."
    if not key in self.tags:
      return None
    return self.tags[key]

  def gettagtext(self, key):
    "Get the tag for a key as raw text."
    return self.gettag(key).extracttext()

  def lineerror(self, message, pos):
    "Show an error message for a line."
    Trace.error(message + ': ' + pos.identifier())

class BibTag(Container):
  "A tag in a BibTeX file."

  valueseparators = ['{', '"', '#', '\\', '}', '$']
  stringdefs = dict()
  replaced = BibTeXConfig.replaced
  replacedinitials = [x[0] for x in BibTeXConfig.replaced]
  factory = FormulaFactory()

  def __init__(self):
    self.contents = []
    self.output = ContentsOutput()

  def constant(self, text):
    "Initialize for a single constant."
    self.contents = [Constant(text)]
    return self

  def error(self):
    "To use when parsing resulted in an error."
    return self.constant('')

  def add(self, piece):
    "Add a new piece to the tag."
    if isinstance(piece, basestring):
      self.addtext(piece)
    else:
      self.contents.append(piece)

  def addtext(self, piece):
    "Add a text string to the tag."
    last = self.findlaststring()
    if last:
      last.string += piece
      return
    self.contents.append(Constant(piece))

  def findlaststring(self):
    "Find the last string in the contents."
    if len(self.contents) == 0:
      return None
    string = self.contents[-1]
    if not isinstance(string, StringContainer):
      return None
    return string

  def parse(self, pos):
    "Parse a BibTeX tag."
    self.parserecursive(pos, True)
    # strip ending blank characters
    last = self.findlaststring()
    if last:
      before = last.string
      last.string = last.string.rstrip()

  def parserecursive(self, pos, initial=False):
    "Parse brackets or quotes recursively."
    while not pos.finished():
      self.parsetext(pos, initial)
      if pos.finished():
        return
      elif pos.checkfor('{'):
        self.parsebracket(pos, initial)
      elif pos.checkfor('"'):
        self.parsequoted(pos, initial)
      elif pos.checkfor('\\'):
        self.parseescaped(pos)
      elif pos.checkfor('#'):
        self.parsehash(pos, initial)
      elif pos.checkfor('$'):
        self.parseformula(pos)
      else:
        pos.error('Unexpected character ' + pos.current())
        pos.skipcurrent()

  def parsetext(self, pos, initial):
    "Parse a bit of text."
    "If on the initial level, try to substitute strings with string defs."
    text = BibTag.readexcluding(pos, self.valueseparators)
    if text == '':
      return
    key = text.strip()
    if initial and key in self.stringdefs:
      self.add(self.stringdefs[key])
      return
    self.add(text)

  def parseescaped(self, pos):
    "Parse an escaped string \\*."
    if pos.checkfor('\\(') or pos.checkfor('\\['):
      # start of formula commands
      self.parseformula(pos)
      return
    if not self.factory.detecttype(FormulaCommand, pos):
      pos.error('Not an escape sequence')
      return
    self.add(self.factory.parsetype(FormulaCommand, pos))

  def parsebracket(self, pos, initial):
    "Parse a {} bracket"
    if not pos.checkskip('{'):
      pos.error('Missing opening { in bracket')
      return
    pos.pushending('}')
    self.parserecursive(pos, initial)
    pos.popending('}')

  def parsequoted(self, pos, initial):
    "Parse a piece of quoted text"
    if not pos.checkskip('"'):
      pos.error('Missing opening " in quote')
      return
    if not initial:
      self.add('"')
      return
    pos.pushending('"')
    self.parserecursive(pos)
    pos.popending('"')
    pos.skipspace()

  def parsehash(self, pos, initial):
    "Parse a hash mark #."
    if not pos.checkskip('#'):
      pos.error('Missing # in hash')
      return
    if not initial:
      self.add('#')

  def parseformula(self, pos):
    "Parse a whole formula."
    formula = Formula().parse(pos)
    self.add(formula)

  def readexcluding(cls, pos, undesired):
    "Parse a piece not structure (including spaces)."
    result = ''
    while not pos.finished():
      if pos.current() in undesired:
        return result
      if pos.current().isspace():
        result += ' '
        pos.skipspace()
      else:
        replaced = cls.readreplaced(pos)
        if replaced:
          result += replaced
        else:
          result += pos.skipcurrent()
    return result

  def readreplaced(cls, pos):
    "Check for one of the replaced strings."
    if not pos.current() in BibTag.replacedinitials:
      return None
    for key in BibTag.replaced:
      if pos.checkskip(key):
        return BibTag.replaced[key]
    return None

  readexcluding = classmethod(readexcluding)
  readreplaced = classmethod(readreplaced)

  def __unicode__(self):
    "Return a printable representation."
    return 'BibTag: ' + self.extracttext()

class BibAuthor(object):
  "A BibTeX individual author."

  def __init__(self):
    self.surname = ''
    self.firstnames = []

  def parse(self, tag):
    "Parse an individual author tag."
    if ',' in tag:
      self.parsecomma(tag)
    else:
      self.parsewithoutcomma(tag)
    return self

  def parsecomma(self, tag):
    "Parse an author with a comma: Python, M."
    bits = tag.split(',')
    if len(bits) > 2:
      Trace.error('Too many commas in ' + tag)
    self.surname = bits[0].strip()
    self.parsefirstnames(bits[1].strip())

  def parsewithoutcomma(self, tag):
    "Parse an author without a comma: M. Python."
    bits = tag.rsplit(None, 1)
    if len(bits) == 0:
      Trace.error('Empty author')
      return
    self.surname = bits[-1].strip()
    if len(bits) == 1:
      return
    self.parsefirstnames(bits[0].strip())

  def parsefirstnames(self, firstnames):
    "Parse the first name."
    for firstname in firstnames.split():
      self.firstnames.append(firstname)

  def getinitial(self):
    "Get the main initial for the author."
    if len(self.surname) == 0:
      return ''
    return self.surname[0].toupper()

  def __unicode__(self):
    "Return a printable representation."
    result = ''
    for firstname in self.firstnames:
      result += firstname + ' '
    return result + self.surname



class BibTeX(Container):
  "Show a BibTeX bibliography and all referenced entries"

  def __init__(self):
    self.parser = InsetParser()
    self.output = ContentsOutput()

  def process(self):
    "Read all bibtex files and process them."
    self.entries = []
    self.contents = [self.createheader()]
    bibliography = Translator.translate('bibliography')
    files = self.getparameterlist('bibfiles')
    showall = False
    if self.getparameter('btprint') == 'btPrintAll':
      showall = True
    for file in files:
      bibfile = BibFile(file, showall)
      bibfile.parse()
      self.entries += bibfile.entries
      Trace.message('Parsed ' + unicode(bibfile))
    self.entries.sort(key = unicode)
    self.applystyle()

  def createheader(self):
    "Create the header for the bibliography."
    header = BiblioHeader()
    if 'bibtotoc' in self.getparameterlist('options'):
      header.addtotoc(self)
    return header

  def applystyle(self):
    "Read the style and apply it to all entries"
    style = self.readstyle()
    for entry in self.entries:
      entry.template = style['default']
      entry.citetemplate = style['cite']
      type = entry.type.lower()
      if type in style:
        entry.template = style[type]
      entry.process()
      self.contents.append(entry)

  def readstyle(self):
    "Read the style from the bibliography options"
    for option in self.getparameterlist('options'):
      if hasattr(BibStylesConfig, option):
        return getattr(BibStylesConfig, option)
    return BibStylesConfig.default

class BibFile(object):
  "A BibTeX file"

  def __init__(self, filename, showall):
    "Create the BibTeX file"
    self.filename = filename + '.bib'
    self.showall = showall
    self.added = 0
    self.ignored = 0
    self.entries = []

  def parse(self):
    "Parse the BibTeX file and extract all entries."
    try:
      self.parsefile()
    except IOError:
      Trace.error('Error reading ' + self.filename + '; make sure the file exists and can be read.')

  def parsefile(self):
    "Parse the whole file."
    bibpath = InputPath(self.filename)
    if Options.lowmem:
      pos = FilePosition(bibpath.path)
    else:
      bulkfile = BulkFile(bibpath.path)
      text = ''.join(bulkfile.readall())
      pos = TextPosition(text)
    while not pos.finished():
      pos.skipspace()
      if pos.checkskip(','):
        pos.skipspace()
      self.parseentry(pos)

  def parseentry(self, pos):
    "Parse a single entry"
    for entry in BibEntry.instances:
      if entry.detect(pos):
        newentry = Cloner.clone(entry)
        newentry.parse(pos)
        if self.showall or newentry.isreferenced():
          self.entries.append(newentry)
          self.added += 1
        else:
          self.ignored += 1
        return
    # Skip the whole line since it's a comment outside an entry
    pos.globincluding('\n').strip()

  def __unicode__(self):
    "String representation"
    string = self.filename + ': ' + unicode(self.added) + ' entries added, '
    string += unicode(self.ignored) + ' entries ignored'
    return string

class BibEntry(Container):
  "An entry in a BibTeX file"

  instances = []

  def detect(self, pos):
    "Throw an error."
    Trace.error('Tried to detect() in ' + unicode(self))

  def parse(self, pos):
    "Throw an error."
    Trace.error('Tried to parse() in ' + unicode(self))

  def isreferenced(self):
    "Throw an error."
    Trace.error('Function isreferenced() not implemented for ' + unicode(self))

  def __unicode__(self):
    "Return a string representation"
    return 'BibTeX entry ' + self.__class__.__name__

class CommentEntry(BibEntry):
  "A simple comment."

  def detect(self, pos):
    "Detect the special entry"
    return pos.checkfor('%')

  def parse(self, pos):
    "Parse all consecutive comment lines."
    while pos.checkfor('%'):
      pos.globincluding('\n')

  def isreferenced(self):
    "A comment entry is never referenced"
    return False

  def __unicode__(self):
    "Return a string representation"
    return 'Comment'

class SpecialEntry(BibEntry):
  "A special entry"

  types = ['@preamble', '@comment']

  def __init__(self):
    self.contents = []
    self.output = EmptyOutput()

  def detect(self, pos):
    "Detect the special entry"
    for type in self.types:
      if pos.checkforlower(type):
        return True
    return False

  def parse(self, pos):
    "Parse and ignore."
    self.type = 'special'
    pos.globincluding('{')
    pos.pushending('}')
    while not pos.finished():
      if pos.checkfor('{'):
        self.parse(pos)
      else:
        pos.skipcurrent()
    pos.popending()

  def isreferenced(self):
    "A special entry is never referenced"
    return False

  def __unicode__(self):
    "Return a string representation"
    return self.type

class StringEntry(SpecialEntry):
  "A string definition. The definition can later be used in other entries."

  parser = BibTagParser()
  start = '@string'
  key = None

  def detect(self, pos):
    "Detect the string definition."
    return pos.checkforlower(self.start)

  def parse(self, pos):
    "Parse a single tag, which will define a string."
    self.type = self.start
    if not self.checkstart(pos):
      return
    pos.skipspace()
    if not pos.checkskip('{'):
      Trace.error('Missing opening { in ' + unicode(self))
      pos.globincluding('\n')
      return
    pos.pushending('}')
    (self.key, value) = self.parser.getkeyvalue(pos)
    BibTag.stringdefs[self.key] = value
    pos.popending('}')

  def checkstart(self, pos):
    "Check that the entry starts with @string."
    if not pos.checkskip('@'):
      Trace.error('Missing @ from string definition')
      return False
    name = '@' + pos.globalpha()
    if not name.lower() == self.start.lower():
      Trace.error('Invalid start @' + name +', missing ' + self.start + ' from ' + unicode(self))
      pos.globincluding('\n')
      return False
    return True

  def __unicode__(self):
    "Return a printable representation."
    result = 'string definition'
    if self.key:
      result += ' for ' + self.key
    return result


BibEntry.instances += [CommentEntry(), SpecialEntry(), StringEntry()]






class PubEntry(BibEntry):
  "A publication entry"

  def __init__(self):
    self.output = TaggedOutput().settag('p class="biblio"', True)

  def detect(self, pos):
    "Detect a publication entry."
    return pos.checkfor('@')

  def parse(self, pos):
    "Parse the publication entry."
    self.parser = BibTagParser()
    self.parser.parse(pos)
    self.type = self.parser.type

  def isreferenced(self):
    "Check if the entry is referenced."
    if not self.parser.key:
      return False
    return self.parser.key in BiblioReference.references

  def process(self):
    "Process the entry."
    self.index = NumberGenerator.generator.generate('pubentry')
    self.parser.tags['index'] = Constant(self.index)
    biblio = BiblioEntry()
    biblio.citeref = self.createref()
    biblio.processcites(self.parser.key)
    self.contents = [biblio, Constant(' ')]
    self.contents += self.entrycontents()

  def entrycontents(self):
    "Get the contents of the entry."
    return self.translatetemplate(self.template)

  def createref(self):
    "Create the reference to cite."
    return self.translatetemplate(self.citetemplate)

  def translatetemplate(self, template):
    "Translate a complete template into a list of contents."
    pos = TextPosition(template)
    part = BibPart(self.parser.tags).parse(pos)
    for variable in part.searchall(BibVariable):
      if variable.empty():
        Trace.error('Error parsing BibTeX template for ' + unicode(self) + ': '
            + unicode(variable) + ' is empty')
    return [part]

  def __unicode__(self):
    "Return a string representation"
    string = ''
    if 'author' in self.parser.tags:
      string += self.parser.gettagtext('author') + ': '
    if 'title' in self.parser.tags:
      string += '"' + self.parser.gettagtext('title') + '"'
    return string

class BibPart(Container):
  "A part of a BibTeX template."

  def __init__(self, tags):
    self.output = ContentsOutput()
    self.contents = []
    self.tags = tags
    self.quotes = 0

  def parse(self, pos):
    "Parse a part of a template, return a list of contents."
    while not pos.finished():
      self.add(self.parsepiece(pos))
    return self

  def parsepiece(self, pos):
    "Get the next piece of the template, return if it was empty."
    if pos.checkfor('{'):
      return self.parsebraces(pos)
    elif pos.checkfor('$'):
      return self.parsevariable(pos)
    result = ''
    while not pos.finished() and not pos.current() in '{$':
      if pos.current() == '"':
        self.quotes += 1
      result += pos.skipcurrent()
    return Constant(result)

  def parsebraces(self, pos):
    "Parse a pair of curly braces {}."
    if not pos.checkskip('{'):
      Trace.error('Missing { in braces.')
      return None
    pos.pushending('}')
    part = BibPart(self.tags).parse(pos)
    pos.popending('}')
    empty = part.emptyvariables()
    if empty:
      return None
    return part

  def parsevariable(self, pos):
    "Parse a variable $name."
    var = BibVariable(self.tags).parse(pos)
    if self.quotes % 2 == 1:
      # odd number of quotes; don't add spans in an attribute
      var.removetag()
    return var

  def emptyvariables(self):
    "Find out if there are only empty variables in the part."
    for variable in self.searchall(BibVariable):
      if not variable.empty():
        return False
    return True

  def add(self, piece):
    "Add a new piece to the current part."
    if not piece:
      return
    if self.redundantdot(piece):
      # remove extra dot
      piece.string = piece.string[1:]
    self.contents.append(piece)
    piece.parent = self

  def redundantdot(self, piece):
    "Find out if there is a redundant dot in the next piece."
    if not isinstance(piece, Constant):
      return False
    if not piece.string.startswith('.'):
      return False
    if len(self.contents) == 0:
      return False
    if not isinstance(self.contents[-1], BibVariable):
      return False
    if not self.contents[-1].extracttext().endswith('.'):
      return False
    return True

class BibVariable(Container):
  "A variable in a BibTeX template."
  
  def __init__(self, tags):
    self.output = TaggedOutput()
    self.contents = []
    self.tags = tags

  def parse(self, pos):
    "Parse the variable name."
    if not pos.checkskip('$'):
      Trace.error('Missing $ in variable name.')
      return self
    self.key = pos.globalpha()
    self.output.tag = 'span class="bib-' + self.key + '"'
    self.processtags()
    return self

  def processtags(self):
    "Find the tag with the appropriate key in the list of tags."
    if not self.key in self.tags:
      return
    result = self.tags[self.key]
    self.contents = [result]

  def empty(self):
    "Find out if the variable is empty."
    if not self.contents:
      return True
    if self.extracttext() == '':
      return True
    return False

  def removetag(self):
    "Remove the output tag and leave just the contents."
    self.output = ContentsOutput()

  def __unicode__(self):
    "Return a printable representation."
    result = 'variable ' + self.key
    if not self.empty():
      result += ':' + self.extracttext()
    return result

BibEntry.instances += [PubEntry()]






class NewfangledChunk(Layout):
  "A chunk of literate programming."

  names = dict()
  firsttime = True

  def process(self):
    "Process the literate chunk."
    self.output.tag = 'div class="chunk"'
    self.type = 'chunk'
    text = self.extracttext()
    parts = text.split(',')
    if len(parts) < 1:
      Trace.error('Not enough parameters in ' + text)
      return
    self.name = parts[0]
    self.number = self.order()
    self.createlinks()
    self.contents = [self.left, self.declaration(), self.right]
    ChunkProcessor.lastchunk = self

  def order(self):
    "Create the order number for the chunk."
    return NumberGenerator.generator.generate('chunk')

  def createlinks(self):
    "Create back and forward links."
    self.leftlink = Link().complete(self.number, 'chunk:' + self.number, type='chunk')
    self.left = TaggedText().complete([self.leftlink], 'span class="chunkleft"', False)
    self.right = TaggedText().constant('', 'span class="chunkright"', False)
    if not self.name in NewfangledChunk.names:
      NewfangledChunk.names[self.name] = []
    else:
      last = NewfangledChunk.names[self.name][-1]
      forwardlink = Link().complete(self.number + u'→', 'chunkback:' + last.number, type='chunk')
      backlink = Link().complete(u'←' + last.number + u' ', 'chunkforward:' + self.number, type='chunk')
      forwardlink.setmutualdestination(backlink)
      last.right.contents.append(forwardlink)
      self.right.contents.append(backlink)
    NewfangledChunk.names[self.name].append(self)
    self.origin = self.createorigin()
    if self.name in NewfangledChunkRef.references:
      for ref in NewfangledChunkRef.references[self.name]:
        self.linkorigin(ref.origin)

  def createorigin(self):
    "Create a link that points to the chunks' origin."
    link = Link()
    self.linkorigin(link)
    return link

  def linkorigin(self, link):
    "Create a link to the origin."
    start = NewfangledChunk.names[self.name][0]
    link.complete(start.number, type='chunk')
    link.destination = start.leftlink
    link.computedestination()

  def declaration(self):
    "Get the chunk declaration."
    contents = []
    text = u'⟨' + self.name + '[' + unicode(len(NewfangledChunk.names[self.name])) + '] '
    contents.append(Constant(text))
    contents.append(self.origin)
    text = ''
    if NewfangledChunk.firsttime:
      Listing.processor = ChunkProcessor()
      NewfangledChunk.firsttime = False
    text += u'⟩'
    if len(NewfangledChunk.names[self.name]) > 1:
      text += '+'
    text += u'≡'
    contents.append(Constant(text))
    return TaggedText().complete(contents, 'span class="chunkdecl"', True)

class ChunkProcessor(object):
  "A processor for listings that belong to chunks."

  lastchunk = None
  counters = dict()
  endcommand = '}'
  chunkref = 'chunkref'

  def preprocess(self, listing):
    "Preprocess a listing: set the starting counter."
    if not ChunkProcessor.lastchunk:
      return
    name = ChunkProcessor.lastchunk.name
    if not name in ChunkProcessor.counters:
      ChunkProcessor.counters[name] = 0
    listing.counter = ChunkProcessor.counters[name]
    for command, container, index in self.commandsinlisting(listing):
      chunkref = self.getchunkref(command)
      if chunkref:
        self.insertchunkref(chunkref, container, index)

  def commandsinlisting(self, listing):
    "Find all newfangle commands in a listing."
    for container in listing.contents:
      for index in range(len(container.contents) - 2):
        if self.findinelement(container, index):
          third = container.contents[index + 2].string
          end = third.index(NewfangleConfig.constants['endmark'])
          command = third[:end]
          lenstart = len(NewfangleConfig.constants['startmark'])
          container.contents[index].string = container.contents[index].string[:-lenstart]
          del container.contents[index + 1]
          container.contents[index + 1].string = third[end + len(NewfangleConfig.constants['endmark']):]
          yield command, container, index

  def findinelement(self, container, index):
    "Find a newfangle command in an element."
    for i in range(2):
      if not isinstance(container.contents[index + i], StringContainer):
        return False
    first = container.contents[index].string
    second = container.contents[index + 1].string
    third = container.contents[index + 2].string
    if not first.endswith(NewfangleConfig.constants['startmark']):
      return False
    if second != NewfangleConfig.constants['startcommand']:
      return False
    if not NewfangleConfig.constants['endmark'] in third:
      return False
    return True

  def getchunkref(self, command):
    "Get the contents of a chunkref command, if present."
    if not command.startswith(NewfangleConfig.constants['chunkref']):
      return None
    if not NewfangleConfig.constants['endcommand'] in command:
      return None
    start = len(NewfangleConfig.constants['chunkref'])
    end = command.index(NewfangleConfig.constants['endcommand'])
    return command[start:end]

  def insertchunkref(self, ref, container, index):
    "Insert a chunkref after the given index at the given container."
    chunkref = NewfangledChunkRef().complete(ref)
    container.contents.insert(index + 1, chunkref)

  def postprocess(self, listing):
    "Postprocess a listing: store the ending counter for next chunk."
    if not ChunkProcessor.lastchunk:
      return
    ChunkProcessor.counters[ChunkProcessor.lastchunk.name] = listing.counter

class NewfangledChunkRef(Inset):
  "A reference to a chunk."

  references = dict()

  def process(self):
    "Show the reference."
    self.output.tag = 'span class="chunkref"'
    self.ref = self.extracttext()
    self.addbits()

  def complete(self, ref):
    "Complete the reference to the given string."
    self.output = ContentsOutput()
    self.ref = ref
    self.contents = [Constant(self.ref)]
    self.addbits()
    return self

  def addbits(self):
    "Add the bits to the reference."
    if not self.ref in NewfangledChunkRef.references:
      NewfangledChunkRef.references[self.ref] = []
    NewfangledChunkRef.references[self.ref].append(self)
    if self.ref in NewfangledChunk.names:
      start = NewfangledChunk.names[self.ref][0]
      self.origin = start.createorigin()
    else:
      self.origin = Link()
    self.contents.insert(0, Constant(u'⟨'))
    self.contents.append(Constant(' '))
    self.contents.append(self.origin)
    self.contents.append(Constant(u'⟩'))

  def __unicode__(self):
    "Return a printable representation."
    return 'Reference to chunk ' + self.ref






class CombiningFunction(OneParamFunction):

  commandmap = FormulaConfig.combiningfunctions

  def parsebit(self, pos):
    "Parse a combining function."
    self.type = 'alpha'
    combining = self.translated
    parameter = self.parsesingleparameter(pos)
    if len(parameter.extracttext()) != 1:
      Trace.error('Applying combining function ' + self.command + ' to invalid string "' + parameter.extracttext() + '"')
    self.contents.append(Constant(combining))

  def parsesingleparameter(self, pos):
    "Parse a parameter, or a single letter."
    if self.factory.detecttype(Bracket, pos) \
        or self.factory.detecttype(FormulaCommand, pos):
      return self.parseparameter(pos)
    letter = FormulaConstant(pos.skipcurrent())
    self.add(letter)
    return letter

class DecoratingFunction(OneParamFunction):
  "A function that decorates some bit of text"

  commandmap = FormulaConfig.decoratingfunctions

  def parsebit(self, pos):
    "Parse a decorating function"
    self.type = 'alpha'
    symbol = self.translated
    self.symbol = TaggedBit().constant(symbol, 'span class="symbolover"')
    self.parameter = self.parseparameter(pos)
    self.output = TaggedOutput().settag('span class="withsymbol"')
    self.contents.insert(0, self.symbol)
    self.parameter.output = TaggedOutput().settag('span class="undersymbol"')
    self.simplifyifpossible()

class LimitCommand(EmptyCommand):
  "A command which accepts limits above and below, in display mode."

  commandmap = FormulaConfig.limitcommands

  def parsebit(self, pos):
    "Parse a limit command."
    pieces = self.translated[1:]
    if not DocumentParameters.displaymode or len(self.translated) == 1:
      pieces = self.translated[0:1]
    self.output = TaggedOutput().settag('span class="limits"')
    for piece in pieces:
      self.contents.append(TaggedBit().constant(piece, 'span class="limit"'))

class LimitsProcessor(MathsProcessor):
  "A processor for limits inside an element."

  def process(self, contents, index):
    "Process the limits for an element."
    if self.checklimits(contents, index):
      self.modifylimits(contents, index)
    if self.checkscript(contents, index) and self.checkscript(contents, index + 1):
      self.modifyscripts(contents, index)

  def checklimits(self, contents, index):
    "Check if the current position has a limits command."
    if not DocumentParameters.displaymode:
      return False
    if not isinstance(contents[index], LimitCommand):
      return False
    return self.checkscript(contents, index + 1)

  def modifylimits(self, contents, index):
    "Modify a limits commands so that the limits appear above and below."
    limited = contents[index]
    subscript = self.getlimit(contents, index + 1)
    limited.contents.append(subscript)
    if self.checkscript(contents, index + 1):
      superscript = self.getlimit(contents, index  + 1)
    else:
      superscript = TaggedBit().constant(u' ', 'sup class="limit"')
    limited.contents.insert(0, superscript)

  def getlimit(self, contents, index):
    "Get the limit for a limits command."
    limit = self.getscript(contents, index)
    limit.output.tag = limit.output.tag.replace('script', 'limit')
    return limit

  def modifyscripts(self, contents, index):
    "Modify the super- and subscript to appear vertically aligned."
    subscript = self.getscript(contents, index)
    # subscript removed so instead of index + 1 we get index again
    superscript = self.getscript(contents, index)
    scripts = TaggedBit().complete([superscript, subscript], 'span class="scripts"')
    contents.insert(index, scripts)

  def checkscript(self, contents, index):
    "Check if the current element is a sub- or superscript."
    if len(contents) <= index:
      return False
    return isinstance(contents[index], SymbolFunction)

  def getscript(self, contents, index):
    "Get the sub- or superscript."
    bit = contents[index]
    bit.output.tag += ' class="script"'
    del contents[index]
    return bit

class BracketCommand(OneParamFunction):
  "A command which defines a bracket."

  commandmap = FormulaConfig.bracketcommands

  def parsebit(self, pos):
    "Parse the bracket."
    OneParamFunction.parsebit(self, pos)

class BracketProcessor(MathsProcessor):
  "A processor for bracket commands."

  directions = {'left': 1, 'right': -1}

  def process(self, contents, index):
    "Convert the bracket using Unicode pieces, if possible."
    if not isinstance(contents[index], BracketCommand):
      return
    self.checkarray(contents, index, 'left')
    self.checkarray(contents, index, 'right')

  def checkarray(self, contents, index, direction):
    "Check for the right command, and an array in the given direction."
    command = contents[index]
    if command.command != '\\' + direction:
      return
    newindex = index + self.directions[direction]
    if newindex < 0 or newindex >= len(contents):
      return
    begin = contents[newindex]
    if not isinstance(begin, BeginCommand):
      return
    array = begin.array
    if not isinstance(array, MultiRowFormula):
      Trace.error('BeginCommand does not contain a MultiRowFormula')
      return False
    self.processarray(command, array, direction)

  def processarray(self, command, array, direction):
    "Process a bracket command with an array next to it."
    character = command.extracttext()
    command.output = EmptyOutput()
    bracket = BigBracket(len(array.rows), character)
    for index, row in enumerate(array.rows):
      cell = bracket.getcell(index, direction)
      if self.directions[direction] == 1:
        row.contents.insert(0, cell)
      else:
        row.contents.append(cell)

class BinomialCell(CommandBit):
  "A cell in a binomial function."

  def setfactory(self, factory):
    "Set the factory."
    self.output = TaggedOutput().settag('span class="binomcell"', True)
    return CommandBit.setfactory(self, factory)

  def parsebit(self, pos):
    "Parse a parameter and make it into a binomial cell."
    self.parseparameter(pos)

  def constant(self, constant):
    "Set a constant as only contents."
    self.contents = [FormulaConstant(constant)]

class BinomialRow(CommandBit):
  "A row for a binomial function."

  def create(self, left, middle, right):
    "Set the row contents."
    self.output = TaggedOutput().settag('span class="binomrow"', True)
    self.contents = [left, middle, right]
    return self

class BinomialFunction(CommandBit):
  "A binomial function which needs pretty decorating."

  commandmap = FormulaConfig.binomialfunctions

  def parsebit(self, pos):
    "Parse two parameters and decorate them."
    self.output = TaggedOutput().settag('span class="binomial"', True)
    leftbracket = BigBracket(3, self.translated[0])
    rightbracket = BigBracket(3, self.translated[1])
    for index in range(3):
      left = leftbracket.getcell(index, 'l')
      right = rightbracket.getcell(index, 'r')
      cell = BinomialCell().setfactory(self.factory)
      if index == 1:
        cell.constant(u' ')
      else:
        cell.parsebit(pos)
      self.add(BinomialRow().create(left, cell, right))


FormulaCommand.types += [
    DecoratingFunction, CombiningFunction, LimitCommand, BracketCommand,
    BinomialFunction,
    ]

FormulaProcessor.processors += [
    LimitsProcessor(), BracketProcessor(),
    ]



class ContainerFactory(object):
  "Creates containers depending on the first line"

  def __init__(self):
    "Read table that convert start lines to containers"
    types = dict()
    for start, typename in ContainerConfig.starts.iteritems():
      types[start] = globals()[typename]
    self.tree = ParseTree(types)

  def createcontainer(self, reader):
    "Parse a single container."
    #Trace.debug('processing "' + reader.currentline().strip() + '"')
    if reader.currentline() == '':
      reader.nextline()
      return None
    container = Cloner.create(self.tree.find(reader))
    container.start = reader.currentline().strip()
    self.parse(container, reader)
    return container

  def parse(self, container, reader):
    "Parse a container"
    parser = container.parser
    parser.parent = container
    parser.ending = self.getending(container)
    parser.factory = self
    container.header = parser.parseheader(reader)
    container.begin = parser.begin
    self.parsecontents(container, reader)
    container.parameters = parser.parameters
    container.parser = None

  def parsecontents(self, container, reader):
    "Parse the contents of a container."
    contents = container.parser.parse(reader)
    if isinstance(contents, basestring):
      # read a string, set as parsed
      container.parsed = contents
      container.contents = []
    else:
      container.contents = contents

  def getending(self, container):
    "Get the ending for a container"
    split = container.start.split()
    if len(split) == 0:
      return None
    start = split[0]
    if start in ContainerConfig.startendings:
      return ContainerConfig.startendings[start]
    classname = container.__class__.__name__
    if classname in ContainerConfig.endings:
      return ContainerConfig.endings[classname]
    if hasattr(container, 'ending'):
      Trace.error('Pending ending in ' + container.__class__.__name__)
      return container.ending
    return None

class ParseTree(object):
  "A parsing tree"

  default = '~~default~~'

  def __init__(self, types):
    "Create the parse tree"
    self.root = dict()
    for start, type in types.iteritems():
      self.addstart(type, start)

  def addstart(self, type, start):
    "Add a start piece to the tree"
    tree = self.root
    for piece in start.split():
      if not piece in tree:
        tree[piece] = dict()
      tree = tree[piece]
    if ParseTree.default in tree:
      Trace.error('Start ' + start + ' duplicated')
    tree[ParseTree.default] = type

  def find(self, reader):
    "Find the current sentence in the tree"
    branches = self.matchline(reader.currentline())
    while not ParseTree.default in branches[-1]:
      branches.pop()
    last = branches[-1]
    return last[ParseTree.default]

  def matchline(self, line):
    "Match a given line against the tree, as deep as possible."
    branches = [self.root]
    for piece in line.split(' '):
      current = branches[-1]
      piece = piece.rstrip('>')
      if piece in current:
        branches.append(current[piece])
      else:
        return branches
    return branches







class TOCEntry(Container):
  "A container for a TOC entry."

  def __init__(self):
    Container.__init__(self)
    self.branches = []

  def create(self, container):
    "Create the TOC entry for a container, consisting of a single link."
    if container.partkey.header:
      return self.header(container)
    self.contents = [self.createlink(container)]
    self.output = TaggedOutput().settag('div class="toc"', True)
    self.partkey = container.partkey
    return self

  def header(self, container):
    "Create a TOC entry for header and footer (0 depth)."
    self.partkey = container.partkey
    self.output = EmptyOutput()
    return self

  def createlink(self, container):
    "Create the link that will make the whole TOC entry."
    labels = container.searchall(Label)
    link = Link()
    if len(labels) == 0 or Options.toc:
      link.url = Options.toctarget + '#' + container.partkey.partkey
    else:
      label = labels[0]
      link.destination = label
    if container.partkey.tocentry:
      link.complete(container.partkey.tocentry)
    titlecontents = self.gettitlecontents(container)
    if titlecontents:
      if Options.notoclabels:
        separator = u'. '
      else:
        separator = u': '
      if container.partkey.tocentry:
        link.contents.append(Constant(separator))
      link.contents += titlecontents
    return link

  def gettitlecontents(self, container):
    "Get the title of the container."
    if not container.partkey.showtitle:
      return None
    shorttitles = container.searchall(ShortTitle)
    if len(shorttitles) > 0:
      contents = []
      for shorttitle in shorttitles:
        contents += shorttitle.contents
      return contents
    extractor = ContainerExtractor(TOCConfig.extracttitle)
    captions = container.searchall(Caption)
    if len(captions) == 1:
      return extractor.extract(captions[0])
    return extractor.extract(container)

  def __unicode__(self):
    "Return a printable representation."
    if not self.partkey.tocentry:
      return 'Unnamed TOC entry'
    return 'TOC entry: ' + self.partkey.tocentry

class Indenter(object):
  "Manages and writes indentation for the TOC."

  def __init__(self):
    self.depth = 0

  def getindent(self, depth):
    indent = ''
    if depth > self.depth:
      indent = self.openindent(depth - self.depth)
    elif depth < self.depth:
      indent = self.closeindent(self.depth - depth)
    self.depth = depth
    return Constant(indent)

  def openindent(self, times):
    "Open the indenting div a few times."
    indent = ''
    for i in range(times):
      indent += '<div class="tocindent">\n'
    return indent

  def closeindent(self, times):
    "Close the indenting div a few times."
    indent = ''
    for i in range(times):
      indent += '</div>\n'
    return indent

class IndentedEntry(Container):
  "An entry with an indentation."

  def __init__(self):
    self.output = ContentsOutput()

  def create(self, indent, entry):
    "Create the indented entry."
    self.contents = [indent, entry]
    return self

class TOCTree(object):
  "A tree that contains the full TOC."

  def __init__(self):
    self.tree = []
    self.branches = []

  def store(self, entry):
    "Place the entry in a tree of entries."
    while len(self.tree) < entry.partkey.level:
      self.tree.append(None)
    if len(self.tree) > entry.partkey.level:
      self.tree = self.tree[:entry.partkey.level]
    stem = self.findstem()
    if len(self.tree) == 0:
      self.branches.append(entry)
    self.tree.append(entry)
    if stem:
      entry.stem = stem
      stem.branches.append(entry)

  def findstem(self):
    "Find the stem where our next element will be inserted."
    for element in reversed(self.tree):
      if element:
        return element
    return None

class TOCConverter(object):
  "A converter from containers to TOC entries."

  cache = dict()
  tree = TOCTree()

  def __init__(self):
    self.indenter = Indenter()

  def convertindented(self, container):
    "Convert a container into an indented TOC entry."
    entry = self.convert(container)
    if not entry:
      return BlackBox()
    return self.indent(entry)

  def indent(self, entry):
    "Indent a TOC entry."
    indent = self.indenter.getindent(entry.partkey.level)
    return IndentedEntry().create(indent, entry)

  def convert(self, container):
    "Convert a container to a TOC entry."
    if not container.partkey:
      return None
    if container.partkey.partkey in self.cache:
      return TOCConverter.cache[container.partkey.partkey]
    if container.partkey.level > DocumentParameters.tocdepth:
      return None
    entry = TOCEntry().create(container)
    TOCConverter.cache[container.partkey.partkey] = entry
    TOCConverter.tree.store(entry)
    return entry







class Basket(object):
  "A basket to place a set of containers. Can write them, store them..."

  def setwriter(self, writer):
    self.writer = writer
    return self

class WriterBasket(Basket):
  "A writer of containers. Just writes them out to a writer."

  def write(self, container):
    "Write a container to the line writer."
    self.writer.write(container.gethtml())

  def finish(self):
    "Mark as finished."
    self.writer.close()

class KeeperBasket(Basket):
  "Keeps all containers stored."

  def __init__(self):
    self.contents = []

  def write(self, container):
    "Keep the container."
    self.contents.append(container)

  def finish(self):
    "Finish the basket by flushing to disk."
    self.flush()

  def flush(self):
    "Flush the contents to the writer."
    for container in self.contents:
      self.writer.write(container.gethtml())

class TOCBasket(Basket):
  "A basket to place the TOC of a document."

  def __init__(self):
    self.converter = TOCConverter()

  def setwriter(self, writer):
    Basket.setwriter(self, writer)
    Options.nocopy = True
    self.writer.write(LyXHeader().process().gethtml())
    return self

  def write(self, container):
    "Write the table of contents for a container."
    entry = self.converter.convertindented(container)
    self.writer.write(entry.gethtml())

  def finish(self):
    "Mark as finished."
    self.writer.write(LyXFooter().gethtml())






class IntegralProcessor(object):
  "A processor for an integral document."

  def __init__(self):
    "Create the processor for the integral contents."
    self.storage = []

  def locate(self, container):
    "Locate only containers of the processed type."
    return isinstance(container, self.processedtype)

  def store(self, container):
    "Store a new container."
    self.storage.append(container)

  def process(self):
    "Process the whole storage."
    for container in self.storage:
      self.processeach(container)

class IntegralTOC(IntegralProcessor):
  "A processor for an integral TOC."

  processedtype = TableOfContents
  tocentries = []

  def processeach(self, toc):
    "Fill in a Table of Contents."
    converter = TOCConverter()
    for container in PartKeyGenerator.partkeyed:
      toc.add(converter.convertindented(container))
    # finish off with the footer to align indents
    toc.add(converter.convertindented(LyXFooter()))

  def writetotoc(self, entries, toc):
    "Write some entries to the TOC."
    for entry in entries:
      toc.contents.append(entry)

class IntegralBiblioEntry(IntegralProcessor):
  "A processor for an integral bibliography entry."

  processedtype = BiblioEntry

  def processeach(self, entry):
    "Process each entry."
    number = NumberGenerator.generator.generate('integralbib')
    link = Link().complete('cite', 'biblio-' + number, type='biblioentry')
    link.contents = entry.citeref
    entry.contents = [Constant('['), link, Constant('] ')]
    if entry.key in BiblioCite.cites:
      for cite in BiblioCite.cites[entry.key]:
        cite.contents = entry.citeref
        cite.anchor = 'cite-' + number
        cite.destination = link

class IntegralFloat(IntegralProcessor):
  "Store all floats in the document by type."

  processedtype = Float
  bytype = dict()

  def processeach(self, float):
    "Store each float by type."
    if not float.type in IntegralFloat.bytype:
      IntegralFloat.bytype[float.type] = []
    IntegralFloat.bytype[float.type].append(float)

class IntegralListOf(IntegralProcessor):
  "A processor for an integral list of floats."

  processedtype = ListOf

  def processeach(self, listof):
    "Fill in a list of floats."
    listof.output = TaggedOutput().settag('div class="fulltoc"', True)
    if not listof.type in IntegralFloat.bytype:
      Trace.message('No floats of type ' + listof.type)
      return
    for float in IntegralFloat.bytype[listof.type]:
      entry = self.processfloat(float)
      if entry:
        listof.contents.append(entry)

  def processfloat(self, float):
    "Get an entry for the list of floats."
    if not float.isparent():
      return None
    return TOCEntry().create(float)

class IntegralReference(IntegralProcessor):
  "A processor for a reference to a label."

  processedtype = Reference

  def processeach(self, reference):
    "Extract the text of the original label."
    text = reference.destination.labelnumber
    if text:
      reference.labelnumber = text
      reference.format()

class MemoryBasket(KeeperBasket):
  "A basket which stores everything in memory, processes it and writes it."

  def __init__(self):
    "Create all processors in one go."
    KeeperBasket.__init__(self)
    self.processors = [
        IntegralTOC(), IntegralBiblioEntry(),
        IntegralFloat(), IntegralListOf(), IntegralReference(),
        ]

  def finish(self):
    "Process everything which cannot be done in one pass and write to disk."
    self.process()
    self.flush()

  def process(self):
    "Process everything with the integral processors."
    self.searchintegral()
    for processor in self.processors:
      processor.process()

  def searchintegral(self):
    "Search for all containers for all integral processors."
    for container in self.contents:
      # container.tree()
      if self.integrallocate(container):
        self.integralstore(container)
      container.locateprocess(self.integrallocate, self.integralstore)

  def integrallocate(self, container):
    "Locate all integrals."
    for processor in self.processors:
      if processor.locate(container):
        return True
    return False

  def integralstore(self, container):
    "Store a container in one or more processors."
    for processor in self.processors:
      if processor.locate(container):
        processor.store(container)







class SplitPartLink(IntegralProcessor):
  "A link processor for multi-page output."

  processedtype = Link

  def processeach(self, link):
    "Process each link and add the current page."
    link.page = self.page

class UpAnchor(Link):
  "An anchor to the top of the page for the up links."

  def create(self, container):
    "Create the up anchor based on the first container."
    if not container.partkey:
      Trace.error('No part key for ' + unicode(container))
      return None
    return self.createliteral(container.partkey.tocentry)

  def createmain(self):
    "Create the up anchor for the main page."
    return self.createliteral(Translator.translate('main-page'))

  def createliteral(self, literal):
    "Create the up anchor based on a literal string."
    self.complete('', '')
    self.output = EmptyOutput()
    self.partkey = PartKey().createanchor(literal)
    return self

class SplitPartNavigation(object):
  "Used to create the navigation links for a new split page."

  def __init__(self):
    self.upanchors = []
    self.lastcontainer = None
    self.nextlink = None
    self.lastnavigation = None

  def writefirstheader(self, basket):
    "Write the first header to the basket."
    anchor = self.createmainanchor()
    basket.write(anchor)
    basket.write(self.createnavigation(anchor))

  def writeheader(self, basket, container):
    "Write the header to the basket."
    basket.write(LyXHeader().process())
    basket.write(self.currentupanchor(container))
    basket.write(self.createnavigation(container))

  def writefooter(self, basket):
    "Write the footer to the basket."
    if self.lastnavigation:
      basket.write(self.lastnavigation)
    basket.write(LyXFooter())

  def createnavigation(self, container):
    "Create the navigation bar with all links."
    prevlink = Link().complete(' ', 'prev', type='prev')
    if self.nextlink:
      self.setlinkname(prevlink, Translator.translate('prev'), self.lastcontainer)
      self.setlinkname(self.nextlink, Translator.translate('next'), container)
      prevlink.setmutualdestination(self.nextlink)
    self.nextlink = Link().complete(' ', Translator.translate('next'), type='next')
    uplink = Link().complete(Translator.translate('up'), url='', type='up')
    self.setlinkname(uplink, Translator.translate('up'), self.getupdestination(container))
    uplink.destination = self.getupdestination(container)
    prevcontainer = TaggedText().complete([prevlink], 'span class="prev"')
    nextcontainer = TaggedText().complete([self.nextlink], 'span class="next"')
    upcontainer = TaggedText().complete([uplink], 'span class="up"')
    contents = [prevcontainer, Constant('\n'), upcontainer, Constant('\n'), nextcontainer]
    header = TaggedText().complete(contents, 'div class="splitheader"', True)
    self.lastcontainer = container
    self.lastnavigation = header
    return header
  
  def currentupanchor(self, container):
    "Update the internal list of up anchors, and return the current one."
    level = self.getlevel(container)
    while len(self.upanchors) > level:
      del self.upanchors[-1]
    while len(self.upanchors) < level:
      self.upanchors.append(self.upanchors[-1])
    upanchor = UpAnchor().create(container)
    self.upanchors.append(upanchor)
    return upanchor

  def createmainanchor(self):
    "Create the up anchor to the main page."
    mainanchor = UpAnchor().createmain()
    self.upanchors.append(mainanchor)
    return mainanchor

  def getupdestination(self, container):
    "Get the name of the up page."
    level = self.getlevel(container)
    if len(self.upanchors) < level:
      uppage = self.upanchors[-1]
    else:
      uppage = self.upanchors[level - 1]
    return uppage

  def getlevel(self, container):
    "Get the level of the container."
    if not container.partkey:
      return 1
    else:
      return container.partkey.level + 1

  def setlinkname(self, link, type, container):
    "Set the name on the link."
    if not container.partkey:
      Trace.error('No part key for link name ' + unicode(container))
      return
    link.contents = [Constant(type + ': ' + container.partkey.tocentry)]

class SplitTOCBasket(MemoryBasket):
  "A memory basket which contains a split table of contents."

  def __init__(self):
    MemoryBasket.__init__(self)
    self.entrycount = 0
    self.root = None
    self.converter = TOCConverter()

  def write(self, container):
    "Keep track of numbered layouts."
    MemoryBasket.write(self, container)
    if not container.partkey:
      return
    if container.partkey.header:
      return
    entry = self.converter.convert(container)
    if not entry:
      return
    self.entrycount += 1
    self.root = entry

  def addtoc(self):
    "Add the table of contents if necessary."
    if self.entrycount != 1:
      return
    if self.root.branches == []:
      return
    text = Translator.translate('toc-for') + self.root.partkey.tocentry
    toc = TableOfContents().create(text)
    self.addbranches(self.root, toc)
    toc.add(self.converter.convertindented(LyXFooter()))
    self.write(toc)

  def addbranches(self, entry, toc):
    "Add an entry and all of its branches to the table of contents."
    for branch in entry.branches:
      toc.add(self.converter.indent(branch))
      self.addbranches(branch, toc)
  
class SplitPartBasket(Basket):
  "A basket used to split the output in different files."

  baskets = []

  def setwriter(self, writer):
    if not hasattr(writer, 'filename') or not writer.filename:
      Trace.error('Cannot use standard output for split output; ' +
          'please supply an output filename.')
      exit()
    self.writer = writer
    self.filename = writer.filename
    self.converter = TOCConverter()
    self.basket = MemoryBasket()
    self.basket.page = writer.filename
    return self

  def write(self, container):
    "Write a container, possibly splitting the file."
    self.basket.write(container)

  def finish(self):
    "Process the whole basket, create page baskets and flush all of them."
    self.basket.process()
    basket = self.firstbasket()
    navigation = SplitPartNavigation()
    for container in self.basket.contents:
      if self.mustsplit(container):
        filename = self.getfilename(container)
        Trace.debug('New page ' + filename)
        basket.addtoc()
        navigation.writefooter(basket)
        basket = self.addbasket(filename)
        navigation.writeheader(basket, container)
      basket.write(container)
      if self.afterheader(container):
        navigation.writefirstheader(basket)
    for basket in self.baskets:
      basket.process()
    for basket in self.baskets:
      basket.flush()

  def afterheader(self, container):
    "Find out if this is the header on the file."
    return isinstance(container, LyXHeader)

  def firstbasket(self):
    "Create the first basket."
    return self.addbasket(self.filename, self.writer)

  def addbasket(self, filename, writer = None):
    "Add a new basket."
    if not writer:
      writer = LineWriter(filename)
    basket = SplitTOCBasket()
    basket.setwriter(writer)
    self.baskets.append(basket)
    # set the page name everywhere
    basket.page = filename
    splitpartlink = SplitPartLink()
    splitpartlink.page = os.path.basename(basket.page)
    basket.processors = [splitpartlink]
    return basket

  def mustsplit(self, container):
    "Find out if the oputput file has to be split at this entry."
    if not container.partkey:
      return False
    if not container.partkey.filename:
      return False
    return True

  def getfilename(self, container):
    "Get the new file name for a given container."
    partname = container.partkey.filename
    base, extension = os.path.splitext(self.filename)
    return base + '-' + partname + extension






class PostFormula(object):
  "Postprocess a formula"

  processedclass = Formula

  def postprocess(self, last, formula, next):
    "Postprocess any formulae"
    if Options.jsmath or Options.mathjax:
      return formula
    self.postnumbering(formula)
    return formula

  def postnumbering(self, formula):
    "Check if it's a numbered equation, insert number."
    if formula.header[0] != 'numbered':
      return
    functions = formula.searchremove(LabelFunction)
    if len(functions) == 0:
      label = self.createlabel(formula)
    elif len(functions) == 1:
      label = self.createlabel(formula, functions[0])
    if len(functions) <= 1:
      label.parent = formula
      formula.contents.insert(0, label)
      return
    for function in functions:
      label = self.createlabel(formula, function)
      row = self.searchrow(function)
      label.parent = row
      row.contents.insert(0, label)

  def createlabel(self, formula, function = None):
    "Create a new label for a formula."
    "Add a label to a formula."
    number = NumberGenerator.chaptered.generate('formula')
    partkey = PartKey().createformula(number)
    if not formula.partkey:
      formula.partkey = partkey
    if not function:
      label = Label()
      label.create(partkey.tocentry + ' ', 'eq-' + number, type="eqnumber")
    else:
      label = function.label
      label.complete(partkey.tocentry + ' ')
    return label

  def searchrow(self, function):
    "Search for the row that contains the label function."
    if isinstance(function.parent, Formula) or isinstance(function.parent, FormulaRow):
      return function.parent
    return self.searchrow(function.parent)

Postprocessor.stages.append(PostFormula)



class eLyXerConverter(object):
  "Converter for a document in a lyx file. Places all output in a given basket."

  def __init__(self):
    self.filtering = False

  def setio(self, ioparser):
    "Set the InOutParser"
    self.reader = ioparser.getreader()
    self.basket = self.getbasket()
    self.basket.setwriter(ioparser.getwriter())
    return self

  def getbasket(self):
    "Get the appropriate basket for the current options."
    if Options.toc:
      return TOCBasket()
    if Options.splitpart:
      return SplitPartBasket()
    if Options.memory:
      return MemoryBasket()
    return WriterBasket()

  def embed(self, reader):
    "Embed the results from a reader into a memory basket."
    "Header and footer are ignored. Useful for embedding one document inside another."
    self.filtering = True
    self.reader = reader
    self.basket = MemoryBasket()
    return self

  def convert(self):
    "Perform the conversion for the document"
    try:
      self.processcontents()
    except (Exception):
      version = '[eLyXer version ' + GeneralConfig.version['number']
      version += ' (' + GeneralConfig.version['date'] + ') in '
      version += Options.location + '] '
      Trace.error(version)
      Trace.error('Conversion failed at ' + self.reader.currentline())
      raise

  def processcontents(self):
    "Parse the contents and write it by containers"
    factory = ContainerFactory()
    processor = Processor(self.filtering)
    while not self.reader.finished():
      container = factory.createcontainer(self.reader)
      result = processor.process(container)
      self.writecontainer(result)
    result = processor.postprocess(None)
    self.writecontainer(result)
    if not self.filtering:
      self.basket.finish()

  def writecontainer(self, container):
    "Write each container to the correct basket."
    if not container:
      return
    includes = container.searchremove(IncludeInset)
    self.basket.write(container)
    # recursive processing for IncludeInset
    for include in includes:
      for element in include.contents:
        self.basket.write(element)

  def getcontents(self):
    "Return the contents of the basket."
    return self.basket.contents

  def __unicode__(self):
    "Printable representation."
    string = 'Converter with filtering ' + unicode(self.filtering)
    string += ' and basket ' + unicode(self.basket)
    return string

class InOutParser(object):
  "Parse in and out arguments"

  def __init__(self):
    self.filein = sys.stdin
    self.fileout = sys.stdout

  def parse(self, args):
    "Parse command line arguments"
    self.filein = sys.stdin
    self.fileout = sys.stdout
    if len(args) < 2:
      Trace.quietmode = True
    if len(args) > 0:
      self.filein = args[0]
      del args[0]
      self.readdir(self.filein, 'directory')
    else:
      Options.directory = '.'
    if len(args) > 0:
      self.fileout = args[0]
      del args[0]
      self.readdir(self.fileout, 'destdirectory')
    else:
      Options.destdirectory = '.'
    if len(args) > 0:
      raise Exception('Unused arguments: ' + unicode(args))
    return self

  def getreader(self):
    "Get the resulting reader."
    return LineReader(self.filein)

  def getwriter(self):
    "Get the resulting writer."
    return LineWriter(self.fileout)

  def readdir(self, filename, diroption):
    "Read the current directory if needed"
    if getattr(Options, diroption) != None:
      return
    setattr(Options, diroption, os.path.dirname(filename))
    if getattr(Options, diroption) == '':
      setattr(Options, diroption, '.')

class NullWriter(object):
  "A writer that goes nowhere."

  def write(self, list):
    "Do nothing."
    pass

class ConverterFactory(object):
  "Create a converter fit for converting a filename and embedding the result."

  def create(self, container):
    "Create a converter for a given container, with filename"
    " and possibly other parameters."
    fullname = os.path.join(Options.directory, container.filename)
    reader = LineReader(container.filename)
    if 'firstline' in container.lstparams:
      reader.setstart(int(container.lstparams['firstline']))
    if 'lastline' in container.lstparams:
      reader.setend(int(container.lstparams['lastline']))
    return eLyXerConverter().embed(reader)

IncludeInset.converterfactory = ConverterFactory()



def convertdoc(args):
  "Read a whole document and write it"
  Options().parseoptions(args)
  ioparser = InOutParser().parse(args)
  converter = eLyXerConverter().setio(ioparser)
  converter.convert()

def main():
  "Main function, called if invoked from the command line"
  convertdoc(list(sys.argv))

if __name__ == '__main__':
  main()

