import os
import shutil
import subprocess
import sys


# 🟣 PREDICATE FUNCTIONS ❓️
def is_corrupt(input: str) -> bool:
    """
    Check if a provided image is corrupt or okay.
    :param input: A path leading to an image file.
    :return: Returns True if an image file is corrupted.
    """

    # 📦 VARIABLES
    safe_input: str = add_quotation(input)
    command: str = "magick identify -regard-warnings " + safe_input

    # ⚙️ LOGIC
    check_path(input)

    if subprocess.run(command, capture_output=True, check=True).returncode == 1:
        return True
    else:
        return False


def is_supported_by_jpegxl(input: str) -> bool:
    """
    Check if a file contains a file extension that is supported by the official JPEG XL encoder.
    :param input: A path leading to a file.
    :return: True, if the file extension is supported.
    """

    # 📦 VARIABLES
    input_type: str = os.path.splitext(input)[1][1:] # First bracket to extract ".type", second bracket to remove "."
    supported_types: list[str] = ["exr", "gif", "jpg", "jpeg", "pam", "pgm", "ppm", "pfm", "pgx", "png", "apng", "jxl"]

    # ⚙️ LOGIC
    for type in supported_types:
        if input_type.upper() == type.upper():
            return True

    return False


# 🟣 HELPER FUNCTIONS ⚒️
def check_path(path: str) -> None:
    """
    Check if a path exists.
    :param path: A path to check.
    :return: Stops the program if path doesn't exit.
    """

    # 📦 VARIABLES
    path_exists: bool = os.path.exists(path)

    # ⚙️ LOGIC
    if path_exists is False:
        print("🫵👁️👄👁️💢 This path doesn't exit: " + path)
        sys.exit(1)


def readable_bytes(num_of_bytes: int) -> str:
    """
    Converts a number of bytes into a human-readable string.
    :param num_of_bytes: The number of bytes.
    :return: A readable string representing the number of bytes.
    """

    # 📦 VARIABLES
    units: list[str] = ['bytes', 'KB', 'MB', 'GB', 'TB']

    # ⚙️ LOGIC
    for unit in units:
        if abs(num_of_bytes) < 1024.0:
            # %3.1f specifies a float number with a width of 3 characters and 1 decimal place
            return "%3.1f %s" % (num_of_bytes, unit)
        num_of_bytes /= 1024.0


def add_quotation(text: str) -> str:
    """
    Add quotation marks at the beginning and the end.
    :param text: A string to add quotation marks.
    :return: A string with quotation marks
    """

    # ⚙️ LOGIC
    return "\"" + text + "\""


def transfer_metadata(input: str, output: str) -> None:
    """
    Transfer every image metadata from input to output.
    :param input: A path leading to a metadata-extractable file.
    :param output: A path leading to a file that can receive metadata.
    :return: None
    """

    # 📦 VARIABLES
    command: str = ""  # Command for console execution

    # Quote paths -> Safe for command usage
    input_quoted: str = add_quotation(input)
    output_quoted: str = add_quotation(output)

    # ⚙️ LOGIC
    # Create console command
    command = "exiftool -overwrite_original -m -TagsFromFile " + input_quoted + " \"-all:all>all:all\" " + output_quoted
    subprocess.run(command, capture_output=True, check=True)  # Capture output to keep console messages clean.


def add_title(input: str) -> None:
    """
    Add title tag in image exif metadata, based on the current file name.
    :param input: A path leading to an image.
    :return: None
    """

    # 📦 VARIABLES
    command: str = "" # Command for console execution
    title: str = "" # This string will be added in exif title tag
    input_quoted: str = add_quotation(input) # String converted to "String" -> Safe for command usage

    # ⚙️ LOGIC
    # Create console command
    title = add_quotation(os.path.basename(input))
    command = "exiftool -overwrite_original -m -Title=" + title + " " + input_quoted
    subprocess.run(command, capture_output=True, check=True) # Capture output to keep console messages clean.


def restore_filetype(input: str) -> str:
    """
    Restore proper file extension naming, using Exiftool
    :param input: A path to a directory to correct
    :return: A path to the newly renamed file
    """

    # 📦 VARIABLES
    command: str = ""  # Command for console execution
    actual_extension: str = ""
    # Quote path -> Safe for command usage
    input_quoted: str = add_quotation(input)
    new_path: str = ""

    # ⚙️ LOGIC
    # Create console command
    command: str = "magick identify -format '%m\\n' " + input_quoted
    # Run the command. Capture the output to keep the console log clean.
    # Set text to True, so that the captured output is converted from bytes to a string
    # Get the string with .stdout and remove the first and the last 2 characters (' and \n).
    actual_extension = subprocess.run(command, capture_output=True, text=True, check=True).stdout.split("\n")[0][1:]

    # Add the captured file extension to the file path
    new_path = input + "." + actual_extension

    # Rename old file
    os.rename(input, new_path)

    return new_path


def delete_file(file: str):
    """
    Try to delete a file.
    :param file: A path to a file to delete.
    :return: None
    """

    # ⚙️ LOGIC
    try:
        os.remove(file)
    except OSError as error:
        print("🫵👁️👄👁️💢 This file could not be deleted: " + file)


# 🟣 GETTER FUNCTIONS 📦
def get_path(arguments: list[str]) -> str:
    """
    Get the path from the first argument, if possible.
    :param arguments: Should be the command line arguments.
    :return: A path.
    """

    # ⚙️ LOGIC
    # No extra argument are given
    if len(arguments) < 2:
        print("🫵👁️👄👁️💢 Command line argument is missing.")
        print("🫵👁️👄👁️💢 Please add an argument containing a path to your media directory.")
        sys.exit(1)
    else:
        # Validate argument
        check_path(arguments[1])
        return os.path.normpath(arguments[1])


def get_size(path: str) -> int:
    """
    Get the size of a directory.
    :param path: A path to a file.
    :return: Size in byte.
    """

    # ⚙️ LOGIC
    check_path(path) # Handle problematic cases
    return os.path.getsize(path)


def find_files(path: str) -> list[str]:
    """
    Scans a directory recursively and creates a list of paths that include name and root
    :param path: A path to a directory.
    :return: A string list of paths.
    """

    # 📦 VARIABLES
    result: list[str] = []

    # ⚙️ LOGIC
    check_path(path) # Handle problematic cases
    # Scan path for files
    for root, dirs, files in os.walk(path):
        for file in files:
            # Build path
            current_file_path: str = os.path.join(root, file)
            # Add path to result
            result.append(current_file_path)
    return result


def find_specific_types(files: list[str], extensions: list[str]) -> list[str]:
    """
    Get a list of file paths that only include files with specific extensions.
    :param files: A list of paths containing root and file extensions.
    :param extensions: A list of extensions, without separation dot.
    :return: Filtered list of paths with desired extensions.
    """

    # 📦 VARIABLES
    result: list[str] = []

    # ⚙️ LOGIC
    for file in files:
        for required_extension in extensions:
            current_file_extension = os.path.splitext(file)[1].replace(".", "")
            if required_extension == current_file_extension:
                result.append(file)
                continue
            if required_extension.upper() == current_file_extension:
                result.append(file)
                continue
    return result


# 🟣 CONVERTER FUNCTIONS 🔄️
def convert_to_jpegxl(input: str) -> str:
    """
    Converts the input as JPEG XL file format to the output path.
    :param input: A path to an image to be converted.
    :return: An output path for the converted file.
    """

    # 📦 VARIABLES
    # Make paths safe to use for console use (spaces in paths can create problems)
    input_quoted: str = add_quotation(input)
    output: str = input + ".jxl"
    output_quoted: str = add_quotation(output)
    settings: str = "--distance 0 --effort 10 --lossless_jpeg 1 --allow_jpeg_reconstruction 0"
    command: str = "cjxl " + input_quoted + " " + output_quoted + " " + settings

    # ⚙️ LOGIC
    subprocess.run(command, capture_output=True, check=True) # Capture output to keep console messages clean.

    # Import metadata and delete old file, if the new JPEG XL file exist.
    if os.path.exists(output):
        # Transfer metadata
        transfer_metadata(input, output)
        # Set the exif title to current file name
        add_title(output)
        # Delete old input
        delete_file(input)

    return output


def convert_to_png(input: str) -> str:
    """
    Converts the input as PNG file format to the output path.
    :param input: A path to an image to be converted.
    :return: Output path to the converted PNG
    """
    # 📦 VARIABLES
    # Make paths safe to use for console use (spaces in paths can create problems)
    quoted_input: str = add_quotation(input)
    output: str = input + ".PNG"
    quoted_output: str = add_quotation(output)
    command: str = "magick " + quoted_input + " -auto-orient " + quoted_output

    # ⚙️ LOGIC
    subprocess.run(command, capture_output=True, check=True) # Capture output to keep console messages clean.

    # Delete old image, if the new converted image exists.
    if os.path.exists(output):
        delete_file(input)

    return output


def recover_image(input: str) -> str:
    """
    Converts the image again, based on the original filetype.
    :param input: A path to an image to be recovered.
    :return: Output path to the recovered image
    """
    # 📦 VARIABLES
    # Make paths safe to use for console use (spaces in paths can create problems)
    output: str = input + os.path.splitext(input)[1]
    quoted_input: str = add_quotation(input)
    quoted_output: str = add_quotation(output)
    command: str = "magick " + quoted_input + " -auto-orient " + quoted_output

    # ⚙️ LOGIC
    if subprocess.run(command, capture_output=True, check=True).returncode == 1:
        raise OSError

    # Delete old image, if the new recovered image exists.
    if os.path.exists(output):
        delete_file(input)

    return output


def convert_image(files: list[str]) -> None:
    """
    Convert an image as JPEG XL and preserve exif metadata.
    :param files: A list of paths leading to files.
    :return: None
    """

    # 📦 VARIABLES
    # A path to the current image file. Current image could be a reconverted inbetween image to prepare actual JXL conversion.
    current_file: str = ""
    # An indicator if we lose or gain space by converting the image. Is either 📈(gain) or 📉(lose)
    indicator: str = ""
    # Current number of image that is being handled.
    current_progress: int = 1
    # We gained or lost this much space
    current_space_gains: int = 0
    # Size of input image
    old_size: int = 0
    # Size of output image
    new_size: int = 0
    # Original directory
    original_path: str = ""
    # Temporary directory
    temporary_path: str = ""

    # ⚙️ LOGIC
    for file in files:
        # Update paths
        original_path = os.path.dirname(file)
        temporary_path = os.path.splitdrive(file)[0]
        current_file = os.path.join(temporary_path, os.path.basename(file))

        # Move file to temporary path to avoid errors based on problematic directory names.
        shutil.move(file, current_file)

        # Get current file size
        old_size = get_size(current_file)

        # Inform user
        print("📢 Current file: " + file)

        # Handle corrupted files
        if is_corrupt(current_file):
            print("This file is corrupted: " + current_file)
            print("Try to recover image.")
            try:
                # Update current_file
                current_file = recover_image(current_file)
                print("Recovery successful.")
            except Exception:
                print("🫵👁️👄👁️💢 Recovery failed. File will be skipped.")
                continue

        # Restore actual file extension (even after recovery) and update current_image
        current_file = restore_filetype(current_file)

        # Check if current filetype is supported by JPEG XL encoder. If not, then convert to PNG
        if is_supported_by_jpegxl(current_file) is False:
            # Update current file
            current_file = convert_to_png(current_file)

        # Convert file to JPEG XL now and update current file
        current_file = convert_to_jpegxl(current_file)

        # Get current file size and compare
        new_size = get_size(current_file)
        current_space_gains += old_size - new_size

        if current_space_gains >= 0:
            indicator = "📉 (Size is smaller than before.)"
        else:
            indicator = "📈 (Size is bigger than before.)"

        print("📢 Current space savings in total: " + readable_bytes(current_space_gains) + " " + indicator)
        print("✔️ Convert image " + str(current_progress) + "/" + str(len(files)) + " 🐸 ")

        # Revert file relocating
        shutil.move(current_file, os.path.join(original_path, os.path.basename(current_file)))

        # Update current progress
        current_progress += 1

# 🟣 MAIN
def main() -> None:

    # 📦 VARIABLES
    argument_path: str = "" # Path that was parsed from console
    size_before: str = "" # Size of directory before conversion
    size_after: str = "" # Size of directory after conversion
    temp: int = 0 # A temporary value to make inbetween calculations
    files: list[str] = [] # A list of files
    image_files: list[str] = [] # A list of image files
    image_extensions: list[str] = ["jpg", "jpeg", "png", "gif", "apng", "tiff", "tif", "heic", "JP2", "webp",
                                   "exr", "pam", "pgm", "ppm", "pfm", "pgx"]

    # ⚙️ LOGIC
    # Get the path from the second position of command line arguments
    argument_path = get_path(sys.argv)
    # Scan every file path from the given path
    files = find_files(argument_path)
    # Find supported image files
    image_files = find_specific_types(files, image_extensions)
    # Get the byte size of directory before the conversion
    for file in files:
        temp += get_size(file)
        size_before = readable_bytes(temp)
    # Let the user know the current status
    print("📢 Given path: " + argument_path)
    print("Total files: " + str(len(files)))
    print("Supported image files: " + str(len(image_files)))
    print("Directory size: " + size_before)

    # Convert the images now
    convert_image(image_files)

    # Get size after conversion
    files = find_files(argument_path)
    temp = 0
    for file in files:
        temp += get_size(file)
        size_after = readable_bytes(temp)

    # End status report
    print("📢 Size information:")
    print("Before and after size of the directory: " + size_before + " / " + size_after)
    print("✔️✔️✔️ Script done! 🦭🐳")


# 🐸 Start the script 🦭
main()