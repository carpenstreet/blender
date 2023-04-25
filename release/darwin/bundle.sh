#!/usr/bin/env bash
#
# Script to create a macOS dmg file for Blender builds, including code
# signing and notarization for releases.

# Check that we have all needed tools.
for i in osascript git codesign hdiutil xcrun ; do
    if [ ! -x "$(which ${i})" ]; then
        echo "Unable to execute command $i, macOS broken?"
        exit 1
    fi
done

# Defaults settings.
_script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
_volume_name="ABLER"
_tmp_dir="$(mktemp -d)"
_tmp_dmg="/tmp/abler-tmp.dmg"
_background_image="${_script_dir}/background.tif"
_mount_dir="/Volumes/${_volume_name}"
_entitlements="${_script_dir}/entitlements.plist"
testing=false
# Handle arguments.
while [[ $# -gt 0 ]]; do
    key=$1
    case $key in
        -s|--source)
            SRC_DIR="$2"
            shift
            shift
            ;;
        -d|--dmg)
            DEST_DMG="$2"
            shift
            shift
            ;;
        -b|--bundle-id)
            N_BUNDLE_ID="$2"
            shift
            shift
            ;;
        -u|--username)
            N_USERNAME="$2"
            shift
            shift
            ;;
        -p|--password)
            N_PASSWORD="$2"
            shift
            shift
            ;;
        -c|--codesign)
            C_CERT="$2"
            shift
            shift
            ;;
        --background-image)
            _background_image="$2"
            shift
            shift
            ;;
        -t|--test)
            testing=true
            shift
            shift
            ;;
        -h|--help)
            echo "Usage:"
            echo " $(basename "$0") --source DIR --dmg IMAGENAME "
            echo "    optional arguments:"
            echo "    --codesign <certname>"
            echo "    --username <username>"
            echo "    --password <password>"
            echo "    --bundle-id <bundleid>"
            echo " Check https://developer.apple.com/documentation/security/notarizing_your_app_before_distribution/customizing_the_notarization_workflow "
            exit 1
            ;;
    esac
done

if [ ! -d "${SRC_DIR}/ABLER.app" ]; then
    echo "use --source parameter to set source directory where ABLER.app can be found"
    exit 1
fi

if [ -z "${DEST_DMG}" ]; then
    echo "use --dmg parameter to set output dmg name"
    exit 1
fi

# Destroy destination dmg if there is any.
test -f "${DEST_DMG}" && rm "${DEST_DMG}"
if [ -d "${_mount_dir}" ]; then
    echo -n "Ejecting existing abler volume.."
    DEV_FILE=$(mount | grep "${_mount_dir}" | awk '{ print $1 }')
    diskutil eject "${DEV_FILE}" || exit 1
    echo
fi

if [ ! -z "${C_CERT}" ]; then
    # Codesigning requires all libs and binaries to be signed separately.
    echo -n "Codesigning Python"
    for f in $(find "${SRC_DIR}/ABLER.app/Contents/Resources" -name "python*"); do
        if [ -x ${f} ] && [ ! -d ${f} ]; then
            codesign --remove-signature "${f}"
            codesign --deep --force --verbose --timestamp --options runtime --entitlements="${_entitlements}" --sign "${C_CERT}" "${f}"
        fi
    done
    echo ; echo -n "Codesigning .dylib, .so and .o libraries"
    for f in $(find "${SRC_DIR}/ABLER.app" -name "*.dylib" -o -name "*.so" -o -name "*.o"); do
        codesign --remove-signature "${f}"
        codesign --deep --force --verbose --timestamp --options runtime --entitlements="${_entitlements}" --sign "${C_CERT}" "${f}"
    done
    # Codesigning .egg files
    echo ; echo -n "Codesigning .egg files"
    for f in $(find "${SRC_DIR}/ABLER.app" -name "*.egg"); do
        echo "Processing file $f..."
        # Get the file path and name without extension
        file_path=$(dirname "$f")
        file_name=$(basename "$f" .egg)
        
        # Rename the file to have a .zip extension
        mv "$file_path/$file_name.egg" "$file_path/$file_name.zip"

        temp_dir="$file_path/$file_name" # zip 실행시 상대경로 문제로 시스템 temp 폴더 사용 안함

        unzip "$file_path/$file_name.zip" -d "$temp_dir"
        rm "$file_path/$file_name.zip"

        for so_file in "$temp_dir"/*.so; do 
            codesign --remove-signature "$so_file"
            codesign --deep --force --verbose --timestamp --options runtime --entitlements="${_entitlements}" --sign "${C_CERT}" "$so_file"
        done

        pushd "$temp_dir"
        zip -r "../$file_name.zip" "."
        popd
        mv "$file_path/$file_name.zip" "$file_path/$file_name.egg"

        codesign --remove-signature "$file_path/$file_name.egg"
        codesign --deep --force --verbose --timestamp --options runtime --entitlements="${_entitlements}" --sign "${C_CERT}" "$file_path/$file_name.egg"

        rm -rf "$temp_dir"
    done
    echo ; echo -n "Codesigning .framework libraries"
    for f in $(find "${SRC_DIR}/ABLER.app" -name "*.framework"); do
        if [ -d "${f}/Versions/A" ]; then
            codesign --remove-signature "${f}/Versions/A"
            codesign --deep --force --verbose --timestamp --options runtime --entitlements="${_entitlements}" --sign "${C_CERT}" "${f}/Versions/A"
        elif [ -d "${f}/Versions/B" ]; then
            codesign --remove-signature "${f}/Versions/B"
            codesign --deep --force --verbose --timestamp --options runtime --entitlements="${_entitlements}" --sign "${C_CERT}" "${f}/Versions/B"
        fi
    done

    sleep 30

    echo ; echo -n "Codesigning ABLER"
    codesign --remove-signature "${SRC_DIR}/ABLER.app/Contents/macOS/ABLER"
    codesign --deep --force --verbose --timestamp --options runtime --entitlements="${_entitlements}" --sign "${C_CERT}" "${SRC_DIR}/ABLER.app/Contents/macOS/ABLER"
    echo

    echo ; echo -n "Codesigning ABLER.app"
    codesign --remove-signature "${SRC_DIR}/ABLER.app"
    codesign --deep --force --verbose --timestamp --options runtime --entitlements="${_entitlements}" --sign "${C_CERT}" "${SRC_DIR}/ABLER.app"
    echo
else
    echo "No codesigning cert given, skipping..."
fi

# Copy dmg contents.
echo -n "Copying ABLER.app..."
cp -R "${SRC_DIR}/ABLER.app" "${_tmp_dir}/" || exit 1
echo

# Create the disk image.
_directory_size=$(du -sh ${_tmp_dir} | awk -F'[^0-9]*' '$0=$1')
_image_size=$(echo "${_directory_size}" + 1400 | bc) # extra 400 need for codesign to work (why on earth?)

echo
echo -n "Creating disk image of size ${_image_size}M.."
test -f "${_tmp_dmg}" && rm "${_tmp_dmg}"
hdiutil create -size "${_image_size}m" -fs HFS+ -srcfolder "${_tmp_dir}" -volname "${_volume_name}" -format UDRW "${_tmp_dmg}" -mode 755

echo "Mounting readwrite image..."
hdiutil attach -readwrite -noverify -noautoopen "${_tmp_dmg}"

echo "Setting background picture.."
if ! test -z "${_background_image}"; then
    echo "Copying background image ..."
    test -d "${_mount_dir}/.background" || mkdir "${_mount_dir}/.background"
    _background_image_NAME=$(basename "${_background_image}")
    cp "${_background_image}" "${_mount_dir}/.background/${_background_image_NAME}"
fi

echo "Creating link to /Applications ..."
ln -s /Applications "${_mount_dir}/Applications"
echo "Renaming Applications to empty string."
mv ${_mount_dir}/Applications "${_mount_dir}/ "

echo "Running applescript to set folder looks ..."
cat "${_script_dir}/abler.applescript" | osascript

echo "Waiting after applescript ..."
sleep 5



# Need to eject dev files to remove /dev files and free .dmg for converting
echo "Unmounting rw disk image ..."
DEV_FILE=$(mount | grep "${_mount_dir}" | awk '{ print $1 }')
diskutil eject "${DEV_FILE}"

sleep 3

echo "Compressing disk image ..."
hdiutil convert "${_tmp_dmg}" -format UDZO -o "${DEST_DMG}"

# Codesign the dmg
if [ ! -z "${C_CERT}" ]; then
    echo -n "Codesigning dmg..."
    codesign --deep --verbose --timestamp --force --sign "${C_CERT}" "${DEST_DMG}"
    echo
fi

# Cleanup
rm -rf "${_tmp_dir}"
rm "${_tmp_dmg}"

# Notarize
if [ ! -z "${N_USERNAME}" ] && [ ! -z "${N_PASSWORD}" ] && [ ! -z "${N_BUNDLE_ID}" ] && ! "$testing"; then
    # Send to Apple
    echo "Sending ${DEST_DMG} for notarization..."
    _tmpout=$(mktemp)
    echo xcrun altool --notarize-app --verbose -f "${DEST_DMG}" --primary-bundle-id "${N_BUNDLE_ID}" --username "${N_USERNAME}" --password "${N_PASSWORD}"
    xcrun altool --notarize-app --verbose -f "${DEST_DMG}" --primary-bundle-id "${N_BUNDLE_ID}" --username "${N_USERNAME}" --password "${N_PASSWORD}" >${_tmpout} 2>&1

    # Parse request uuid
    _requuid=$(cat "${_tmpout}" | grep "RequestUUID" | awk '{ print $3 }')
    echo "RequestUUID: ${_requuid}"
    if [ ! -z "${_requuid}" ]; then
        # Wait for Apple to confirm notarization is complete
        echo "Waiting for notarization to be complete.."
        for c in {200..0};do
            sleep 60
            xcrun altool --notarization-info "${_requuid}" --username "${N_USERNAME}" --password "${N_PASSWORD}" >${_tmpout} 2>&1
            _status=$(cat "${_tmpout}" | grep "Status:" | awk '{ print $2 }')
            if [ "${_status}" == "invalid" ]; then
                echo "Got invalid notarization!"
                break;
            fi

            if [ "${_status}" == "success" ]; then
                echo -n "Notarization successful! Stapling..."
                xcrun stapler staple -v "${DEST_DMG}"
                break;
            fi
            echo "Notarization in progress, waiting..."
        done
    else
        cat ${_tmpout}
        echo "Error getting RequestUUID, notarization unsuccessful"
    fi
else
    echo "No notarization credentials supplied, skipping..."
fi

echo "..done. You should have ${DEST_DMG} ready to upload"
