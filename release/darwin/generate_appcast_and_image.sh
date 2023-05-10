# Before running this script, you need to do the following:
# 1. Generate Keys by using generate_keys command in Sparkle
# 2. Update version number in CMakelists.txt
# 3. Update SUPublicEDKey, SUFeedURL, and CFBundleLocalizations for appcast.xml
# 4. Successfully build the app

# Handle arguments.
while [[ $# -gt 0 ]]; do
    key=$1
    case $key in
        -d|--dmg)
            DMG_DIR="$2"
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
            echo " $(basename "$0") --dmg DMG_DIR --version ABLER_VERSION --sparkle-dir SPARKLE_DIR --image-address ABLER_IMAGE_ADDRESS"
            exit 1
            ;;
    esac
done

_work_dir="$(dirname "${DMG_DIR}")"
mkdir -p "${_work_dir}"
cd "${_work_dir}"

[[ "$(uname -m)" = "x86_64" ]] && _cpu="intel" || _cpu="silicon"

# Move old versions
echo "Moving old versions..."

mkdir -p ./old_versions
find . -name "ABLER_MacOS_*.dmg" -exec mv {} ./old_versions \;
mv ./*.xml ./old_versions

# Generate appcast
echo "Generating appcast..."

# Sparkle 의 generate_appcast 에서 url 의 prefix 만 변경가능하고, dmg 는 기존 이름 그대로 유지하기 때문에
# generate_appcast 실행 후 이름을 변경

"${SPARKLE_DIR}"/bin/generate_appcast . --download-url-prefix="${ABLER_IMAGE_ADDRESS}"

# Change image name
mv "${DMG_DIR}" ./ABLER_MacOS_"${_cpu}"_v"${ABLER_VERSION}".dmg

# Change appcast name
mv ./*.xml ./appcast_"${_cpu}"_v"${ABLER_VERSION}".xml

echo "Successfully generated appcast. Please upload dmg and appcast via Abler Deploy Manager website."

open .