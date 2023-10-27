import os
import re
import shutil
from xml.etree import ElementTree as ET

ET.register_namespace('', "http://schemas.android.com/apk/res/android")

def find_and_replace(pattern, replacement, text):
    match = re.search(pattern, text)
    if match:
        old_version = match.group(1)
        new_text = re.sub(pattern, replacement, text)
        return new_text, f"{pattern.split()[-1]} {old_version} dan {replacement.split()[-1]} a değişti."
    return text, None

def comment_out_noCompress(text):
    lines = text.split('\n')
    changed = False
    for i, line in enumerate(lines):
        if 'noCompress' in line and not line.strip().startswith('//'):
            lines[i] = f'// {line}'
            changed = True
    new_text = '\n'.join(lines)
    if changed:
        return new_text, "noCompress satırları yorum satırına çevrildi."
    return new_text, None

def copy_file(src, dest):
    destination_dir = os.path.dirname(dest)
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    shutil.copy2(src, dest)
    return f"{src} dosyası {dest} konumuna kopyalandı."

def update_android_manifest(manifest_path):
    ET.register_namespace('android', "http://schemas.android.com/apk/res/android")
    tree = ET.ElementTree()
    tree.parse(manifest_path)
    root = tree.getroot()

    application_element = root.find('./application')
    if application_element is not None:
        activity_element = application_element.find('./activity')
        if activity_element is not None:
            activity_element.set('android:clearTaskOnLaunch', 'false')
            print("Activity içerisine android:clearTaskOnLaunch='false', eklendi.")
            activity_element.set('android:finishOnTaskLaunch', 'false')
            print("Activity içerisine android:finishOnTaskLaunch='false', eklendi.")
            activity_element.set('android:process', ':unity')
            print("android:process', ':unity', has been added to Activity section.")

            # android:launchMode özelliğini kontrol et ve güncelle
          #  if 'android:launchMode' in activity_element.attrib:
            #    if activity_element.attrib['android:launchMode'] == 'singleTask':
            #        activity_element.set('android:launchMode', 'standard')
             #       print("android:launchMode 'singleTask' has been replaced by 'standard'.")
        #    else:
           #     activity_element.set('android:launchMode', 'standard')
           #     print("android:launchMode 'standard' has been set.")
            
            # Intent filtrelerini sil
            for intent_filter in activity_element.findall('./intent-filter'):
                activity_element.remove(intent_filter)
                print("'Intent filters' have been removed.")

    tree.write(manifest_path, encoding="utf-8", xml_declaration=True)

def update_build_gradle(gradle_path):
    try:
        with open(gradle_path, 'r') as file:
            content = file.readlines()
        start_line = -1
        end_line = -1
        for i, line in enumerate(content):
            if 'dependencies {' in line:
                start_line = i
            if start_line != -1 and '}' in line:
                end_line = i
                break
        if start_line != -1 and end_line != -1:
            new_block = [
                "    implementation fileTree(dir: 'libs', include: ['*.jar'])\n",
                "    implementation files('libs/arcore_client.aar')\n",
                "    implementation files('libs/UnityARCore.aar')\n",
                "    implementation files('libs/ARPresto.aar')\n",
                "    implementation files('libs/unityandroidpermissions.aar')\n",
                "    implementation files('libs/xrmanifest.androidlib')\n"
            ]
            content[start_line + 1:end_line] = new_block
            with open(gradle_path, 'w') as file:
                file.writelines(content)
            return "build.gradle dosyası başarıyla güncellendi."
        else:
            return "build.gradle dosyasında dependencies bloğu bulunamadı."
    except Exception as e:
        return f"build.gradle dosyasını güncellerken bir hata oluştu: {str(e)}"

def main():
    current_directory = os.getcwd()
    source_path = os.path.join(current_directory, 'launcher', 'src', 'main', 'res', 'values', 'strings.xml')
    destination_path = os.path.join(current_directory, 'unityLibrary', 'src', 'main', 'res', 'values', 'strings.xml')
    if os.path.exists(source_path):
        print(copy_file(source_path, destination_path))
    else:
        print(f"Kaynak dosya ({source_path}) bulunamadı.")
    gradle_file_path = os.path.join(current_directory, 'unityLibrary', 'build.gradle')
    if os.path.exists(gradle_file_path):
        print(update_build_gradle(gradle_file_path))
        with open(gradle_file_path, 'r') as file:
            file_contents = file.read()
        file_contents, change_log = find_and_replace(r'compileSdkVersion (\d+)', 'compileSdkVersion 33', file_contents)
        if change_log:
            print(change_log)
        file_contents, change_log = find_and_replace(r'minSdkVersion (\d+)', 'minSdkVersion 24', file_contents)
        if change_log:
            print(change_log)
        file_contents, change_log = find_and_replace(r'targetSdkVersion (\d+)', 'targetSdkVersion 33', file_contents)
        if change_log:
            print(change_log)
        file_contents, comment_log = comment_out_noCompress(file_contents)
        if comment_log:
            print(comment_log)
        with open(gradle_file_path, 'w') as file:
            file.write(file_contents)
    else:
        print(f"build.gradle dosya yolu ({gradle_file_path}) bulunamadı.")

    manifest_path = os.path.join(current_directory, 'unityLibrary', 'src', 'main', 'AndroidManifest.xml')
    if os.path.exists(manifest_path):
        print(update_android_manifest(manifest_path))
    else:
        print(f"AndroidManifest.xml dosya yolu ({manifest_path}) bulunamadı.")

if __name__ == "__main__":
    main()
