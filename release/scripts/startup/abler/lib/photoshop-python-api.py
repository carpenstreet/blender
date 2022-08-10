from photoshop import Session
import photoshop.api as psi
import os
from PIL import Image

dir_path = "C:/Users/master/Desktop/Coni's room"
file_lst = os.listdir(dir_path)

im = Image.open(dir_path + "/" + file_lst[0], 'r')
width, height = im.size

psd_file = dir_path + "/" + os.path.basename(dir_path) + ".psd"

try:
    with Session(psd_file, action="new_document",auto_close=True) as ps:
        desc = ps.ActionDescriptor
        event_id = ps.app.charIDToTypeID("Plc ")  # `Plc` need one space in here.

        for file in reversed(file_lst):
            file_path = dir_path + "/" + file
            desc.putPath(ps.app.charIDToTypeID("null"), file_path)
            ps.app.executeAction(ps.app.charIDToTypeID("Plc "), desc)
            
        ps.active_document.resizeImage(width,height)
        ps.active_document.saveAs(psd_file, psi.PhotoshopSaveOptions(), True)

except Exception as e:
    raise e

