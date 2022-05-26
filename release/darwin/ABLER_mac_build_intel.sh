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
# cd ~/Desktop/RND_aconBlender/launcher_abler
# pyinstaller --icon=icon.icns --onefile --windowed --uac-admin AblerLauncher.py -y --argv-emulation
cd ~/Desktop/ACON3D/RND_aconBlender
git submodule update --init --recursive
cmake -S ./launcher_qt -B ./launcher_qt/build
cmake --build ./launcher_qt/build --target ALL_BUILD --config Release
make
cd ./release/darwin
_mount_dir="/Users/sdkfile/Desktop/ACON3D/build_darwin/bin"

if ! "${testing}"; then
    macdeployqt ${_mount_dir}/ABLER.app -verbose=3

    echo ; echo -n "bundling .dylib libraries"
    for f in $(find "${_mount_dir}/ABLER.app" -name "*.dylib"); do
        echo "fixing ${f}"
        dylibbundler -cd -b -x "${f}" -d "${_mount_dir}"/ABLER.app/Contents/Frameworks/ -p @executable_path/../Frameworks/ -s /usr/local/lib
    done

    python ~/Desktop/ACON3D/RND_BlenderPlugins/ABLER_installer_assets/macdeployqtfix.py "${_mount_dir}"/ABLER.app/Contents/macOS/AblerLauncher /opt/homebrew/Cellar/qt/6.1.3/
    python ~/Desktop/ACON3D/RND_BlenderPlugins/ABLER_installer_assets/macdeployqtfix.py "${_mount_dir}"/ABLER.app/Contents/macOS/ABLER /opt/homebrew/Cellar/qt/6.1.3/
    sh ./bundle.sh --source ~/Desktop/ACON3D/build_darwin/bin --dmg ~/Desktop/ABLER.dmg --bundle-id com.acon3d.abler.release --username global@acon3d.com --password "@keychain:altool-password" --codesign ED321BF2FD82281C72FCEB2E8BAD98543897592E
else
    sh ./bundle.sh --source ~/Desktop/ACON3D/build_darwin/bin --dmg ~/Desktop/ABLER.dmg --bundle-id com.acon3d.abler.release --username global@acon3d.com --password "@keychain:altool-password" --codesign ED321BF2FD82281C72FCEB2E8BAD98543897592E --test
fi
