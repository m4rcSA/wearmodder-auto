import subprocess, os, sys, shutil
# xml.etree is imported but not used
# from xml.etree import ElementTree
from pathlib import Path

# --- Argument Handling (same as before) ---
if len(sys.argv)<2:
    print('Run this script passing the path to the app\'s APK file as the argument.') # Corrected help message
    exit()
apk_path=sys.argv[1]
if not os.path.isfile(apk_path):
    # Corrected error message slightly for clarity
    print(f'Error: Path "{apk_path}" is not a valid file or does not exist.')
    exit()
apk_name=Path(apk_path).stem
tmp_path=f'./tmp_{apk_name}' # Use Path object for consistency? tmp_path = Path(f'./tmp_{apk_name}')

# --- Cleanup Temp Directory (same as before) ---
# Convert tmp_path to Path object if not already done
tmp_path_p = Path(tmp_path)
if tmp_path_p.exists():
    print(f"Removing existing temporary directory: {tmp_path_p}")
    shutil.rmtree(tmp_path_p) # Use Path object with shutil

# --- Decompile APK (same as before) ---
print(f"Decompiling {apk_path} to {tmp_path_p}...")
subprocess.run(['java', '-jar', './resources/apktool.jar', 'd', apk_path, '--no-src', '-o', str(tmp_path_p)], check=True) # Added check=True, use str(tmp_path_p)

# --- <<< NEW: Remove unwanted lib directories >>> ---
lib_dir = tmp_path_p / 'lib'
keep_lib = 'armeabi-v7a' # The architecture to keep

if lib_dir.is_dir(): # Check if lib directory exists
    print(f"Checking libraries in {lib_dir}...")
    found_libs = False
    for item in lib_dir.iterdir():
        if item.is_dir(): # Ensure it's a directory (like armeabi-v7a, x86, etc.)
            found_libs = True
            if item.name != keep_lib:
                print(f"Removing unwanted library architecture: {item.name}")
                shutil.rmtree(item)
            else:
                print(f"Keeping library architecture: {item.name}")
    if not found_libs:
        print("No subdirectories found in lib directory.")
else:
    print("No 'lib' directory found in the decompiled structure.")
# --- <<< End of NEW section >>> ---

# --- Run WearModder (same as before) ---
# Ensure resource paths are strings if needed by subprocess
wearmodder_script = Path('./resources/wearmodder.py')
res_folder = tmp_path_p / 'res'
print(f"Running modification script {wearmodder_script} on {res_folder}...")
# Check if wearmodder script exists before running?
if wearmodder_script.is_file() and res_folder.is_dir():
     subprocess.run([sys.executable, str(wearmodder_script), str(res_folder)], check=True) # Use sys.executable for python path, added check=True
else:
    print(f"Warning: {wearmodder_script} or {res_folder} not found. Skipping modification script.")


# --- Rebuild APK (same as before) ---
output_apk_name = f'{apk_name}-w.apk'
print(f"Rebuilding APK from {tmp_path_p} to {output_apk_name}...")
subprocess.run(['java', '-jar', './resources/apktool.jar', 'b', str(tmp_path_p), '-o', output_apk_name], check=True) # Added check=True

# --- Sign APK (same as before) ---
# Ensure resource paths are strings
signer_jar = Path('./resources/uber-apk-signer.jar')
print(f"Signing {output_apk_name}...")
if signer_jar.is_file():
    subprocess.run(['java', '-jar', str(signer_jar), '-a', output_apk_name, '--overwrite'], check=True) # Added check=True
else:
    print(f"Warning: Signer JAR {signer_jar} not found. Skipping signing.")


# --- Final Cleanup (same as before) ---
print(f"Removing temporary directory: {tmp_path_p}")
shutil.rmtree(tmp_path_p)

print(f"Process finished. Modified APK: {output_apk_name}")
