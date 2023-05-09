tell application "Finder"
    tell disk "ABLER"
        open
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        set the bounds of container window to {100, 100, 640, 472}
        set theViewOptions to icon view options of container window
        set arrangement of theViewOptions to not arranged
        set icon size of theViewOptions to 128
        set background picture of theViewOptions to file ".background:background.tif"
        set position of item " " of container window to {400, 190}
        set position of item ".background" of container window to {135, 100}
        set position of item ".fseventsd" of container window to {135, 100}
        set position of item "README.txt" of container window to {400, 100}
        set position of item "abler.app" of container window to {135, 190}
        update without registering applications
        delay 5
        close
    end tell
end tell
