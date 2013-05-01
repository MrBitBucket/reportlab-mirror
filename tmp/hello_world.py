from reportlab.pdfgen.canvas import Canvas
canv = Canvas('hello-world.pdf')
canv.drawString(72,8*72,'Hello World!')
canv.save()
