import time
from curses import wrapper
import os
import shutil
import subprocess
import sys



# 🟣 PREDICATE FUNCTIONS ❓️
def is_corrupt(input: str, stdscr) -> bool:
    """ Check if a provided image is corrupt or not.

    Args:
        input: A path leading to an image file.
        stdscr: An object for managing the console output.


    Returns:
        True, if an image is corrupted.

    """

    # 📦 VARIABLES
    safe_input: str = add_quotation(input)
    command: str = "magick identify -regard-warnings " + safe_input

    # ⚙️ LOGIC
    check_path(input, stdscr)

    if subprocess.run(command, capture_output=True, check=True).returncode == 1:
        return True
    else:
        return False


def is_supported_by_jpegxl(input: str) -> bool:
    """ Check if a file contains a file extension that is supported by the official JPEG XL encoder.

    Args:
        input: A path leading to a file.

    Returns:
        True, if the file extension is supported.

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
def check_path(path: str, stdscr) -> None:
    """ Check if a path exists.

    Args:
        path: A path to check.
        stdscr: An object for managing the console output.

    Returns:
        Stops the program, if the path does not exit.

    """

    # 📦 VARIABLES
    path_exists: bool = os.path.exists(path)

    # ⚙️ LOGIC
    if path_exists is False:
        stdscr.addstr(7, 0, "🫵👁️👄👁️💢 This path doesn't exit: " + path + get_many_spaces(10))
        stdscr.refresh()
        # TODO throw an exception
        sys.exit(1)


def readable_bytes(num_of_bytes: int) -> str:
    """ Converts a number of bytes into a human-readable string.

    Args:
        num_of_bytes: The number of bytes

    Returns:
        A readable string representing the number of bytes.

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
    """ Add quotation marks at the beginning and the end of a text.

    Args:
        text: A string to add quotation marks.

    Returns:
        A string with quotation marks.

    """

    # ⚙️ LOGIC
    return "\"" + text + "\""


def transfer_metadata(input: str, output: str) -> None:
    """ Transfer every image metadata from input to output.

    Args:
        input: A path leading to a metadata-extractable file.
        output: A path leading to a file that can receive metadata.

    Returns:
        None.

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


def add_exif_title(input: str) -> None:
    """ Add title tag in image EXIF metadata, based on the current file name.

    Args:
        input: A path leading to an image.

    Returns:
        None.

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
    """ Restore proper file extension naming.

    Args:
        input: A path leading to an image.

    Returns:
        A path to the newly renamed file.

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


def delete_file(file: str, stdscr) -> None:
    """ Delete a file.

    Args:
        file: A path to a file to delete.
        stdscr: An object for managing the console output.

    Returns:
        None.

    """

    # ⚙️ LOGIC
    try:
        os.remove(file)
    except OSError as error:
        stdscr.addstr(7, 0, "🫵👁️👄👁️💢 This file could not be deleted: " + file + get_many_spaces(10))
        stdscr.refresh()


def find_specific_types(files: list[str], extensions: list[str]) -> list[str]:
    """ Get a list of file paths that only include files with specific extensions.

    Args:
        files: A list of file paths.
        extensions: A list of extensions, without the separation dot.

    Returns:
        Filtered list of paths with desired extensions.

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


def prioritize_list(files: list[str], stdscr) -> list[str]:
    """ Prioritizes images that can be converted faster to be converted first.

    Args:
        files: A list of paths leading to images.
        stdscr: An object for managing the console output.

    Returns:
        A prioritized list of image paths.

    """

    # 📦 VARIABLES
    prioritized_list: list[str] = []  # The returned end result. Structured like this: Small JPEGs -> Big JPEGs -> Small Images -> Big Images
    small_jpegs: list[str] = []  # A list of JPEGs that are considered small
    big_jpegs: list[str] = []  # A list of JPEGs that are not considered small
    small_images: list[str] = []  # A list of images that are considered small
    big_images: list[str] = []  # A list of images that are not considered small
    current_type: str = ""  # Current file extension
    current_size: int = 0  # Current file size in byte
    comparison_size: int = 1000000  # The number represents 1 MB in byte unit
    is_small: bool = False  # A predicate to determine a small image
    is_big: bool = False  # A predicate to determine a not small image
    is_jpeg: bool = False  # A predicate to determine a JPEG image
    is_image: bool = False  # A predicate to determine a not JPEG image

    # ⚙️ LOGIC
    for file in files:
        # Update variables
        current_size = get_size(file, stdscr)
        current_type = os.path.splitext(file)[1][1:]  # First bracket to extract ".type", second bracket to remove "."
        is_small = current_size <= comparison_size
        is_big = not is_small
        is_jpeg = current_type.upper() == "JPEG" or current_type.upper() == "JPG"
        is_image = not is_jpeg

        # Sort current file

        # Case: Small JPEG
        if is_jpeg and is_small:
            small_jpegs.append(file)
            continue

        # Case: Big JPEG
        if is_jpeg and is_big:
            big_jpegs.append(file)
            continue

        # Case: Small image
        if is_image and is_small:
            small_images.append(file)
            continue

        # Case: Big image
        if is_image and is_big:
            big_images.append(file)
            continue

        # Case: Fallback
        big_images.append(file)

    prioritized_list = small_jpegs + big_jpegs + small_images + big_images

    return prioritized_list


# 🟣 GETTER FUNCTIONS 📦
def get_path(arguments: list[str], stdscr) -> str:
    """ Get a path from the first command line argument.

    Args:
        arguments: The command line arguments.
        stdscr: An object for managing the console output.


    Returns:
        A path.

    """

    # ⚙️ LOGIC
    # No extra argument are given
    if len(arguments) < 2:
        # TODO
        stdscr.addstr(7, 0, "🫵👁️👄👁️💢 Command line argument is missing." + get_many_spaces(10))
        stdscr.addstr(8, 0, "🫵👁️👄👁️💢 Please add an argument containing a path to your media directory." + get_many_spaces(10))
        stdscr.refresh()
        sys.exit(1)
    else:
        # Validate argument
        check_path(arguments[1], stdscr)
        return os.path.normpath(arguments[1])


def get_size(path: str, stdscr) -> int:
    """ Get the byte size of a file.

    Args:
        path: A path to a file.
        stdscr: An object for managing the console output.

    Returns:
        Byte size of a file.

    """

    # ⚙️ LOGIC
    check_path(path, stdscr) # Handle problematic cases
    return os.path.getsize(path)


def find_files(path: str, stdscr) -> list[str]:
    """ Get a list of file paths recursively, based from a directory.

    Args:
        path: A path to a directory.
        stdscr: An object for managing the console output.

    Returns:
        A string list of paths.

    """

    # 📦 VARIABLES
    result: list[str] = []

    # ⚙️ LOGIC
    check_path(path, stdscr) # Handle problematic cases
    # Scan path for files
    for root, dirs, files in os.walk(path):
        for file in files:
            # Build path
            current_file_path: str = os.path.join(root, file)
            # Add path to result
            result.append(current_file_path)
    return result


def get_many_spaces(number_of_spaces: int) -> str:
    """ Get a string with a specific amount of characters.

    Args:
        number_of_spaces: The number of spaces to be generated.

    Returns:
        A string with 'number_of_spaces' space characters

    """

    # ⚙️ LOGIC
    return " " * 100


# 🟣 CONVERTER FUNCTIONS 🔄️
def convert_to_jpegxl(input: str, stdscr) -> str:
    """ Converts the input as JPEG XL file.

    Args:
        input: A path to an image to be converted.
        stdscr: An object for managing the console output.

    Returns:
        An output path for the converted file.

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
        add_exif_title(output)
        # Delete old input
        delete_file(input, stdscr)

    return output


def convert_to_png(input: str, stdscr) -> str:
    """ Converts the input as PNG file.

    Args:
        input: A path to an image to be converted.
        stdscr: An object for managing the console output.

    Returns:
        An output path for the converted file.

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
        delete_file(input, stdscr)

    return output


def recover_image(input: str, stdscr) -> str:
    """ Try to recover a corrupt image.

    Args:
        input: A path to an image to be recovered.
        stdscr: An object for managing the console output.

    Returns:
        Output path to the recovered image.

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
        delete_file(input, stdscr)

    return output


def convert_images(files: list[str], stdscr) -> None:
    """ Converts images as JPEG XL with previous EXIF metadata.

    Args:
        files: A list of paths leading to images.
        stdscr: An object for managing the console output.

    Returns:
        None.

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
        temporary_path = os.path.normpath(os.path.join(os.path.splitdrive(file)[0], "/JPEG XL Converter"))
        os.makedirs(temporary_path, exist_ok=True)
        current_file = os.path.join(temporary_path, os.path.basename(file))

        # Move file to temporary path to avoid errors based on problematic directory names.
        shutil.move(file, current_file)

        # Get current file size
        old_size = get_size(current_file, stdscr)

        # Inform user
        stdscr.addstr(4, 0, "") # Reset current line
        stdscr.addstr(4, 0, "📢 Current file: " + file)
        stdscr.refresh()

        # Handle corrupted files
        if is_corrupt(current_file, stdscr):
            stdscr.addstr(7, 0, "This file is corrupted: " + current_file + get_many_spaces(10))
            stdscr.addstr(8, 0, "Try to recover image." + get_many_spaces(10))
            stdscr.refresh()
            try:
                # Update current_file
                current_file = recover_image(current_file, stdscr)
                stdscr.addstr(9, 0, "Recovery successful." + get_many_spaces(10))
                stdscr.refresh()
            except Exception:
                stdscr.addstr(9, 0, "🫵👁️👄👁️💢 Recovery failed. File will be skipped." + get_many_spaces(10))
                stdscr.refresh()
                continue

        # Restore actual file extension (even after recovery) and update current_image
        current_file = restore_filetype(current_file)

        # Check if current filetype is supported by JPEG XL encoder. If not, then convert to PNG
        if is_supported_by_jpegxl(current_file) is False:
            # Update current file
            current_file = convert_to_png(current_file, stdscr)

        # Convert file to JPEG XL now and update current file
        current_file = convert_to_jpegxl(current_file, stdscr)

        # Get current file size and compare
        new_size = get_size(current_file, stdscr)
        current_space_gains += old_size - new_size

        if current_space_gains >= 0:
            indicator = "📉 (Size is smaller than before.)"
        else:
            indicator = "📈 (Size is bigger than before.)"

        stdscr.addstr(5, 0, "") # Reset current line
        stdscr.addstr(5, 0, "📢 Current space savings in total: " + readable_bytes(current_space_gains) + " " + indicator)
        stdscr.addstr(6, 0, "✔️ Convert image " + str(current_progress) + "/" + str(len(files)) + " 🐸 " + get_many_spaces(10))
        stdscr.refresh()

        # Revert file relocating
        shutil.move(current_file, os.path.join(original_path, os.path.basename(current_file)))

        # Update current progress
        current_progress += 1


# 🟣 MAIN
def main(stdscr) -> None:
    """ A function to start the script.

    Args:
        stdscr: An object for managing the console output.

    Returns:
        None.

    """

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
    # Clear console text
    stdscr.clear()
    # Get the path from the second position of command line arguments
    argument_path = get_path(sys.argv, stdscr)
    # Scan every file path from the given path
    files = find_files(argument_path, stdscr)
    # Find supported image files
    image_files = find_specific_types(files, image_extensions)
    # Prioritize images for faster conversion at the beginning
    image_files = prioritize_list(image_files, stdscr)
    # Get the byte size of directory before the conversion
    for file in files:
        temp += get_size(file, stdscr)
        size_before = readable_bytes(temp)
    # Let the user know the current status
    stdscr.addstr(0, 0, "📢 Given path: " + argument_path + get_many_spaces(10))
    stdscr.addstr(1, 0, "Total files: " + str(len(files)) + get_many_spaces(10))
    stdscr.addstr(2, 0, "Supported image files: " + str(len(image_files)) + get_many_spaces(10))
    stdscr.addstr(3, 0, "Directory size: " + size_before + get_many_spaces(10))
    stdscr.refresh()

    # Convert the images now
    convert_images(image_files, stdscr)

    # Get size after conversion
    files = find_files(argument_path, stdscr)
    temp = 0
    for file in files:
        temp += get_size(file, stdscr)
        size_after = readable_bytes(temp)

    # End status report
    stdscr.addstr(7, 0, "📢 Size information:" + get_many_spaces(10))
    stdscr.addstr(8, 0, "Before and after size of the directory: " + size_before + " / " + size_after + get_many_spaces(10))
    stdscr.addstr(9, 0, "✔️✔️✔️ Script done! 🦭🐳" + get_many_spaces(10))
    stdscr.refresh()
    time.sleep(5)


# 🐸 Start the script 🦭
wrapper(main)

# TODO find out what type of object 'stdscr' is