# 사용되는 변수들 초기화
testing=false
arch_setting=false # arch_setting : false -> arm64, true -> x86_64
_codesign_cert="$(security find-identity -v -p codesigning | grep "Developer ID Application: carpenstreet Inc." | awk '{print $2}')" # get codesign cert from keychain
_mount_dir="../../../build_darwin/bin"
_qt_loc=""

# test 아규먼트 처리
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

# 아키텍쳐 받아오기
if uname -m | grep -q "x86_64"; then
   arch_setting=true
fi

# 빌드
make update
make
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
          dylibbundler -cd -b -x "${f}" -d "${_mount_dir}"/ABLER.app/Contents/Frameworks/ -p @executable_path/../Frameworks/ -s /usr/local/lib
        fi
        dylibbundler -cd -b -x "${f}" -d "${_mount_dir}"/ABLER.app/Contents/Frameworks/ -p @executable_path/../Frameworks/ -s /opt/homebrew/lib
    done

    # dylibbundler가 제대로 작돋하지 않을 경우를 대비해서 아래와 같은 스크립트를 추가적으로 실행해줌 -> 링크는 https://github.com/arl/macdeployqtfix 참조
    if "${arch_setting}"; then
      # 가장 최신 qt 버전을 찾아서 실행
      _qt_loc="$(for dir in /usr/local/Cellar/qt/*/; do basename "$dir"; done | sort --reverse | head -1)"
      python ./macdeployqtfix.py "${_mount_dir}"/ABLER.app/Contents/macOS/AblerLauncher /usr/local/Cellar/qt/"${_qt_loc}"/
      python ./macdeployqtfix.py "${_mount_dir}"/ABLER.app/Contents/macOS/ABLER /usr/local/Cellar/qt/"${_qt_loc}"/
    else
      # 가장 최신 qt 버전을 찾아서 실행
      _qt_loc="$(for dir in /opt/homebrew/Cellar/qt/*/; do basename "$dir"; done | sort --reverse | head -1)"
      python ./macdeployqtfix.py "${_mount_dir}"/ABLER.app/Contents/macOS/AblerLauncher /opt/homebrew/Cellar/qt/"${_qt_loc}"/
      python ./macdeployqtfix.py "${_mount_dir}"/ABLER.app/Contents/macOS/ABLER /opt/homebrew/Cellar/qt/"${_qt_loc}"/
    fi

    # bundle.sh 실행
    sh ./bundle.sh --source "${_mount_dir}" --dmg ~/Desktop/ABLER.dmg --bundle-id com.acon3d.abler.release --username global@acon3d.com --password "@keychain:altool-password" --codesign "${_codesign_cert}"
else
    # qt 기본 제공 번들러
    macdeployqt ${_mount_dir}/ABLER.app -verbose=3

    # macdeployqt가 제대로 작동을 안해서 추가적으로 dylibbundler를 사용함
    echo ; echo -n "bundling .dylib libraries"
    for f in $(find "${_mount_dir}/ABLER.app" -name "*.dylib"); do
        echo "fixing ${f}"
        if "${arch_setting}"; then
          dylibbundler -cd -b -x "${f}" -d "${_mount_dir}"/ABLER.app/Contents/Frameworks/ -p @executable_path/../Frameworks/ -s /usr/local/lib
        fi
        dylibbundler -cd -b -x "${f}" -d "${_mount_dir}"/ABLER.app/Contents/Frameworks/ -p @executable_path/../Frameworks/ -s /opt/homebrew/lib
    done

    # dylibbundler가 제대로 작돋하지 않을 경우를 대비해서 아래와 같은 스크립트를 추가적으로 실행해줌 -> 링크는 https://github.com/arl/macdeployqtfix 참조
    if "${arch_setting}"; then
      # 가장 최신 qt 버전을 찾아서 실행
      _qt_loc="$(for dir in /usr/local/Cellar/qt/*/; do basename "$dir"; done | sort --reverse | head -1)"
      python ./macdeployqtfix.py "${_mount_dir}"/ABLER.app/Contents/macOS/AblerLauncher /usr/local/Cellar/qt/"${_qt_loc}"/
      python ./macdeployqtfix.py "${_mount_dir}"/ABLER.app/Contents/macOS/ABLER /usr/local/Cellar/qt/"${_qt_loc}"/
    else
      # 가장 최신 qt 버전을 찾아서 실행
      _qt_loc="$(for dir in /opt/homebrew/Cellar/qt/*/; do basename "$dir"; done | sort --reverse | head -1)"
      python ./macdeployqtfix.py "${_mount_dir}"/ABLER.app/Contents/macOS/AblerLauncher /opt/homebrew/Cellar/qt/"${_qt_loc}"/
      python ./macdeployqtfix.py "${_mount_dir}"/ABLER.app/Contents/macOS/ABLER /opt/homebrew/Cellar/qt/"${_qt_loc}"/
    fi

    # bundle.sh 실행
    sh ./bundle.sh --source "${_mount_dir}" --dmg ~/Desktop/ABLER.dmg --bundle-id com.acon3d.abler.release --username global@acon3d.com --password "@keychain:altool-password" --codesign "${_codesign_cert}" --test
fi
