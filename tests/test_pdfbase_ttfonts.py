
"""Test TrueType font subsetting & embedding code.

This test uses a sample font (Vera.ttf) taken from Bitstream which is called Vera
Serif Regular and is covered under the license in ../fonts/bitstream-vera-license.txt.
"""
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation, NearTestCase
if __name__=='__main__':
    setOutDir(__name__)
import unittest
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfdoc import PDFDocument, PDFError
from reportlab.pdfbase.ttfonts import TTFont, TTFontFace, TTFontFile, TTFOpenFile, \
                                      TTFontParser, TTFontMaker, TTFError, \
                                      makeToUnicodeCMap, \
                                      FF_SYMBOLIC, FF_NONSYMBOLIC, \
                                      calcChecksum, add32
from reportlab import rl_config
from reportlab.lib.utils import getBytesIO, isPy3, uniChr, int2Byte

def utf8(code):
    "Convert a given UCS character index into UTF-8"
    return uniChr(code).encode('utf8')

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
                    ch = utf8(i * 32 + j+p*alter)
                    c.drawString(80 + j * 13 + int(j / 16.0) * 4, 600 - i * 13 - int(i / 8.0) * 8, ch)
        c.showPage()
    c.save()

def show_all_glyphs(fn,fontName='Vera'):
    c = Canvas(outputfile(fn))
    c.setFont('Helvetica', 20)
    c.drawString(72,c._pagesize[1]-30, 'Unicode TrueType Font Test %s' % fontName)
    from reportlab.pdfbase.pdfmetrics import _fonts
    from reportlab.lib.utils import uniChr
    font = _fonts[fontName]
    doc = c._doc
    kfunc = font.face.charToGlyph.keys if isPy3 else font.face.charToGlyph.iterkeys
    for s in kfunc():
        if s<0x10000:
            font.splitString(uniChr(s),doc)
    state = font.state[doc]
    cn = {}
    #print('len(assignments)=%d'%  len(state.assignments))
    nzero = 0
    ifunc = state.assignments.items if isPy3 else state.assignments.iteritems
    for code, n in ifunc():
        if code==0: nzero += 1
        cn[n] = uniChr(code)
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
            c.drawString(x,y,uniChr(code))
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
        try:
            pdfmetrics.registerFont(TTFont("DejaVuSans", "DejaVuSans.ttf"))
        except:
            pass
        else:
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
        self.assertRaises(TTFError, TTFontFile, getBytesIO(b""))
        self.assertRaises(TTFError, TTFontFile, getBytesIO(b"invalid signature"))
        self.assertRaises(TTFError, TTFontFile, getBytesIO(b"OTTO - OpenType not supported yet"))
        self.assertRaises(TTFError, TTFontFile, getBytesIO(b"\0\1\0\0"))

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
        TTFontFile(getBytesIO(F), validate=1) # should not fail
        F1 = F[:12345] + b"\xFF" + F[12346:] # change one byte
        self.assertRaises(TTFError, TTFontFile, getBytesIO(F1), validate=1)
        F1 = F[:8] + b"\xFF" + F[9:] # change one byte
        self.assertRaises(TTFError, TTFontFile, getBytesIO(F1), validate=1)

    def testSubsetting(self):
        "Tests TTFontFile and TTF parsing code"
        ttf = TTFontFile("Vera.ttf")
        subset = ttf.makeSubset([0x41, 0x42])
        subset = TTFontFile(getBytesIO(subset), 0)
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
        ttf = TTFontParser(getBytesIO(stm), 0)
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
        import io, zlib, base64
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
        uncompressed = zlib.decompress(getattr(base64,'decodebytes' if isPy3 else 'decodestring')(font))
        ttf = io.BytesIO(uncompressed)
        setattr(ttf ,"name", "(invisible.ttf)")
        font = TTFont('invisible', ttf)
        for coord in font.face.bbox:
            self.assertEqual(coord, 0)
        pdfmetrics.registerFont(font)
        _simple_subset_generation('test_pdfbase_ttffonts_invisible.pdf',2,fonts=('invisible',))

    def testSplitString(self):
        "Tests TTFont.splitString"
        doc = PDFDocument()
        font = TTFont("Vera", "Vera.ttf")
        text = b"".join(utf8(i) for i in range(511))
        allchars = b"".join(int2Byte(i) for i in range(256))
        if rl_config.reserveTTFNotdef:
            chunks = [(0, allchars), (1, allchars[1:32] + allchars[33:]), (2, b'\x01')]
        else:
            chunks = [(0, allchars), (1, allchars[:32] + allchars[33:])]
        self.assertEqual(font.splitString(text, doc), chunks)
        # Do it twice
        self.assertEqual(font.splitString(text, doc), chunks)

        text = b"".join(utf8(i) for i in range(510, -1, -1))
        revver = (lambda b: map(int2Byte,reversed(b))) if isPy3 else (lambda b: reversed(list(b)))
        chunks = [(i[0],b"".join(revver(i[1]))) for i in reversed(chunks)]
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
        self.assertEqual(state.subsets[1][32], 32)

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
        self.assertEqual(font.getSubsetInternalName(1, doc), "/F1+1")
        self.assertEqual(font.getSubsetInternalName(2, doc), "/F1+2")
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
        ttfAsciiReadable = rl_config.ttfAsciiReadable
        try:
            rl_config.ttfAsciiReadable = 1
            doc1 = PDFDocument()
            doc2 = PDFDocument()
            font = TTFont("Vera", "Vera.ttf")
            self.assertEqual(font.splitString('hello ', doc1), [(0, b'hello ')])
            self.assertEqual(font.splitString('hello ', doc2), [(0, b'hello ')])
            self.assertEqual(font.splitString(u'\u0410\u0411'.encode('UTF-8'), doc1), [(0, b'\x80\x81')])
            self.assertEqual(font.splitString(u'\u0412'.encode('UTF-8'), doc2), [(0, b'\x80')])
            font.addObjects(doc1)
            self.assertEqual(font.splitString(u'\u0413'.encode('UTF-8'), doc2), [(0, b'\x81')])
            font.addObjects(doc2)
        finally:
            rl_config.ttfAsciiReadable = ttfAsciiReadable

    def testAddObjects(self):
        "Test TTFont.addObjects"
        # Actually generate some subsets
        ttfAsciiReadable = rl_config.ttfAsciiReadable
        try:
            rl_config.ttfAsciiReadable = 1
            doc = PDFDocument()
            font = TTFont("Vera", "Vera.ttf")
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
        finally:
            rl_config.ttfAsciiReadable = ttfAsciiReadable

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
