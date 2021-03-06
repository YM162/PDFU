import os
import pikepdf
from pdfrw import PdfReader, PdfWriter
from pdfrw.findobjs import wrap_object , find_objects
from pdfrw.objects import PdfName
from pikepdf import Pdf
import re

def meta(prepdf):
    #print(prepdf.pages[0]["/Contents"][0].read_bytes())
    page = prepdf.pages[0]
    instructions = pikepdf.parse_content_stream(page)
    data = pikepdf.unparse_content_stream(instructions)
    data = data.decode('ascii')
    pattern="<(.*?)>"
    
    metalist = []
    
    for substring in re.findall(pattern,data):
        bytes_object = bytes.fromhex(substring)
        text = bytes_object.decode("latin-1")
        metalist.append(text)
    metadict = {
        "Archivo":metalist[0],
        "Autor":metalist[1],
        "Asignatura":metalist[2],
        "Curso y Grado":metalist[3],
        "Facultad":metalist[4],
        "Universidad":metalist[5]
    }
    
    return metadict
    
def deembed(pdf_path):
    '''
    Deembeds the pdf and creates a new PDF in the same folder with each embedded page
    in a new page.
    
    Args:
        pdf_path: The path where the pdf file is located.
        
    Returns:
        return_msg: Dict. with three values:
            Success: bool indicating whether the process was successful.
            return_path: If successful, returns the path of the deembedded file.
            Error: If unsuccessful, returns a description of the error.
    '''
    print("Trying to Deembed:",pdf_path)
    return_msg={"Success":False,"return_path":"","Error":"","Meta":{}}
    try:
        if pdf_path[-4:]!=".pdf":
            return_msg["Success"]=False
            return_msg["Error"]="File is not a .pdf file."
            return return_msg
        
        prepdf=Pdf.open(pdf_path)
        
        try:
            metadict = meta(prepdf)
            return_msg["Meta"]=metadict
        except:
            print("Meta not extracted. Probably not a W file.")
        
        prepdf.save(pdf_path[:-4]+"_inter.pdf")
        prepdf.close()
        
        pdf = PdfReader(pdf_path[:-4]+"_inter.pdf")
        xobjs=list(find_objects(pdf.pages,valid_subtypes=(PdfName.Form, PdfName.Dummy)))
        p??ginas=[]
        for item in xobjs:
            p??ginas.append(wrap_object(item, 1000, 0.5*72))
        if len(xobjs)==0:
            os.remove(pdf_path[:-4]+"_inter.pdf")
            return_msg["Success"]=False
            return_msg["Error"]="No embedded pages found."
            return return_msg

        output=pdf_path[:-4]+"_deembedded.pdf"
        writer = PdfWriter(output)
        writer.addpages(p??ginas)
        writer.write()

        os.remove(pdf_path[:-4]+"_inter.pdf")
        return_msg["Success"]=True
        return_msg["return_path"]=output
        return return_msg
    except Exception as e:
        return_msg["Success"]=False
        return_msg["Error"]=e
        return return_msg


if __name__ == "__main__":
    print('Call from the "pdfu" command.')
    print(deembed("../tests/testpdf/AnonimoTema9.pdf"))
    