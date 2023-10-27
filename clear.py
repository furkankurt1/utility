import os
import shutil

def delete_build_folder():
    try:
        current_directory = os.getcwd()  # Şu anki çalışma klasörünü al
        directories = [
            os.path.join(current_directory, 'android', 'app'),
            os.path.join(current_directory, 'android', 'reactUnity'),
            os.path.join(current_directory, 'unityBuild', 'unityLibrary')
        ]
        
        build_folders_to_delete = []

        for directory in directories:
            build_path = os.path.join(directory, 'build')
            if os.path.exists(build_path):
                build_folders_to_delete.append(build_path)
        
        if build_folders_to_delete:
            user_input = input(f"Toplamda {len(build_folders_to_delete)} 'build' klasörü bulundu. Hepsi silinsin mi? (Evet/Hayır): ")
            if user_input.lower() == 'evet':
                for build_path in build_folders_to_delete:
                    shutil.rmtree(build_path)
                    print(f"'{build_path}' klasörü silindi.")
            else:
                print("Klasörler silinmedi.")
        else:
            print("Silinecek 'build' klasörü bulunamadı.")

    except PermissionError:
        print("Bu klasörü silmek için izniniz yok.")
    except Exception as e:
        print(f"İşlem sırasında bir hata oluştu: {e}")

if __name__ == "__main__":
    delete_build_folder()
