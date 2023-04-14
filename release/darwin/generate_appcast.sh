# Before running this script, you need to do the following:
# 1. Generate Keys by using generate_keys command in Sparkle
# 2. Update version number in CMakelists.txt
# 3. Update SUPublicEDKey, SUFeedURL, and CFBundleLocalizations for appcast.xml
# 4. Successfully build the app

# Default Settings

# sparkle Framework 경로
_sparkle_dir="/opt/homebrew/Caskroom/sparkle"
# dmg 파일이 올라갈 서버 주소
#_dmg_url="https://download.abler.world/mac/dmg/latest.dmg"
_dmg_url="https://abler-dev-assets.s3.ap-northeast-2.amazonaws.com/macos-updater/latest.dmg"
_version="0.3.3"

# Handle arguments.
while [[ $# -gt 0 ]]; do
    key=$1
    case $key in
        -d|--dmg)
            DMG_DIR="$2"
            shift
            shift
            ;;
        -h|--help)
            echo "Usage:"
            echo " $(basename "$0") --dmg DMG_DIR"
            exit 1
            ;;
    esac
done

_work_dir="$(dirname "${DMG_DIR}")"
mkdir -p "${_work_dir}"
cd "${_work_dir}"

# Move old versions
echo "Moving old versions..."

mkdir -p ./old_versions
find . -name "ABLER_MacOS_v*" -exec mv {} ./old_versions \;
mv ./*.xml ./old_versions

# Generate appcast
echo "Generating appcast..."

# Sparkle 의 generate_appcast 에서 url 의 prefix 만 변경가능하고, dmg 는 기존 이름 그대로 유지하기 때문에
# generate_appcast 실행 후 이름을 변경

"${_sparkle_dir}"/2.4.0/bin/generate_appcast . --download-url-prefix="${_dmg_url}"

# Change image name
mv "${DMG_DIR}" ./ABLER_MacOS_v"${_version}".dmg

# Change appcast name
mv ./appcast.xml ./appcast_v"${_version}".xml

echo "Successfully generated appcast. Please upload dmg and appcast via Abler Deploy Manager website."

open .