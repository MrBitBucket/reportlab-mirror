from reportlab import xrange
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation, NearTestCase
setOutDir(__name__)
import unittest
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfform

class PdfFormTestCase(NearTestCase):
    def testMultipleUsage(self):
        for i in range(2):
            c = canvas.Canvas(outputfile('test_pdfbase_pdfform_multiple_usage_%s.pdf'%i))
            c.drawString(100, 100, "Test")
            pdfform.buttonFieldAbsolute(c, 'button', 'Off', 200, 200)
            c.save()

    def testAAbsoluteAndRelativeFields(self):
        #the old test1 in pdfform
        c = canvas.Canvas(outputfile("test_pdfbase_pdfform_formtest.pdf"))
        # first page
        c.setFont("Courier", 10)
        c.drawString(100, 500, "hello world")
        pdfform.textFieldAbsolute(c, "fieldA", 100, 600, 100, 20, "default value")
        pdfform.textFieldAbsolute(c, "fieldB", 100, 300, 100, 50, "another default value", multiline=1)
        pdfform.selectFieldAbsolute(c, "fieldC", "France", ["Canada", "France", "China"], 100, 200, 100, 20)
        c.rect(100, 600, 100, 20)
        pdfform.buttonFieldAbsolute(c, "field2", "Yes", 100, 700, width=20, height=20)
        c.rect(100, 700, 20, 20)
        pdfform.buttonFieldAbsolute(c, "field3", "Off", 100, 800, width=20, height=20)
        c.rect(100, 800, 20, 20)
        # second page
        c.showPage()
        c.setFont("Helvetica", 7)
        c.translate(50, 20)
        c.drawString(100, 500, "hello world")
        pdfform.textFieldRelative(c, "fieldA_1", 100, 600, 100, 20, "default value 2")
        c.setStrokeColorRGB(1,0,0)
        c.setFillColorRGB(0,1,0.5)
        pdfform.textFieldRelative(c, "fieldB_1", 100, 300, 100, 50, "another default value 2", multiline=1)
        pdfform.selectFieldRelative(c, "fieldC_1", "France 1", ["Canada 0", "France 1", "China 2"], 100, 200, 100, 20)
        c.rect(100, 600, 100, 20)
        pdfform.buttonFieldRelative(c, "field2_1", "Yes", 100, 700, width=20, height=20)
        c.rect(100, 700, 20, 20)
        pdfform.buttonFieldRelative(c, "field3_1", "Off", 100, 800, width=20, height=20)
        c.rect(100, 800, 20, 20)
        c.save()

    def testNewAcroform(self):
        from reportlab.lib.colors import toColor, black, red, green, blue, magenta, yellow, pink
        canv = canvas.Canvas(outputfile("test_pdfbase_acroform-0.pdf"))
        doc = canv._doc
        af = canv.acroForm

        #these are absolute in unchanged matrix
        canv.drawString(4*72,800,'unshifted absolute')
        af.checkbox(name='cb1A',tooltip='Field cb1A',checked=True,x=72,y=72,buttonStyle='circle',borderWidth=1, borderColor=red, fillColor=green, textColor=blue,forceBorder=True)
        af.checkbox(name='cb1B',tooltip='Field cb1B',checked=True,x=72,y=72+36,buttonStyle='check',borderWidth=2, borderColor=green, fillColor=blue, textColor=red,forceBorder=True)
        af.checkbox(name='cb1C',tooltip='Field cb1C',checked=True,x=72,y=72+2*36,buttonStyle='cross',borderWidth=2, borderColor=red, fillColor=green, textColor=blue,forceBorder=True)
        af.checkbox(name='cb1D',tooltip='Field cb1D',checked=True,x=72,y=72+3*36,buttonStyle='star',borderWidth=2, borderColor=red, fillColor=green, textColor=blue,forceBorder=True)
        af.checkbox(name='cb1E',tooltip='Field cb1E',checked=True,x=72,y=72+4*36,buttonStyle='diamond',borderStyle='bevelled', borderWidth=2, borderColor=red, fillColor=green, textColor=blue,forceBorder=True)
        af.checkbox(name='cb1F',tooltip='Field cb1F',checked=True,x=72,y=72+5*36,buttonStyle='check', borderWidth=2, borderColor=red, fillColor=None, textColor=None,forceBorder=True)
        af.checkbox(name='cb1H',tooltip='Field cb1H',checked=True,x=72,y=72+6*36,buttonStyle='check', borderStyle='underlined',borderWidth=2, borderColor=red, fillColor=None, textColor=None,forceBorder=True)
        af.checkbox(name='cb1G',tooltip='Field cb1G',checked=True,x=72,y=72+7*36,buttonStyle='check', borderStyle='dashed',borderWidth=2, borderColor=red, fillColor=None, textColor=None,forceBorder=True)
        af.checkbox(name='cb1I',tooltip='Field cb1I',checked=True,x=72,y=72+8*36,buttonStyle='check', borderStyle='inset',borderWidth=1, borderColor=red, fillColor=None, textColor=None,forceBorder=True)
        af.checkbox(name='cb1J',tooltip='Field cb1J',checked=True,x=72,y=72+9*36,buttonStyle='check', borderStyle='solid',shape='circle', borderWidth=2, borderColor=red, fillColor=green, textColor=blue,forceBorder=True)
        af.checkbox(name='cb1K',tooltip='Field cb1K',checked=True,x=72,y=72+10*36,buttonStyle='check', borderWidth=1, borderColor=None, fillColor=None, textColor=None,forceBorder=True)
        af.checkbox(name='cb1L',tooltip='Field cb1L',checked=False,x=72,y=800,buttonStyle='check',borderWidth=None, borderColor=None, fillColor=None, textColor=None,forceBorder=True)
        af.checkbox(name='cb1M',tooltip='Field cb1M',checked=False,x=72,y=600,buttonStyle='check',borderWidth=2, borderColor=blue, fillColor=None, textColor=None,forceBorder=True)
        af.radio(name='rb1A',tooltip='Field rb1A', value='V1', selected=False,x=144,y=72+0*36,buttonStyle='circle', borderStyle='solid',shape='circle', borderWidth=2, borderColor=red, fillColor=green, textColor=blue,forceBorder=True)
        af.radio(name='rb1A',tooltip='Field rb1A', value='V2', selected=True,x=144,y=72+1*36,buttonStyle='circle', borderStyle='solid',shape='circle', borderWidth=2, borderColor=red, fillColor=green, textColor=blue,forceBorder=True)
        af.radio(name='rb1B',tooltip='Field rb1B', value='V1', selected=False,x=144+36,y=72+0*36,buttonStyle='check', borderStyle='solid',shape='square', borderWidth=2, borderColor=green, fillColor=red, textColor=blue,forceBorder=True)
        af.radio(name='rb1B',tooltip='Field rb1B', value='V2', selected=False,x=144+36,y=72+1*36,buttonStyle='check', borderStyle='solid',shape='square', borderWidth=2, borderColor=green, fillColor=red, textColor=blue,forceBorder=True)
        af.radio(name='rb1C',tooltip='Field rb1C', value='V1', selected=False,x=144*2,y=72+0*36,buttonStyle='circle', borderStyle='bevelled',shape='circle', borderWidth=2, borderColor=green, fillColor=yellow, textColor=blue,forceBorder=True)
        af.radio(name='rb1C',tooltip='Field rb1C', value='V2', selected=True,x=144*2,y=72+1*36,buttonStyle='circle', borderStyle='inset',shape='circle', borderWidth=2, borderColor=magenta, fillColor=pink, textColor=blue,forceBorder=True)
        af.textfield(name='tf1A',tooltip='Field tf1A',value='Hello World',x=144*2+36,y=72+0*36, borderStyle='inset', borderWidth=2, borderColor=magenta, fillColor=pink, textColor=blue,forceBorder=True)
        af.textfield(name='tf1B',tooltip='Field tf1B',value='Hello World',x=144*2+36,y=72+2*36, borderStyle='inset', borderWidth=2, fontName='Courier-Bold', borderColor=magenta, fillColor=pink, textColor=blue,forceBorder=True)
        af.textfield(name='tf1C',tooltip='Field tf1C',value='Hello World',x=144*2+36,y=72+3*36, borderStyle='inset', borderWidth=0, fontName='Courier-Bold', borderColor=green, fillColor=red, textColor=black)
        canv.showPage()
        canv.translate(72,0)    #shift matrix
        #these are absolute in changed matrix
        canv.drawString(4*72,800,'shifted absolute')
        af.checkbox(name='cb2A',tooltip='Field cb2A',checked=True,x=72,y=72,buttonStyle='circle',borderWidth=1, borderColor=red, fillColor=green, textColor=blue,forceBorder=True)
        af.checkbox(name='cb2B',tooltip='Field cb2B',checked=True,x=72,y=72+36,buttonStyle='check',borderWidth=2, borderColor=green, fillColor=blue, textColor=red,forceBorder=True)
        af.checkbox(name='cb2C',tooltip='Field cb2C',checked=True,x=72,y=72+2*36,buttonStyle='cross',borderWidth=2, borderColor=red, fillColor=green, textColor=blue,forceBorder=True)
        af.checkbox(name='cb2D',tooltip='Field cb2D',checked=True,x=72,y=72+3*36,buttonStyle='star',borderWidth=2, borderColor=red, fillColor=green, textColor=blue,forceBorder=True)
        af.checkbox(name='cb2E',tooltip='Field cb2E',checked=True,x=72,y=72+4*36,buttonStyle='diamond',borderStyle='bevelled', borderWidth=2, borderColor=red, fillColor=green, textColor=blue,forceBorder=True)
        af.checkbox(name='cb2F',tooltip='Field cb2F',checked=True,x=72,y=72+5*36,buttonStyle='check', borderWidth=2, borderColor=red, fillColor=None, textColor=None,forceBorder=True)
        af.checkbox(name='cb2H',tooltip='Field cb2H',checked=True,x=72,y=72+6*36,buttonStyle='check', borderStyle='underlined',borderWidth=2, borderColor=red, fillColor=None, textColor=None,forceBorder=True)
        af.checkbox(name='cb2G',tooltip='Field cb2G',checked=True,x=72,y=72+7*36,buttonStyle='check', borderStyle='dashed',borderWidth=2, borderColor=red, fillColor=None, textColor=None,forceBorder=True)
        af.checkbox(name='cb2I',tooltip='Field cb2I',checked=True,x=72,y=72+8*36,buttonStyle='check', borderStyle='inset',borderWidth=2, borderColor=red, fillColor=None, textColor=None,forceBorder=True)
        af.checkbox(name='cb2J',tooltip='Field cb2J',checked=True,x=72,y=72+9*36,buttonStyle='check', borderStyle='solid',shape='circle', borderWidth=2, borderColor=red, fillColor=green, textColor=blue,forceBorder=True)
        af.checkbox(name='cb2K',tooltip='Field cb2K',checked=True,x=72,y=72+10*36,buttonStyle='check', borderWidth=1, borderColor=None, fillColor=None, textColor=None,forceBorder=True)
        af.checkbox(name='cb2L',tooltip='Field cb2L',checked=False,x=72,y=800,buttonStyle='check',borderWidth=None, borderColor=None, fillColor=None, textColor=None,forceBorder=True)
        af.checkbox(name='cb2M',tooltip='Field cb2M',checked=False,x=72,y=600,buttonStyle='check',borderWidth=2, borderColor=blue, fillColor=None, textColor=None,forceBorder=True)
        af.radio(name='rb2A',tooltip='Field rb2A', value='V1', selected=False,x=144,y=72+0*36,buttonStyle='circle', borderStyle='solid',shape='circle', borderWidth=2, borderColor=red, fillColor=green, textColor=blue,forceBorder=True)
        af.radio(name='rb2A',tooltip='Field rb2A', value='V2', selected=True,x=144,y=72+1*36,buttonStyle='circle', borderStyle='solid',shape='circle', borderWidth=2, borderColor=red, fillColor=green, textColor=blue,forceBorder=True)
        af.radio(name='rb2B',tooltip='Field rb2B', value='V1', selected=False,x=144+36,y=72+0*36,buttonStyle='check', borderStyle='solid',shape='square', borderWidth=2, borderColor=green, fillColor=red, textColor=blue,forceBorder=True)
        af.radio(name='rb2B',tooltip='Field rb2B', value='V2', selected=False,x=144+36,y=72+1*36,buttonStyle='check', borderStyle='solid',shape='square', borderWidth=2, borderColor=green, fillColor=red, textColor=blue,forceBorder=True)
        af.radio(name='rb2C',tooltip='Field rb2C', value='V1', selected=False,x=144*2,y=72+0*36,buttonStyle='circle', borderStyle='bevelled',shape='circle', borderWidth=2, borderColor=green, fillColor=yellow, textColor=blue,forceBorder=True)
        af.radio(name='rb2C',tooltip='Field rb2C', value='V2', selected=True,x=144*2,y=72+1*36,buttonStyle='circle', borderStyle='inset',shape='circle', borderWidth=2, borderColor=magenta, fillColor=pink, textColor=blue,forceBorder=True)
        af.textfield(name='tf2A',tooltip='Field tf2A',value='Hello World',x=144*2+36,y=72+0*36, borderStyle='inset', borderWidth=2, borderColor=magenta, fillColor=pink, textColor=blue,forceBorder=True)
        af.textfield(name='tf2B',tooltip='Field tf2B',value='Hello World',x=144*2+36,y=72+2*36, borderStyle='inset', borderWidth=2, fontName='Courier-Bold', borderColor=magenta, fillColor=pink, textColor=blue,forceBorder=True)
        af.textfield(name='tf2C',tooltip='Field tf2C',value='Hello World',x=144*2+36,y=72+3*36, borderStyle='inset', borderWidth=0, fontName='Courier-Bold', borderColor=green, fillColor=red, textColor=black)
        canv.showPage()
        canv.translate(72,0)    #shift matrix
        #these are relative in changed matrix
        canv.drawString(4*72,800,'shifted relative')
        af.checkboxRelative(name='cb3A',tooltip='Field cb3A',checked=True,x=72,y=72,buttonStyle='circle',borderWidth=1, borderColor=red, fillColor=green, textColor=blue,forceBorder=True)
        af.checkboxRelative(name='cb3B',tooltip='Field cb3B',checked=True,x=72,y=72+36,buttonStyle='check',borderWidth=2, borderColor=green, fillColor=blue, textColor=red,forceBorder=True)
        af.checkboxRelative(name='cb3C',tooltip='Field cb3C',checked=True,x=72,y=72+2*36,buttonStyle='cross',borderWidth=2, borderColor=red, fillColor=green, textColor=blue,forceBorder=True)
        af.checkboxRelative(name='cb3D',tooltip='Field cb3D',checked=True,x=72,y=72+3*36,buttonStyle='star',borderWidth=2, borderColor=red, fillColor=green, textColor=blue,forceBorder=True)
        af.checkboxRelative(name='cb3E',tooltip='Field cb3E',checked=True,x=72,y=72+4*36,buttonStyle='diamond',borderStyle='bevelled', borderWidth=2, borderColor=red, fillColor=green, textColor=blue,forceBorder=True)
        af.checkboxRelative(name='cb3F',tooltip='Field cb3F',checked=True,x=72,y=72+5*36,buttonStyle='check', borderWidth=2, borderColor=red, fillColor=None, textColor=None,forceBorder=True)
        af.checkboxRelative(name='cb3H',tooltip='Field cb3H',checked=True,x=72,y=72+6*36,buttonStyle='check', borderStyle='underlined',borderWidth=2, borderColor=red, fillColor=None, textColor=None,forceBorder=True)
        af.checkboxRelative(name='cb3G',tooltip='Field cb3G',checked=True,x=72,y=72+7*36,buttonStyle='check', borderStyle='dashed',borderWidth=2, borderColor=red, fillColor=None, textColor=None,forceBorder=True)
        af.checkboxRelative(name='cb3I',tooltip='Field cb3I',checked=True,x=72,y=72+8*36,buttonStyle='check', borderStyle='inset',borderWidth=2, borderColor=red, fillColor=None, textColor=None,forceBorder=True)
        af.checkboxRelative(name='cb3J',tooltip='Field cb3J',checked=True,x=72,y=72+9*36,buttonStyle='check', borderStyle='solid',shape='circle', borderWidth=2, borderColor=red, fillColor=green, textColor=blue,forceBorder=True)
        af.checkboxRelative(name='cb3K',tooltip='Field cb3K',checked=True,x=72,y=72+10*36,buttonStyle='check', borderWidth=1, borderColor=None, fillColor=None, textColor=None,forceBorder=True)
        af.checkboxRelative(name='cb3L',tooltip='Field cb3L',checked=False,x=72,y=800,buttonStyle='check',borderWidth=None, borderColor=None, fillColor=None, textColor=None,forceBorder=True)
        af.checkboxRelative(name='cb3M',tooltip='Field cb3M',checked=False,x=72,y=600,buttonStyle='check',borderWidth=2, borderColor=blue, fillColor=None, textColor=None,forceBorder=True)
        af.radioRelative(name='rb3A',tooltip='Field rb3A', value='V1', selected=False,x=144,y=72+0*36,buttonStyle='circle', borderStyle='solid',shape='circle', borderWidth=2, borderColor=red, fillColor=green, textColor=blue,forceBorder=True)
        af.radioRelative(name='rb3A',tooltip='Field rb3A', value='V2', selected=True,x=144,y=72+1*36,buttonStyle='circle', borderStyle='solid',shape='circle', borderWidth=2, borderColor=red, fillColor=green, textColor=blue,forceBorder=True)
        af.radioRelative(name='rb3B',tooltip='Field rb3B', value='V1', selected=False,x=144+36,y=72+0*36,buttonStyle='check', borderStyle='solid',shape='square', borderWidth=2, borderColor=green, fillColor=red, textColor=blue,forceBorder=True)
        af.radioRelative(name='rb3B',tooltip='Field rb3B', value='V2', selected=False,x=144+36,y=72+1*36,buttonStyle='check', borderStyle='solid',shape='square', borderWidth=2, borderColor=green, fillColor=red, textColor=blue,forceBorder=True)
        af.radioRelative(name='rb3C',tooltip='Field rb3C', value='V1', selected=False,x=144*2,y=72+0*36,buttonStyle='circle', borderStyle='bevelled',shape='circle', borderWidth=2, borderColor=green, fillColor=yellow, textColor=blue,forceBorder=True)
        af.radioRelative(name='rb3C',tooltip='Field rb3C', value='V2', selected=True,x=144*2,y=72+1*36,buttonStyle='circle', borderStyle='inset',shape='circle', borderWidth=2, borderColor=magenta, fillColor=pink, textColor=blue,forceBorder=True)
        af.textfieldRelative(name='tf3A',tooltip='Field tf3A',value='Hello World',x=144*2+36,y=72+0*36, borderStyle='inset', borderWidth=2, borderColor=magenta, fillColor=pink, textColor=blue,forceBorder=True)
        af.textfieldRelative(name='tf3B',tooltip='Field tf3B',value='Hello World',x=144*2+36,y=72+2*36, borderStyle='inset', borderWidth=2, fontName='Courier-Bold', borderColor=magenta, fillColor=pink, textColor=blue,forceBorder=True)
        af.textfieldRelative(name='tf3C',tooltip='Field tf3C',value='Hello World',x=144*2+36,y=72+3*36, borderStyle='inset', borderWidth=0, fontName='Courier-Bold', borderColor=green, fillColor=red, textColor=black)
        canv.showPage()
        BS = ['solid','bevelled','inset','dashed','underlined']
        V = ['Av','B','Cv','D','Dv','E','F','G','Gv']
        ff = ['','edit']
        for i in xrange(500):
            x = 72+(i%3)*180
            y = 800 - int(i/3)*36
            if y<100: break
            value=V[i%len(V)]
            bW=i%3+1
            af.choice(name='CH%d'%i,value=value,x=x,y=y, width=72+bW, height=20+bW, borderStyle=BS[i%5], borderWidth=bW,
                fieldFlags=ff[i and i%9==0],
                borderColor=red, fillColor=green, textColor=blue,forceBorder=False,
                tooltip = 'CH%d value=%r' % (i,value),
                options=[('A','Av'),'B',('C','Cv'),('D','Dv'),'E',('F',),('G','Gv')])
        canv.showPage()
        BS = ['solid','bevelled','inset','dashed','underlined']
        V = ['Av','B','Cv','D','Dv','E','F','G','Gv','H']
        ff = ['','multiSelect']
        for i in xrange(500):
            x = 72+(i%3)*180
            y = 800 - int(i/3)*108 - 52
            if y<100: break
            v=i%len(V)
            value=[V[v]]
            if v>=5:
                v1 = V[3+i%5]
                if v1 not in value:
                    value.append(v1)
            bW=i%3+1
            fieldFlags=ff[len(value)>1]
            af.listbox(name='LB%d'%i,value=value,x=x,y=y, width=72+bW, height=72+bW, borderStyle=BS[i%5], borderWidth=bW,
                fieldFlags=fieldFlags,
                borderColor=red, fillColor=green, textColor=blue,forceBorder=False,
                tooltip = 'LB%d value=%r' % (i,value),
                options=[('A','Av'),'B',('C','Cv'),('D','Dv'),'E',('F',),('G','Gv'),'H'])
        canv.showPage()
        canv.save()

def makeSuite():
    return makeSuiteForClasses(PdfFormTestCase)

#noruntests
if __name__ == "__main__":
    unittest.TextTestRunner().run(makeSuite())
    printLocation()
