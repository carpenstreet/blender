testing=false
# arch_setting : false -> arm64, true -> x86_64
arch_setting=false
if uname -m | grep -q "x86_64"; then
   arch_setting=true
fi
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
# get codesign cert from keychain
_codesign_cert="$(security find-identity -v -p codesigning | grep "Developer ID Application: carpenstreet Inc." | awk '{print $2}')"

# build AblerLauncher and ABLER
cd ../.. || exit
git submodule update --init --recursive
cd ./launcher_qt || exit
make
cd ..
make
cd ./release/darwin || exit
_mount_dir="../../../build_darwin/bin"
if ! "${testing}"; then
    macdeployqt ${_mount_dir}/ABLER.app -verbose=3

    echo ; echo -n "bundling .dylib libraries"
    for f in $(find "${_mount_dir}/ABLER.app" -name "*.dylib"); do
        echo "fixing ${f}"
        if "${arch_setting}"; then
          dylibbundler -cd -b -x "${f}" -d "${_mount_dir}"/ABLER.app/Contents/Frameworks/ -p @executable_path/../Frameworks/ -s /usr/local/lib
        fi
        dylibbundler -cd -b -x "${f}" -d "${_mount_dir}"/ABLER.app/Contents/Frameworks/ -p @executable_path/../Frameworks/ -s /opt/homebrew/lib
    done

    python ./macdeployqtfix.py "${_mount_dir}"/ABLER.app/Contents/macOS/AblerLauncher /opt/homebrew/Cellar/qt/6.2.3_1/
    python ./macdeployqtfix.py "${_mount_dir}"/ABLER.app/Contents/macOS/ABLER /opt/homebrew/Cellar/qt/6.2.3_1/
    sh ./bundle.sh --source "${_mount_dir}" --dmg ~/Desktop/ABLER.dmg --bundle-id com.acon3d.abler.release --username global@acon3d.com --password "@keychain:altool-password" --codesign "${_codesign_cert}"
else
    macdeployqt "${_mount_dir}"/ABLER.app
    python ./macdeployqtfix.py "${_mount_dir}"/ABLER.app/Contents/macOS/ABLER /opt/homebrew/Cellar/qt/6.2.3_1/
    sh ./bundle.sh --source "${_mount_dir}" --dmg ~/Desktop/ABLER.dmg --bundle-id com.acon3d.abler.release --username global@acon3d.com --password "@keychain:altool-password" --codesign "${_codesign_cert}" --test
fi
