from photoshop import Session
import photoshop.api as psi
import os

dir_path = "C:/Users/master/Desktop/Coni's room"
file_lst = os.listdir(dir_path)

psd_file = dir_path + "/" + os.path.basename(dir_path) + ".psd"
app = psi.Application()
doc = app.documents.add(4800,2700)
doc.saveAs(psd_file, psi.PhotoshopSaveOptions(), True)
doc.close()

# try:
with Session(psd_file, action="open",auto_close=True) as ps:
    desc = ps.ActionDescriptor
    event_id = ps.app.charIDToTypeID("Plc ")  # `Plc` need one space in here.

    for file in reversed(file_lst):
        file_path = dir_path + "/" + file
        desc.putPath(ps.app.charIDToTypeID("null"), file_path)
        ps.app.executeAction(ps.app.charIDToTypeID("Plc "), desc)
        
        ps.active_document.save()

# except Exception as e:
#     raise e

