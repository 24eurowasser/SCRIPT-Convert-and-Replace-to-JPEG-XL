import os
import sys

def path_check(path: str) -> None:
    """
    Check if a path exists.
    :param path: A path to check.
    :return: Stops the program if path doesn't exit.
    """
    path_exists: bool = os.path.exists(path)
    path_is_directory: bool = os.path.isdir(path)

    if path_exists and path_is_directory is False:
        print("🫵👁️👄👁️💢 That path doesn't exit: " + path)
        sys.exit(1)

def get_path(arguments: list[str]) -> str:
    """
    Get the path from the first argument, if possible.
    :param arguments: Should be the command line arguments.
    :return: A path.
    """

    # No argument given
    if len(arguments) < 2:
        print("🫵👁️👄👁️💢 Command line argument is missing.")
        print("🫵👁️👄👁️💢 Please add an argument containing a path to your media directory.")
        sys.exit(1)
    else:
        # Error handling
        path_check(arguments[1])
        return os.path.normpath(arguments[1])

def scan_for_files(path: str) -> list[str]:
    """
    Scans a directory recursively and creates a list of paths that include name and root
    :param path: A path to a directory.
    :return: A string list of paths.
    """

    # Handle problematic cases
    path_check(path)

    # Prepare result variable
    result: list[str] = []

    # Scan path for files
    for root, dirs, files in os.walk(path):
        for file in files:
            # Build path
            current_file_path: str = os.path.join(root, file)
            # Add path to result
            result.append(current_file_path)

    return result

def get_size(path: str) -> int:
    """
    Get the size of a directory.
    :param path: A path to a directory.
    :return: Size in byte.
    """

    # Handle problematic cases
    path_check(path)

    files: list[str] = scan_for_files(path)
    result: int = 0

    for file in files:
        current_size: int = os.path.getsize(file)
        result = result + current_size

    return result

def find_files_with_extension(files: list[str], extensions: list[str]) -> list[str]:
    """
    Get a list of file paths that only include files with specific extensions.
    :param files: A list of paths containing root and file extensions.
    :param extensions: A list of extensions, without separation dot.
    :return: Filtered list of paths with desired extensions.
    """
    result: list[str] = []

    for required_extension in extensions:
        for file in files:
            current_file_extension = os.path.splitext(file)[1].replace(".", "")

            if required_extension == current_file_extension:
                result.append(file)

            continue

    return result

def quote_string(text: str) -> str:
    """
    Add quotation marks at the beginning and the end.
    :param text: A string to add quotation marks.
    :return: A string with quotation marks
    """
    result: str = "\"" + text + "\""
    return result

def convert_image(input: str) -> None:
    """
    Convert an image as JPEG XL and preserve exif metadata.
    :param input: Input path to original image.
    :return: None
    """
    # Variables
    extension_jxl:    str = ".jxl"
    output:           str = input + extension_jxl
    exif_backup_path: str # 🦆 To be filled

    # Export metadata, because it would get lost during conversion
    exif_backup_path = export_meta(input)
    # Convert image to jpegxl
    convert_to_jpegxl(input, output)
    # Import metadata
    import_meta(output, exif_backup_path)
    # Set the exif title to current file name
    add_title(input)
    # Delete metadata extraction file
    delete(exif_backup_path)

def export_meta(input: str) -> str:
    """
    Export possible EXIF information from the input.
    :param input: A path leading to an exif-extractable file.
    :return: Path to the exported exif file.
    """
    # Variables
    command:                 str # 🦆 To be filled
    safe_input:              str # 🦆 To be filled
    safe_output:             str # 🦆 To be filled
    output_extension:        str = ".xmp"
    output:                  str = input + output_extension

    # Make paths safe to use for console use (spaces in paths can create problems)
    safe_input  = quote_string(input)
    safe_output = quote_string(output)
    # Create console command
    command = "exiftool -o " + safe_output + " -tagsfromfile " + safe_input

    os.system(command)

    return output

def import_meta(image: str, metadata: str) -> None:
    """
    Imports EXIF tags to an image.
    :param image: A path leading to an image.
    :param metadata: A path leading to metadata.
    :return: None
    """
    # Variables
    command:       str # 🦆 To be filled
    safe_image:    str = quote_string(image)
    safe_metadata: str = quote_string(metadata)

    command = "exiftool -overwrite_original -m -tagsfromfile " + safe_metadata + " " + safe_image

    os.system(command)

def add_title(input: str) -> None:
    """
    Add title tag in image exif metadata, based on the current file name.
    :param input: A path leading to an image.
    :return: None
    """
    # Variables
    safe_input: str = quote_string(input)
    title:      str = os.path.basename(os.path.splitext(input)[0])
    command:    str = "exiftool -overwrite_original -m -Title=" + title + " " + safe_input

    os.system(command)

def convert_to_jpegxl(input: str, output: str) -> None:
    """
    Converts the input as JPEG XL file format to the output path.
    :param input: A path to an image to be converted.
    :param output: An output path for the converted file.
    :return: None
    """
    # Variables
    # Make paths safe to use for console use (spaces in paths can create problems)
    safe_input:  str = quote_string(input)
    safe_output: str = quote_string(output)
    settings:    str = "--distance 0 --effort 10 --lossless_jpeg 1 --allow_jpeg_reconstruction 0"
    command:     str = "cjxl " + safe_input + " " + safe_output + " " + settings

    os.system(command)

def delete(file: str):
    """
    Try to delete a file.
    :param file: A path to a file to delete.
    :return: None
    """
    try:
        os.remove(file)
    except OSError as error:
        print("This file couldn't be deleted: " + file)

def main() -> None:
    # Variables
    argument_path:             str       # 🦆 To be filled

    size_before:               int       # 🦆 To be filled
    size_after:                int       # 🦆 To be filled
    number_of_files:           int       # 🦆 To be filled
    number_of_image_files:     int       # 🦆 To be filled
    current_progress:          int = 1

    files:                     list[str] # 🦆 To be filled
    image_files:               list[str] # 🦆 To be filled
    supported_file_extensions: list[str] = ["exr", "gif", "jpg", "jpeg", "pam", "pgm", "ppm", "pfm", "pgx", "png", "apng", "jxl"]

    # Get the path from the second position of command line arguments
    argument_path = get_path(sys.argv)
    # Get the byte size of the given path
    size_before = get_size(argument_path)
    # Scan every file path from the given path
    files = scan_for_files(argument_path)
    # Get the number of files in the given path
    number_of_files = len(files)
    # Find supported image files
    image_files = find_files_with_extension(files, supported_file_extensions)
    # Get the number of image files in the given path
    number_of_image_files = len(image_files)
    # Let the user know the current status
    print("💡 Given path: " + argument_path)
    print("💡 Path contains this number of total files: " + str(number_of_files))
    print("💡 Path contains this number of image files: " + str(number_of_image_files))
    print("💡 The total byte size of the given path is " + str(size_before) + " bytes.")

    # Convert the images now
    for file in image_files:
        print("💡 Convert image " + str(current_progress) + "/" + str(number_of_image_files))
        convert_image(file)
        # Delete old image after conversion, only if JPEG XL file exist
        if os.path.exists(file + ".jxl"):
            delete(file)
        print("✔️ Conversion done.")
        # Update progress
        current_progress = current_progress + 1

    # Get size after conversion
    size_after = get_size(argument_path)
    # End status report
    print("💡 Given path: " + argument_path)
    print("💡 Byte size after operation: " + str(size_after))
    print("💡 Before / After: " + str(size_before) + " / " + str(size_after))
    print("✔️ Script done.")

# 🐸 Start the script 🦭
main()