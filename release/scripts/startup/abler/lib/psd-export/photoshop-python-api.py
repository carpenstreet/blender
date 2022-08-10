from photoshop import Session
import os

dir_path = "C:/Users/master/Downloads/Coni's room"
file_lst = os.listdir(dir_path)

psd_file = dir_path + "/" + "Coni.psd"

try:
    with Session(action="new_document", auto_close=True) as ps:
        desc = ps.ActionDescriptor
        event_id = ps.app.charIDToTypeID("Plc ")  # `Plc` need one space in here.

        for file in reversed(file_lst):
            file_path = dir_path + "/" + file
            desc.putPath(ps.app.charIDToTypeID("null"), file_path)
            ps.app.executeAction(ps.app.charIDToTypeID("Plc "), desc)
        
        ps.active_document.saveAs(psd_file, ps.PhotoshopSaveOptions(), True)

except Exception as e:
    raise e

