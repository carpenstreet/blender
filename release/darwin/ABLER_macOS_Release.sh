# 사용되는 변수들 초기화
testing=false
arch_setting=false # arch_setting : false -> arm64, true -> x86_64
_codesign_cert="$(security find-identity -v -p codesigning | grep "Developer ID Application: carpenstreet Inc." | awk 'NR==1{print $2}')" # get codesign cert from keychain
_mount_dir="../../../build_darwin/bin"
_qt_loc=""

# dmg가 저장될 로컬 경로
_dmg_dir="$HOME/Desktop/abler-release/latest.dmg"

# test 아규먼트 처리
while [[ $# -gt 0 ]]; do
    key=$1
    case $key in
        -t|--test)
            testing=true
            shift
            shift
            ;;
        -v|--version)
            ABLER_VERSION="$2"
            shift
            shift
            ;;
        -s|--sparkle-dir)
            SPARKLE_DIR="$2"
            shift
            shift
            ;;
        -i|--image-address)
            ABLER_IMAGE_ADDRESS="$2"
            shift
            shift
            ;;
        -h|--help)
            echo "Usage:"
            echo " $(basename "$0") (--test) --version ABLER_VERSION --sparkle-dir SPARKLE_DIR --image-address ABLER_IMAGE_ADDRESS"
            exit 1
            ;;
    esac
done

# 아키텍쳐 받아오기
if uname -m | grep -q "x86_64"; then
   arch_setting=true
fi

# 빌드
make update
make -j $(sysctl -n hw.physicalcpu)
cd ./release/darwin || exit

# dylib 번들링 작업
if ! "${testing}"; then
    # qt 기본 제공 번들러
    macdeployqt ${_mount_dir}/ABLER.app -verbose=3

    # macdeployqt가 제대로 작동을 안해서 추가적으로 dylibbundler를 사용함
    echo ; echo -n "bundling .dylib libraries"
    for f in $(find "${_mount_dir}/ABLER.app" -name "*.dylib"); do
        echo "fixing ${f}"
        if "${arch_setting}"; then
          dylibbundler -cd -of -b -x "${f}" -d "${_mount_dir}"/ABLER.app/Contents/Frameworks/ -p @executable_path/../Frameworks/ -s /usr/local/lib
        fi
        dylibbundler -cd -of -b -x "${f}" -d "${_mount_dir}"/ABLER.app/Contents/Frameworks/ -p @executable_path/../Frameworks/ -s /opt/homebrew/lib
    done

    # bundle.sh 실행
    sh ./bundle.sh --source "${_mount_dir}" --dmg "${_dmg_dir}" --bundle-id com.acon3d.abler.release --username global@acon3d.com --password "@keychain:altool-password" --codesign "${_codesign_cert}"
else
    # qt 기본 제공 번들러
    macdeployqt ${_mount_dir}/ABLER.app -verbose=3

    # macdeployqt가 제대로 작동을 안해서 추가적으로 dylibbundler를 사용함
    echo ; echo -n "bundling .dylib libraries"
    for f in $(find "${_mount_dir}/ABLER.app" -name "*.dylib"); do
        echo "fixing ${f}"
        if "${arch_setting}"; then
          dylibbundler -cd -of -od -b -x "${f}" -d "${_mount_dir}"/ABLER.app/Contents/Frameworks/ -p @executable_path/../Frameworks/ -s /usr/local/lib
        fi
        dylibbundler -cd -of -od -b -x "${f}" -d "${_mount_dir}"/ABLER.app/Contents/Frameworks/ -p @executable_path/../Frameworks/ -s /opt/homebrew/lib
    done

    # bundle.sh 실행
    sh ./bundle.sh --source "${_mount_dir}" --dmg "${_dmg_dir}" --bundle-id com.acon3d.abler.release --username global@acon3d.com --password "@keychain:altool-password" --codesign "${_codesign_cert}" --test
fi

# generate_appcast.sh 실행
sh ./generate_appcast.sh --dmg "${_dmg_dir}" --version "${ABLER_VERSION}" --sparkle-dir "${SPARKLE_DIR}"
