import os
import shutil

# This will replace the Shared folder in test_build
# Replace qtwebsocket



source_file = "./qtwebsocket.py"
d_directory = "test_build"
destination = "test_build/qtClient.py"

os.makedirs(d_directory, exist_ok=True)


shutil.copy(source_file, destination)


print(f"Copied {source_file} to {destination}")


# copying shared

source_dir =  "./Shared"
destination_dir = "test_build/Shared"

if os.path.exists(destination_dir):
    shutil.rmtree(destination_dir)

try:
    shutil.copytree(source_dir, destination_dir)
    print(f"Directory '{source_dir}' copied to '{destination_dir}' successfully.")
except FileExistsError:
    print(f"Error: Destination directory '{destination_dir}' already exists.")
    print("Please ensure the destination directory does not exist before copying,")
    print("or handle the existing directory as needed (e.g., delete it first).")
except Exception as e:
    print(f"An error occurred: {e}")