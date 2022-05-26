testing=false
# Handle arguments.
while [[ $# -gt 0 ]]; do
    key=$1
    case $key in
        -t|--test)
            testing=true
            shift
            shift
            ;;
    esac
done
# cd ~/Desktop/ACON3D/RND_aconBlender/launcher_abler
# pyinstaller --icon=icon.icns --onefile --windowed --uac-admin AblerLauncher.py -y --argv-emulation
cd ~/Desktop/ABLER/blender || exit
git submodule update --init --recursive
cd ./launcher_qt || exit
make
#cmake -S ./launcher_qt -B ./launcher_qt/build
#cmake --build ./launcher_qt/build --target ALL_BUILD --config Release
cd ..
make
cd ./release/darwin || exit
_mount_dir="/Users/sdkfile/Desktop/ABLER/build_darwin/bin"
if ! "${testing}"; then
    macdeployqt ${_mount_dir}/ABLER.app -verbose=3

    echo ; echo -n "bundling .dylib libraries"
    for f in $(find "${_mount_dir}/ABLER.app" -name "*.dylib"); do
        echo "fixing ${f}"
        dylibbundler -cd -b -x "${f}" -d "${_mount_dir}"/ABLER.app/Contents/Frameworks/ -p @executable_path/../Frameworks/ -s /opt/homebrew/lib
    done

    python ~/Desktop/ABLER/ABLER-Misc/ABLER_installer_assets/macdeployqtfix.py "${_mount_dir}"/ABLER.app/Contents/macOS/AblerLauncher /opt/homebrew/Cellar/qt/6.2.3_1/
    python ~/Desktop/ABLER/ABLER-Misc/ABLER_installer_assets/macdeployqtfix.py "${_mount_dir}"/ABLER.app/Contents/macOS/ABLER /opt/homebrew/Cellar/qt/6.2.3_1/
    sh ./bundle.sh --source "${_mount_dir}" --dmg ~/Desktop/ABLER.dmg --bundle-id com.acon3d.abler.release --username global@acon3d.com --password "@keychain:altool-password" --codesign 2ADA4D39CF99C227755D54DEC93F41ACEAAE3707
else
    macdeployqt "${_mount_dir}"/ABLER.app
    # python macdeployqtfix.py "${_mount_dir}"/ABLER.app/Contents/macOS/AblerLauncher /opt/homebrew/Cellar/qt/6.1.3/
    python ~/Desktop/ABLER/ABLER-Misc/ABLER_installer_assets/macdeployqtfix.py "${_mount_dir}"/ABLER.app/Contents/macOS/ABLER /opt/homebrew/Cellar/qt/6.2.3_1/
    sh ./bundle.sh --source "${_mount_dir}" --dmg ~/Desktop/ABLER.dmg --bundle-id com.acon3d.abler.release --username global@acon3d.com --password "@keychain:altool-password" --codesign 2ADA4D39CF99C227755D54DEC93F41ACEAAE3707 --test
fi
