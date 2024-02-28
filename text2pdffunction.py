#from reportlab.lib.pagesizes import letter
#from reportlab.pdfgen import canvas
#from reportlab.lib.utils import ImageReader
#from PIL import Image
#from textwrap import wrap
#from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import reportlab.lib.styles
from reportlab import rl_config
from os import path


def main(pathfileTXT):

    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    styleH = styles['Heading1']
    story = []
    
    ptr = open(pathfileTXT, "r")  # text file I need to convert
    
    
    (head,tail)=path.split(pathfileTXT)
    (head2,tail2)=path.splitext(tail)
    filename=head2
    
    c = SimpleDocTemplate(head+'/'+filename+'.pdf',rightMargin=72,leftMargin=72,
                            topMargin=72,bottomMargin=58)
    
    story.append(Paragraph(filename,styleH))
    
    
    lineas = ptr.readlines()
    ptr.close()
    
    #numeroLinea = 0
    n=0
    #topmargin=100
    #space=topmargin
    
    for linea in lineas:
        #print(n)
        n+=1    
        #print(linea.strip())
        #
        text=linea.strip()
        story.append(Paragraph(text,styleN))
        story.append(Spacer(1, 5))
        
    
    c.build(story)
    