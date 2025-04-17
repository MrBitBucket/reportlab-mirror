"""Test TrueType font subsetting & embedding code.

This test uses a sample font (Vera.ttf) taken from Bitstream which is called Vera
Serif Regular and is covered under the license in ../fonts/bitstream-vera-license.txt.
"""
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation, NearTestCase, rlSkipUnless
if __name__=='__main__':
    setOutDir(__name__)
import unittest, os
from io import BytesIO
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfgen.textobject import PDFTextObject
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfdoc import PDFDocument, PDFError
from reportlab.pdfbase.ttfonts import TTFont, TTFontFace, TTFontFile, TTFOpenFile, \
                                      TTFontParser, TTFontMaker, TTFError, \
                                      makeToUnicodeCMap, \
                                      FF_SYMBOLIC, FF_NONSYMBOLIC, \
                                      calcChecksum, add32, uharfbuzz, shapeFragWord, \
                                      ShapedFragWord, ShapedStr, ShapeData, _sdSimple, \
                                      freshTTFont
from reportlab.platypus.paragraph import Paragraph, _HSFrag
from reportlab.lib.styles import getSampleStyleSheet
import zlib, base64
from reportlab import rl_config
from reportlab.lib.utils import int2Byte
from reportlab.lib.abag import ABag

try:
    TTFont("DejaVuSans", "DejaVuSans.ttf")
except:
    haveDejaVuSans = False
else:
    haveDejaVuSans = True

def utf8(code):
    "Convert a given UCS character index into UTF-8"
    return chr(code).encode('utf8')

def _simple_subset_generation(fn,npages,alter=0,fonts=('Vera','VeraBI')):
    c = Canvas(outputfile(fn))
    c.setFont('Helvetica', 30)
    c.drawString(100,700, 'Unicode TrueType Font Test %d pages' % npages)
    # Draw a table of Unicode characters
    for p in range(npages):
        for fontName in fonts:
            c.setFont(fontName, 10)
            for i in range(32):
                for j in range(32):
                    ch = chr(i * 32 + j+p*alter)
                    c.drawString(80 + j * 13 + int(j / 16.0) * 4, 600 - i * 13 - int(i / 8.0) * 8, ch)
        c.showPage()
    c.save()

def show_all_glyphs(fn,fontName='Vera'):
    c = Canvas(outputfile(fn))
    c.setFont('Helvetica', 20)
    c.drawString(72,c._pagesize[1]-30, 'Unicode TrueType Font Test %s' % fontName)
    from reportlab.pdfbase.pdfmetrics import _fonts
    font = _fonts[fontName]
    doc = c._doc
    kfunc = font.face.charToGlyph.keys
    for s in sorted(list(kfunc())):
        if s<0x10000:
            font.splitString(chr(s),doc)
    state = font.state[doc]
    cn = {}
    #print('len(assignments)=%d'%  len(state.assignments))
    nzero = 0
    ifunc = state.assignments.items
    for code, n in sorted(list(ifunc())):
        if code==0: nzero += 1
        cn[n] = chr(code)
    if nzero>1: print('%s there were %d zero codes' % (fontName,nzero))


    ymin = 10*12
    y = y0 = c._pagesize[1] - 72
    for nss,subset in enumerate(state.subsets):
        if y<ymin:
            c.showPage()
            y = y0
        c.setFont('Helvetica', 10)
        x = 72
        c.drawString(x,y,'Subset %d len=%d' % (nss,len(subset)))
        #print('Subset %d len=%d' % (nss,len(subset)))
        c.setFont(fontName, 10)
        for i, code in enumerate(subset):
            if i%32 == 0:
                y -= 12
                x = 72
            c.drawString(x,y,chr(code))
            x += 13
        y -= 18

    c.showPage()
    c.save()

class TTFontsTestCase(unittest.TestCase):
    "Make documents with TrueType fonts"

    def testTTF(self):
        "Test PDF generation with TrueType fonts"
        pdfmetrics.registerFont(TTFont("Vera", "Vera.ttf"))
        pdfmetrics.registerFont(TTFont("VeraBI", "VeraBI.ttf"))
        if haveDejaVuSans:
            pdfmetrics.registerFont(freshTTFont('DejaVuSans', 'DejaVuSans.ttf'))
            show_all_glyphs('test_pdfbase_ttfonts_dejavusans.pdf',fontName='DejaVuSans')
        show_all_glyphs('test_pdfbase_ttfonts_vera.pdf',fontName='Vera')
        _simple_subset_generation('test_pdfbase_ttfonts1.pdf',1)
        _simple_subset_generation('test_pdfbase_ttfonts3.pdf',3)
        _simple_subset_generation('test_pdfbase_ttfonts35.pdf',3,5)

        # Do it twice with the same font object
        c = Canvas(outputfile('test_pdfbase_ttfontsadditional.pdf'))
        # Draw a table of Unicode characters
        c.setFont('Vera', 10)
        c.drawString(100, 700, b'Hello, ' + utf8(0xffee))
        c.save()

    def testSameTTFDifferentName(self):
        "Test PDF generation with TrueType fonts"
        pdfmetrics.registerFont(TTFont("Vera", "Vera.ttf"))
        pdfmetrics.registerFont(TTFont("MyVera", "Vera.ttf"))

        # Do it twice with the same font object
        c = Canvas(outputfile('test_pdfbase_ttfontsduplicate.pdf'))
        # Draw a table of Unicode characters
        c.setFont('Vera', 10)
        c.drawString(100, 700, b'Hello World')
        c.setFont('MyVera', 10)
        c.drawString(100, 688, b'Hello World')
        c.save()

class TTFontFileTestCase(NearTestCase):
    "Tests TTFontFile, TTFontParser and TTFontMaker classes"

    def testFontFileFailures(self):
        "Tests TTFontFile constructor error checks"
        self.assertRaises(TTFError, TTFontFile, "nonexistent file")
        self.assertRaises(TTFError, TTFontFile, BytesIO(b""))
        self.assertRaises(TTFError, TTFontFile, BytesIO(b"invalid signature"))
        self.assertRaises(TTFError, TTFontFile, BytesIO(b"OTTO - OpenType not supported yet"))
        self.assertRaises(TTFError, TTFontFile, BytesIO(b"\0\1\0\0"))

    def testFontFileReads(self):
        "Tests TTFontParset.read_xxx"

        class FakeTTFontFile(TTFontParser):
            def __init__(self, data):
                self._ttf_data = data
                self._pos = 0

        ttf = FakeTTFontFile(b"\x81\x02\x03\x04" b"\x85\x06" b"ABCD" b"\x7F\xFF" b"\x80\x00" b"\xFF\xFF")
        self.assertEqual(ttf.read_ulong(), 0x81020304) # big-endian
        self.assertEqual(ttf._pos, 4)
        self.assertEqual(ttf.read_ushort(), 0x8506)
        self.assertEqual(ttf._pos, 6)
        self.assertEqual(ttf.read_tag(), 'ABCD')
        self.assertEqual(ttf._pos, 10)
        self.assertEqual(ttf.read_short(), 0x7FFF)
        self.assertEqual(ttf.read_short(), -0x8000)
        self.assertEqual(ttf.read_short(), -1)

    def testFontFile(self):
        "Tests TTFontFile and TTF parsing code"
        ttf = TTFontFile("Vera.ttf")
        self.assertEqual(ttf.name, b"BitstreamVeraSans-Roman")
        self.assertEqual(ttf.flags, FF_SYMBOLIC)
        self.assertEqual(ttf.italicAngle, 0.0)
        self.assertNear(ttf.ascent,759.765625)
        self.assertNear(ttf.descent,-240.234375)
        self.assertEqual(ttf.capHeight, 759.765625)
        self.assertNear(ttf.bbox, [-183.10546875, -235.83984375, 1287.109375, 928.22265625])
        self.assertEqual(ttf.stemV, 87)
        self.assertEqual(ttf.defaultWidth, 600.09765625)

    def testAdd32(self):
        "Test add32"
        self.assertEqual(add32(10, -6), 4)
        self.assertEqual(add32(6, -10), -4&0xFFFFFFFF)
        self.assertEqual(add32(0x80000000, -1), 0x7FFFFFFF)
        self.assertEqual(add32(0x7FFFFFFF, 1), 0x80000000)

    def testChecksum(self):
        "Test calcChecksum function"
        self.assertEqual(calcChecksum(b""), 0)
        self.assertEqual(calcChecksum(b"\1"), 0x01000000)
        self.assertEqual(calcChecksum(b"\x01\x02\x03\x04\x10\x20\x30\x40"), 0x11223344)
        self.assertEqual(calcChecksum(b"\x81"), 0x81000000)
        self.assertEqual(calcChecksum(b"\x81\x02"), 0x81020000)
        self.assertEqual(calcChecksum(b"\x81\x02\x03"), 0x81020300)
        self.assertEqual(calcChecksum(b"\x81\x02\x03\x04"), 0x81020304)
        self.assertEqual(calcChecksum(b"\x81\x02\x03\x04\x05"), 0x86020304)
        self.assertEqual(calcChecksum(b"\x41\x02\x03\x04\xD0\x20\x30\x40"), 0x11223344)
        self.assertEqual(calcChecksum(b"\xD1\x02\x03\x04\x40\x20\x30\x40"), 0x11223344)
        self.assertEqual(calcChecksum(b"\x81\x02\x03\x04\x90\x20\x30\x40"), 0x11223344)
        self.assertEqual(calcChecksum(b"\x7F\xFF\xFF\xFF\x00\x00\x00\x01"), 0x80000000)

    def testFontFileChecksum(self):
        "Tests TTFontFile and TTF parsing code"
        F = TTFOpenFile("Vera.ttf")[1].read()
        TTFontFile(BytesIO(F), validate=1) # should not fail
        F1 = F[:12345] + b"\xFF" + F[12346:] # change one byte
        self.assertRaises(TTFError, TTFontFile, BytesIO(F1), validate=1)
        F1 = F[:8] + b"\xFF" + F[9:] # change one byte
        self.assertRaises(TTFError, TTFontFile, BytesIO(F1), validate=1)

    def testSubsetting(self):
        "Tests TTFontFile and TTF parsing code"
        ttf = TTFontFile("Vera.ttf")
        subset = ttf.makeSubset([0x41, 0x42])
        subset = TTFontFile(BytesIO(subset), 0)
        for tag in ('cmap', 'head', 'hhea', 'hmtx', 'maxp', 'name', 'OS/2',
                    'post', 'cvt ', 'fpgm', 'glyf', 'loca', 'prep'):
            self.assertTrue(subset.get_table(tag))

        subset.seek_table('loca')
        for n in range(4):
            pos = subset.read_ushort()    # this is actually offset / 2
            self.assertFalse(pos % 2 != 0, "glyph %d at +%d should be long aligned" % (n, pos * 2))

        self.assertEqual(subset.name, b"BitstreamVeraSans-Roman")
        self.assertEqual(subset.flags, FF_SYMBOLIC)
        self.assertEqual(subset.italicAngle, 0.0)
        self.assertNear(subset.ascent,759.765625)
        self.assertNear(subset.descent,-240.234375)
        self.assertEqual(subset.capHeight, 759.765625)
        self.assertNear(subset.bbox, [-183.10546875, -235.83984375, 1287.109375, 928.22265625])
        self.assertEqual(subset.stemV, 87)

    def testFontMaker(self):
        "Tests TTFontMaker class"
        ttf = TTFontMaker()
        ttf.add("ABCD", b"xyzzy")
        ttf.add("QUUX", b"123")
        ttf.add("head", b"12345678xxxx")
        stm = ttf.makeStream()
        ttf = TTFontParser(BytesIO(stm), 0)
        self.assertEqual(ttf.get_table("ABCD"), b"xyzzy")
        self.assertEqual(ttf.get_table("QUUX"), b"123")


class TTFontFaceTestCase(unittest.TestCase):
    "Tests TTFontFace class"

    def testAddSubsetObjects(self):
        "Tests TTFontFace.addSubsetObjects"
        face = TTFontFace("Vera.ttf")
        doc = PDFDocument()
        fontDescriptor = face.addSubsetObjects(doc, "TestFont", [ 0x78, 0x2017 ])
        fontDescriptor = doc.idToObject[fontDescriptor.name].dict
        self.assertEqual(fontDescriptor['Type'], '/FontDescriptor')
        self.assertEqual(fontDescriptor['Ascent'], face.ascent)
        self.assertEqual(fontDescriptor['CapHeight'], face.capHeight)
        self.assertEqual(fontDescriptor['Descent'], face.descent)
        self.assertEqual(fontDescriptor['Flags'], (face.flags & ~FF_NONSYMBOLIC) | FF_SYMBOLIC)
        self.assertEqual(fontDescriptor['FontName'], "/TestFont")
        self.assertEqual(fontDescriptor['FontBBox'].sequence, face.bbox)
        self.assertEqual(fontDescriptor['ItalicAngle'], face.italicAngle)
        self.assertEqual(fontDescriptor['StemV'], face.stemV)
        fontFile = fontDescriptor['FontFile2']
        fontFile = doc.idToObject[fontFile.name]
        self.assertTrue(fontFile.content != "")

class TTFontTestCase(NearTestCase):
    "Tests TTFont class"

    def testStringWidth(self):
        "Test TTFont.stringWidth"
        font = TTFont("Vera", "Vera.ttf")
        self.assertTrue(font.stringWidth("test", 10) > 0)
        width = font.stringWidth(utf8(0x2260) * 2, 1000)
        expected = font.face.getCharWidth(0x2260) * 2
        self.assertNear(width,expected)

    def testTTFontFromBytesIO(self):
        "Test loading TTFont from in-memory file"
        # Direct source: https://github.com/tmbdev/hocr-tools/blob/master/hocr-pdf
        # Glyphless variation of vedaal's invisible font retrieved from
        # http://www.angelfire.com/pr/pgpf/if.html, which says:
        # 'Invisible font' is unrestricted freeware. Enjoy, Improve, Distribute freely
        font = """
        eJzdlk1sG0UUx/+zs3btNEmrUKpCPxikSqRS4jpfFURUagmkEQQoiRXgAl07Y3vL2mvt2ml8APXG
        hQPiUEGEVDhWVHyIC1REPSAhBOWA+BCgSoULUqsKcWhVBKjhzfPU+VCi3Flrdn7vzZv33ryZ3TUE
        gC6chsTx8fHck1ONd98D0jnS7jn26GPjyMIleZhk9fT0wcHFl1/9GRDPkTxTqHg1dMkzJH9CbbTk
        xbWlJfKEdB+Np0pBswi+nH/Nvay92VtfJp4nvEztUJkUHXsdksUOkveXK/X5FNuLD838ICx4dv4N
        I1e8+ZqbxwCNP2jyqXoV/fmhy+WW/2SqFsb1pX68SfEpZ/TCrI3aHzcP//jitodvYmvL+6Xcr5mV
        vb1ScCzRnPRPfz+LsRSWNasuwRrZlh1sx0E8AriddyzEDfE6EkglFhJDJO5u9fJbFJ0etEMB78D5
        4Djm/7kjT0wqhSNURyS+u/2MGJKRu+0ExNkrt1pJti9p2x6b3TBJgmUXuzgnDmI8UWMbkVxeinCw
        Mo311/l/v3rF7+01D+OkZYE0PrbsYAu+sSyxU0jLLtIiYzmBrFiwnCT9FcsdOOK8ZHbFleSn0znP
        nDCnxbnAnGT9JeYtrP+FOcV8nTlNnsoc3bBAD85adtCNRcsSffjBsoseca/lBE7Q09LiJOm/ttyB
        0+IqcwfncJt5q4krO5k7jV7uY+5m7mPebuLKUea7iHvk48w72OYF5rvZT8C8k/WvMN/Dc19j3s02
        bzPvZZv3me9j/ox5P9t/xdzPzPVJcc7yGnPL/1+GO1lPVTXM+VNWOTRRg0YRHgrUK5yj1kvaEA1E
        xAWiCtl4qJL2ADKkG6Q3XxYjzEcR0E9hCj5KtBd1xCxp6jV5mKP7LJBr1nTRK2h1TvU2w0akCmGl
        5lWbBzJqMJsdyaijQaCm/FK5HqspHetoTtMsn4LO0T2mlqcwmlTVOT/28wGhCVKiNANKLiJRlxqB
        F603axQznIzRhDSq6EWZ4UUs+xud0VHsh1U1kMlmNwu9kTuFaRqpURU0VS3PVmZ0iE7gct0MG/8+
        2fmUvKlfRLYmisd1w8pk1LSu1XUlryM1MNTH9epTftWv+16gIh1oL9abJZyjrfF5a4qccp3oFAcz
        Wxxx4DpvlaKKxuytRDzeth5rW4W8qBFesvEX8RFRmLBHoB+TpCmRVCCb1gFCruzHqhhW6+qUF6tC
        pL26nlWN2K+W1LhRjxlVGKmRTFYVo7CiJug09E+GJb+QocMCPMWBK1wvEOfRFF2U0klK8CppqqvG
        pylRc2Zn+XDQWZIL8iO5KC9S+1RekOex1uOyZGR/w/Hf1lhzqVfFsxE39B/ws7Rm3N3nDrhPuMfc
        w3R/aE28KsfY2J+RPNp+j+KaOoCey4h+Dd48b9O5G0v2K7j0AM6s+5WQ/E0wVoK+pA6/3bup7bJf
        CMGjwvxTsr74/f/F95m3TH9x8o0/TU//N+7/D/ScVcA=
        """.encode('latin1')
        uncompressed = zlib.decompress(base64.decodebytes(font))
        ttf = BytesIO(uncompressed)
        setattr(ttf ,"name", "(invisible.ttf)")
        font = TTFont('invisible', ttf)
        for coord in font.face.bbox:
            self.assertEqual(coord, 0)
        pdfmetrics.registerFont(font)
        _simple_subset_generation('test_pdfbase_ttffonts_invisible.pdf',2,fonts=('invisible',))

    def testSplitString(self):
        "Tests TTFont.splitString"
        doc = PDFDocument()
        font = TTFont("Vera", "Vera.ttf", asciiReadable=True)
        T = list(range(256))
        for c in sorted(font.face.charToGlyph):
            if c not in T: T.append(c)
        text = "".join(map(chr,T))
        #we ignore rserveTTFNotDef by assuming it's always True
        #PDFUA forbids index 0(.notdef) in strings
        chunks = [(0,
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 !"#$%&\''
            b'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmno'
            b'pqrstuvwxyz{|}~\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00 \x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f'
            b'\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f'
            b'\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f'
            b'\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f'
            b'\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf'
            b'\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf'
            b'\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf'
            b'\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf'
            b'\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef'
            b'\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff'),
         (1,
            b'\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14'
            b'\x15\x16\x17\x18\x19\x1a\x1b\x1c')]
        self.assertEqual(font.splitString(text, doc), chunks)
        # Do it twice
        self.assertEqual(font.splitString(text, doc), chunks)

    def testSplitStringSpaces(self):
        # In order for justification (word spacing) to work, the space
        # glyph must have a code 32, and no other character should have
        # that code in any subset, or word spacing will be applied to it.

        doc = PDFDocument()
        font = TTFont("Vera", "Vera.ttf")
        text = b"".join(utf8(i) for i in range(512, -1, -1))
        chunks = font.splitString(text, doc)
        state = font.state[doc]
        self.assertEqual(state.assignments[32], 32)
        self.assertEqual(state.subsets[0][32], 32)

    def testSubsetInternalName(self):
        "Tests TTFont.getSubsetInternalName"
        doc = PDFDocument()
        font = TTFont("Vera", "Vera.ttf")
        # Actually generate some subsets
        text = b"".join(utf8(i) for i in range(513))
        font.splitString(text, doc)
        self.assertRaises(IndexError, font.getSubsetInternalName, -1, doc)
        self.assertRaises(IndexError, font.getSubsetInternalName, 3, doc)
        self.assertEqual(font.getSubsetInternalName(0, doc), "/F1+0")
        self.assertEqual(doc.delayedFonts, [font])

    def testAddObjectsEmpty(self):
        "TTFont.addObjects should not fail when no characters were used"
        font = TTFont("Vera", "Vera.ttf")
        doc = PDFDocument()
        font.addObjects(doc)

    def no_longer_testAddObjectsResets(self):
        "Test that TTFont.addObjects resets the font"
        # Actually generate some subsets
        doc = PDFDocument()
        font = TTFont("Vera", "Vera.ttf")
        font.splitString('a', doc)            # create some subset
        doc = PDFDocument()
        font.addObjects(doc)
        self.assertEqual(font.frozen, 0)
        self.assertEqual(font.nextCode, 0)
        self.assertEqual(font.subsets, [])
        self.assertEqual(font.assignments, {})
        font.splitString('ba', doc)           # should work

    def testParallelConstruction(self):
        "Test that TTFont can be used for different documents at the same time"
        doc1 = PDFDocument()
        doc2 = PDFDocument()
        font = TTFont("Vera", "Vera.ttf", asciiReadable=1)
        self.assertEqual(font.splitString('hello ', doc1), [(0, b'hello ')])
        self.assertEqual(font.splitString('hello ', doc2), [(0, b'hello ')])
        self.assertEqual(font.splitString('\xae\xab', doc1), [(0, b'\x01\x02')])
        self.assertEqual(font.splitString('\xab\xae', doc2), [(0, b'\x01\x02')])
        self.assertEqual(font.splitString('\xab\xae', doc1), [(0, b'\x02\x01')])
        self.assertEqual(font.splitString('\xae\xab', doc2), [(0, b'\x02\x01')])
        font.addObjects(doc1)
        #after addObjects doc1 state is no longer valid, doc2 should be OK
        self.assertEqual(font.splitString('\xae\xab', doc2), [(0, b'\x02\x01')])
        font.addObjects(doc2)

    def testAddObjects(self):
        "Test TTFont.addObjects"
        # Actually generate some subsets
        doc = PDFDocument()
        font = TTFont("Vera", "Vera.ttf", asciiReadable=1)
        font.splitString('a', doc)            # create some subset
        internalName = font.getSubsetInternalName(0, doc)[1:]
        font.addObjects(doc)
        pdfFont = doc.idToObject[internalName]
        self.assertEqual(doc.idToObject['BasicFonts'].dict[internalName], pdfFont)
        self.assertEqual(pdfFont.Name, internalName)
        self.assertEqual(pdfFont.BaseFont, "AAAAAA+BitstreamVeraSans-Roman")
        self.assertEqual(pdfFont.FirstChar, 0)
        self.assertEqual(pdfFont.LastChar, 127)
        self.assertEqual(len(pdfFont.Widths.sequence), 128)
        toUnicode = doc.idToObject[pdfFont.ToUnicode.name]
        self.assertTrue(toUnicode.content != "")
        fontDescriptor = doc.idToObject[pdfFont.FontDescriptor.name]
        self.assertEqual(fontDescriptor.dict['Type'], '/FontDescriptor')

    def testMakeToUnicodeCMap(self):
        "Test makeToUnicodeCMap"
        self.assertEqual(makeToUnicodeCMap("TestFont", [ 0x1234, 0x4321, 0x4242 ]),
"""/CIDInit /ProcSet findresource begin
12 dict begin
begincmap
/CIDSystemInfo
<< /Registry (TestFont)
/Ordering (TestFont)
/Supplement 0
>> def
/CMapName /TestFont def
/CMapType 2 def
1 begincodespacerange
<00> <02>
endcodespacerange
3 beginbfchar
<00> <1234>
<01> <4321>
<02> <4242>
endbfchar
endcmap
CMapName currentdict /CMap defineresource pop
end
end""")

    @rlSkipUnless(uharfbuzz,'no harfbuzz support')
    def test_ShapedStrOps(self):
        sd = ShapedStr('0123456789',shapeData=list(range(10)))
        e = []
        def sdcmp(op,v,ex):
            e.append(f'{op} errors:')
            i=len(e)
            if v!=ex: e.append(f'{v!a}!={ex!a}')
            if type(v)!=type(ex):
                e.append(f'{v.__class__.__name__}!={ex.__class__.__name__}')
            elif isinstance(ex,ShapedStr) and v.__shapeData__!=ex.__shapeData__:
                e.append(f'{v.__shapeData__}!={ex.__shapeData__}')
            if len(e)==i:
                e.pop()
            else:
                e[i-1] = ' '.join(e[i-1:])
                del e[i:]
        sdcmp('sd[1]',sd[1],ShapedStr('1',[1]))
        sdcmp('sd[2]',sd[2],ShapedStr('2',[2]))
        sdcmp('sd[-1]',sd[-1],ShapedStr('9',[9]))
        sdcmp('sd[:2]',sd[:2],ShapedStr('01',[0,1]))
        sdcmp('sd[:-8]',sd[:-8],ShapedStr('01',[0,1]))
        sdcmp('sd[-3:-2]',sd[-3:-2],ShapedStr('7',[7]))
        sdcmp('sd[:0]',sd[:0],'')
        sdcmp('sd[1:1]',sd[1:1],'')
        sdcmp('sd[-2:-2]',sd[-2:-2],'')
        sdcmp('sd[:2]+sd[-2:]',sd[:2]+sd[-2:],ShapedStr('0189',[0,1,8,9]))
        sdcmp('sd+"ABC"',sd+"ABC",ShapedStr('0123456789ABC',list(range(10))+3*[_sdSimple]))
        sdcmp('"ABC"+sd',"ABC"+sd,ShapedStr('ABC0123456789',3*[_sdSimple]+list(range(10))))
        sd += 'ABC'
        sdcmp('sd+="ABC"',sd,ShapedStr('0123456789ABC',list(range(10))+3*[_sdSimple]))
        e = '\n'.join(e)
        self.assertEqual('',e)

    def hbIfaceTest(self, ttfpath, text, exLen, exText, exShapedData):
        ttfn = os.path.splitext(os.path.basename(ttfpath))[0]
        ttf = freshTTFont(ttfn, ttfpath)
        fontName = ttf.fontName
        fontSize = 30
        pdfmetrics.registerFont(ttf)
        w = [pdfmetrics.stringWidth(text,fontName,fontSize),(ABag(fontName=fontName,fontSize=fontSize),text)]
        new = shapeFragWord(w)
        ttf.unregister()
        self.assertEqual(len(new),2,'expected a len of 2')
        self.assertTrue(isinstance(new,ShapedFragWord),f'returned list class is {new.__class__.__name__} not expected ShapedFragWord')
        self.assertEqual(new[0],exLen,f'new[0]={new[0]} not expected ={exLen}')
        self.assertTrue(isinstance(new[1][1],ShapedStr),f'returned str class is {new[1].__class__.__name__} not expected ShapedStr')
        self.assertTrue(new[1][1]==exText,'shaped string is wrong')
        self.assertEqual(new[1][1].__shapeData__,exShapedData, 'shape data is wrong')

    @rlSkipUnless(uharfbuzz,'no harfbuzz support')
    def test_hb_shape_change(self):
        return self.hbIfaceTest('hb-test.ttf','\u1786\u17D2\u1793\u17B6\u17C6|', 44.22,'\ue000\ue001\u17c6|',
                                [ShapeData(cluster=0, x_advance=923, y_advance=0, x_offset=0, y_offset=0, width=923),
                                ShapeData(cluster=0, x_advance=0, y_advance=0, x_offset=-296, y_offset=-26, width=0),
                                ShapeData(cluster=4, x_advance=0, y_advance=0, x_offset=47, y_offset=-29, width=0),
                                ShapeData(cluster=5, x_advance=551, y_advance=0, x_offset=0, y_offset=0, width=551)])

    @rlSkipUnless(uharfbuzz,'no harfbuzz support')
    def test_hb_ligature(self):
        #ligatures cause the standard length 133.2275390625 to be reduced to 130.78125
        return self.hbIfaceTest('Vera.ttf','Aon Way',130.78125,'Aon Way',
                                [ShapeData(cluster=0, x_advance=675.29296875, y_advance=0, x_offset=0.0, y_offset=0, width=684.08203125),
                                ShapeData(cluster=1, x_advance=603.02734375, y_advance=0, x_offset=-8.7890625, y_offset=0, width=611.81640625),
                                ShapeData(cluster=2, x_advance=633.7890625, y_advance=0, x_offset=0.0, y_offset=0, width=633.7890625),
                                ShapeData(cluster=3, x_advance=317.87109375, y_advance=0, x_offset=0.0, y_offset=0, width=317.87109375),
                                ShapeData(cluster=4, x_advance=956.54296875, y_advance=0, x_offset=0.0, y_offset=0, width=988.76953125),
                                ShapeData(cluster=5, x_advance=581.0546875, y_advance=0, x_offset=-31.73828125, y_offset=0, width=612.79296875),
                                ShapeData(cluster=6, x_advance=591.796875, y_advance=0, x_offset=0.0, y_offset=0, width=591.796875)])


    @staticmethod
    def drawVLines(canv,x,y,fontSize,X):
        canv.saveState()
        canv.setLineWidth(0.5)
        canv.setStrokeColor((1,0,0))
        canv.lines([(_+x,y-0.2*fontSize,_+x,y+fontSize) for _ in X])
        canv.restoreState()

    @classmethod
    def drawParaVLines(cls,canv,x,y,p,ttfn):
        X = [0]
        mfs = 0
        frags = p.frags
        for f in frags:
            for t in f[1:]:
                fontName = t[0].fontName
                if fontName!=ttfn: continue
                fontSize = t[0].fontSize
                mfs = max(mfs,fontSize)
                v = t[1]
                if type(v) is str:
                    for s in v:
                        X.append(X[-1]+pdfmetrics.stringWidth(s,fontName,fontSize))
                else:
                    for d in v.__shapeData__:
                        X.append(X[-1]+d.x_advance*fontSize/1000)
            if fontName!=ttfn: break
            if isinstance(f,_HSFrag):
                X.append(X[-1]+pdfmetrics.stringWidth(' ',fontName,fontSize))
        if mfs: cls.drawVLines(canv,x,y,mfs,X)

    @staticmethod
    def shapedStrAdvances(s,fontSize):
        A = [0]
        for a in s.__shapeData__:
            A.append(fontSize*a.x_advance/1000 + A[-1])
        return A

    @rlSkipUnless(uharfbuzz,'no harfbuzz support')
    def test_hb_examples(self):
        canv = Canvas(outputfile('test_pdfbase_ttfonts_hb_examples.pdf'))
        def hb_example(ttfpath, text, y, fpdfLiteral, excode):
            ttfn = os.path.splitext(os.path.basename(ttfpath))[0]
            ttf = freshTTFont(ttfn, ttfpath, shapable=False)
            try:
                fontName = ttf.fontName
                fontSize = 30
                pdfmetrics.registerFont(ttf)
                ttf.splitString(text,canv._doc)
                w = [pdfmetrics.stringWidth(text,fontName,fontSize),(ABag(fontName=fontName,fontSize=fontSize),text)]
                new = shapeFragWord(w)
                advances = self.shapedStrAdvances(new[1][1],fontSize)
                canv.setFont('Helvetica',12)
                x1 = 400
                canv.drawString(x1,y,f'unshaped {fontName}')
                canv.drawString(x1,y-1.2*fontSize,f'fpdf2 shaping {fontName}')
                canv.drawString(x1,y-2*1.2*fontSize,f'rl shaping {fontName}')
                canv.setFont(fontName,fontSize)
                canv.drawString(36,y,text)
                self.drawVLines(canv,36,y,fontSize,
                   [pdfmetrics.stringWidth(text[:_],fontName,fontSize) for _ in range(len(text)+1)])
                canv.saveState()
                canv.translate(0,-fontSize*1.2)
                ttf.shapable = True
                t = canv.beginText(36, y-1.2*fontSize) #786 - 1.2*30
                t._textOut(new[1][1],False)
                code = t.getCode()
                canv.drawText(t)
                self.drawVLines(canv,36,y-1.2*fontSize,fontSize,advances)
                if fpdfLiteral:
                    canv.addLiteral(fpdfLiteral)
                    self.drawVLines(canv,36,y,fontSize,advances)
                canv.restoreState()
                if code!=excode:
                    canv.showPage()
                    canv.save()
                self.assertEqual(code,excode,f'{fontName} PDF _textOut is wrong\n')
            finally:
                ttf.unregister()
        hb_example(
            'Vera.ttf',
            'Aon Way',
            786,
            fpdfLiteral='''BT 1 0 0 1 36 786 Tm /F2+0 30 Tf 36 TL (A) Tj 1 0 0 1 56 786 Tm (o) Tj 1 0 0 1 74.35 786 Tm (n) Tj 1 0 0 1 93.36 786 Tm ( ) Tj 1 0 0 1 102.9 786 Tm (W) Tj 1 0 0 1 130.64 786 Tm (a) Tj 1 0 0 1 149.03 786 Tm (y) Tj 1 0 0 1 166.78 786 Tm ET''',
            excode='''BT 1 0 0 1 36 750 Tm /F2+0 30 Tf 36 TL [(A) 17.57812 (on W) 63.96484 (ay)] TJ ET'''
            )
        canv.translate(0,-36)
        hb_example(
            'hb-test.ttf',
            '\u1786\u17D2\u1793\u17B6\u17C6|',
            706,
            fpdfLiteral=r'''BT 1 0 0 1 0 0 Tm 1 0 0 1 36 706 Tm /F3+0 30 Tf 36 TL (\006) Tj 1 0 0 1 54.81 705.22 Tm (\007) Tj 1 0 0 1 63.69 706 Tm 1 0 0 1 65.1 705.13 Tm (\005) Tj 1 0 0 1 63.49 706 Tm (|) Tj  ET''',
            excode = r'''BT 1 0 0 1 36 670 Tm /F3+0 30 Tf 36 TL (\006) Tj -0.78 Ts [296 (\007) -296] TJ -0.87 Ts [-47 (\005) 47 (|)] TJ ET'''
            )
        canv.translate(0,-50)
        if haveDejaVuSans:
            hb_example(
                'DejaVuSans.ttf',
                'Huffing Clifftop finish|',
                706-70,
                fpdfLiteral=r'''BT 1 0 0 1 36 636 Tm /F4+0 30 Tf 36 TL (H) Tj 1 0 0 1 58.56 636 Tm (u) Tj 1 0 0 1 77.57 636 Tm (\001) Tj 1 0 0 1 106.58 636 Tm (n) Tj 1 0 0 1 125.59 636 Tm (g) Tj 1 0 0 1 144.63 636 Tm ( ) Tj 1 0 0 1 154.17 636 Tm (C) Tj 1 0 0 1 175.12 636 Tm (l) Tj 1 0 0 1 183.45 636 Tm (i) Tj 1 0 0 1 191.79 636 Tm (\002) Tj 1 0 0 1 212.46 636 Tm (t) Tj 1 0 0 1 224.22 636 Tm (o) Tj 1 0 0 1 242.57 636 Tm (p) Tj 1 0 0 1 261.62 636 Tm ( ) Tj 1 0 0 1 271.15 636 Tm (\003) Tj 1 0 0 1 290.05 636 Tm (n) Tj 1 0 0 1 309.06 636 Tm (i) Tj 1 0 0 1 317.4 636 Tm (s) Tj 1 0 0 1 333.03 636 Tm (h) Tj 1 0 0 1 352.04 636 Tm (|) Tj 1 0 0 1 362.15 636 Tm ET''',
                excode=r'''BT 1 0 0 1 36 600 Tm /F4+0 30 Tf 36 TL (Hu\001ng Cli\002top \003nish|) Tj ET'''
                )

        canv.showPage()
        canv.save()

    def hb_paragraph_drawon(self, canv, ttfpath, text, y=786, textp=None):
        try:
            ttfn = os.path.splitext(os.path.basename(ttfpath))[0]
            ttfn1 = ttfn+'1'
            ttf = freshTTFont(ttfn,ttfpath,shapable=False)
            ttf1 = freshTTFont(ttfn1,ttfpath,shapable=True)
            ttf1.face.name = ttf.face.name + b'1'
            pdfmetrics.registerFont(ttf)
            pdfmetrics.registerFont(ttf1)
            stysh = getSampleStyleSheet()
            fontSize = 30
            leading = 36
            sty = stysh.Normal.clone('sty',fontName=ttfn,fontSize=fontSize,leading=leading)
            sty1 = stysh.Normal.clone('sty1',fontName=ttfn1,fontSize=fontSize,leading=leading,shaping=True)
            pW, pH = canv._pagesize
            x = 36
            aW = pW - 2*36
            aH = pH - 2*36
            p = Paragraph(f'{text}<span face="Helvetica" size="12"> {ttfn} unshaped</span>',sty)
            w,h = p.wrap(aW,aH)
            p.drawOn(canv, x=x, y=y)
            self.drawParaVLines(canv,x,y,p,ttfn)
            y -= leading
            p1 = Paragraph(f'{text}<span face="Helvetica" size="12"> {ttfn} shaped</span>',sty1)
            w,h = p1.wrap(aW,aH)
            p1.drawOn(canv, x=x, y=y)
            self.drawParaVLines(canv,x,y,p1,ttfn1)
            y -= 12
            xe = pW - 36
            xm = pW*0.5
            canv.saveState()
            if textp is None: textp = text
            canv.setFont(ttfn,10)
            canv.drawString(x,y,textp)
            canv.drawRightString(xe,y,textp)
            canv.drawCentredString(xm,y,textp)
            y -= 12
            canv.setFont(ttfn1,10)
            canv.drawString(x,y,textp,shaping=True)
            canv.drawRightString(xe,y,textp,shaping=True)
            canv.drawCentredString(xm,y,textp,shaping=True)
            canv.restoreState()
            y -= 12
        finally:
            for _ in ('ttf','ttf1'):
                if _ in locals():
                    locals()[_].unregister()

    @rlSkipUnless(uharfbuzz,'no harfbuzz support')
    def test_hb_paragraph_drawOn(self):
        canv = Canvas(outputfile('test_pdfbase_ttfonts_hb_para_drawOn.pdf'))
        self.hb_paragraph_drawon(canv, 'hb-test.ttf', '\u1786\u17D2\u1793\u17B6\u17C6|', y=786)
        self.hb_paragraph_drawon(canv, 'Vera.ttf', 'Aon Way|', y=786-2*48)
        if haveDejaVuSans:
            self.hb_paragraph_drawon(canv, 'DejaVuSans.ttf',
                            '<span color="green">H</span>u<span color="blue">f</span>fing <u>Clifftop</u> <a href="https://www.reportlab.com">finish</a>|',
                            y=786-4*48, textp='Huffing Clifftop finish|')
        canv.showPage()
        canv.save()

def makeSuite():
    suite = makeSuiteForClasses(
        TTFontsTestCase,
        TTFontFileTestCase,
        TTFontFaceTestCase,
        TTFontTestCase)
    return suite


#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
