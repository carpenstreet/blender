# import photoshop.api as ps

# app = ps.Application()
# doc = app.documents.add()
# new_doc = doc.artLayers.add()
# text_color = ps.SolidColor()
# text_color.rgb.red = 0
# text_color.rgb.green = 255
# text_color.rgb.blue = 0
# new_text_layer = new_doc
# new_text_layer.kind = ps.LayerKind.TextLayer
# new_text_layer.textItem.contents = 'Hello, World!'
# new_text_layer.textItem.position = [160, 167]
# new_text_layer.textItem.size = 40
# new_text_layer.textItem.color = text_color
# options = ps.JPEGSaveOptions(quality=5)
# # # save to jpg
# jpg = 'd:/hello_world.jpg'
# doc.saveAs(jpg, options, asCopy=True)
# app.doJavaScript(f'alert("save to jpg: {jpg}")')

## Import Image As Layer
from photoshop import Session

with Session(action="new_document") as ps:
    desc = ps.ActionDescriptor
    event_id = ps.app.charIDToTypeID("Plc ")  # `Plc` need one space in here.

    desc.putPath(ps.app.charIDToTypeID("null"), "C:/Users/master/Downloads/Coni's room/Coni's room.png")
    ps.app.executeAction(ps.app.charIDToTypeID("Plc "), desc)

    desc.putPath(ps.app.charIDToTypeID("null"), "C:/Users/master/Downloads/Coni's room/Coni's room_line.png")
    ps.app.executeAction(ps.app.charIDToTypeID("Plc "), desc)

    desc.putPath(ps.app.charIDToTypeID("null"), "C:/Users/master/Downloads/Coni's room/Coni's room_line_shadow.png")
    ps.app.executeAction(ps.app.charIDToTypeID("Plc "), desc)
