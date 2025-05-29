import os
import shutil
from datetime import datetime
import argparse
from pathlib import Path
from tqdm import tqdm
import logging
from PIL import Image
import piexif
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# File type configurations
SUPPORTED_FORMATS = {
    'videos': ('.mov', '.mp4', '.avi', '.mkv', '.wmv'),
    'photos': ('.jpg', '.jpeg', '.png', '.arw', '.dng', '.heic', '.raw'),
    'others': ()  # Will catch all other files
}

def get_creation_date(file_path):
    """Extract creation date from file metadata."""
    try:
        # Try to get date from EXIF for images
        if any(file_path.lower().endswith(ext) for ext in SUPPORTED_FORMATS['photos']):
            try:
                img = Image.open(file_path)
                if 'exif' in img.info:
                    exif_dict = piexif.load(img.info['exif'])
                    if piexif.ExifIFD.DateTimeOriginal in exif_dict['Exif']:
                        date_str = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal].decode('utf-8')
                        return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
            except Exception as e:
                logging.warning(f"Could not read EXIF data from {file_path}: {e}")

        # Try to get date from video metadata
        if any(file_path.lower().endswith(ext) for ext in SUPPORTED_FORMATS['videos']):
            try:
                parser = createParser(file_path)
                if parser:
                    metadata = extractMetadata(parser)
                    if metadata and metadata.has('creation_date'):
                        return metadata.get('creation_date')
            except Exception as e:
                logging.warning(f"Could not read video metadata from {file_path}: {e}")

        # Fallback to file modification time
        return datetime.fromtimestamp(os.path.getmtime(file_path))
    except Exception as e:
        logging.error(f"Error getting creation date for {file_path}: {e}")
        return datetime.fromtimestamp(os.path.getmtime(file_path))

def get_destination_path(file_path, base_dir, creation_date, organize_by='date'):
    """Determine the destination path for a file."""
    file_name = os.path.basename(file_path)
    file_ext = os.path.splitext(file_name)[1].lower()

    # Determine file type category
    category = next(
        (cat for cat, exts in SUPPORTED_FORMATS.items() if file_ext in exts),
        'others'
    )

    # Create date-based directory structure
    if organize_by == 'date':
        date_path = creation_date.strftime('%Y-%m-%d')
    elif organize_by == 'year_month':
        date_path = creation_date.strftime('%Y/%m')
    else:  # year_month_day
        date_path = creation_date.strftime('%Y/%m/%d')

    return Path(base_dir) / date_path / category / file_name

def handle_duplicate(dest_path, counter=1):
    """Handle duplicate filenames by adding a counter."""
    while dest_path.exists():
        base_name = dest_path.stem
        # Remove existing counter if present
        if ' (' in base_name:
            base_name = base_name.rsplit(' (', 1)[0]
        new_name = f"{base_name} ({counter}){dest_path.suffix}"
        dest_path = dest_path.parent / new_name
        counter += 1
    return dest_path

def organize_media(directory, organize_by='date', copy=False, dry_run=False):
    """Main function to organize media files."""
    directory = Path(directory)
    if not directory.exists():
        raise ValueError(f"Directory not found: {directory}")

    # Get list of all files
    files = list(directory.rglob('*'))
    files = [f for f in files if f.is_file()]

    # Process files with progress bar
    with tqdm(total=len(files), desc="Processing files") as pbar:
        stats = {'moved': 0, 'skipped': 0, 'errors': 0}
        
        for file_path in files:
            try:
                # Skip hidden files
                if file_path.name.startswith('.'):
                    stats['skipped'] += 1
                    continue

                # Get creation date and destination path
                creation_date = get_creation_date(str(file_path))
                dest_path = get_destination_path(str(file_path), directory, creation_date, organize_by)

                # Handle duplicates
                if dest_path.exists():
                    dest_path = handle_duplicate(dest_path)

                # Create destination directory
                dest_path.parent.mkdir(parents=True, exist_ok=True)

                if not dry_run:
                    if copy:
                        shutil.copy2(file_path, dest_path)
                    else:
                        shutil.move(file_path, dest_path)
                    stats['moved'] += 1
                    logging.info(f"{'Copied' if copy else 'Moved'} '{file_path}' to '{dest_path}'")
                else:
                    logging.info(f"Would {'copy' if copy else 'move'} '{file_path}' to '{dest_path}'")

            except Exception as e:
                logging.error(f"Error processing {file_path}: {e}")
                stats['errors'] += 1

            pbar.update(1)

    return stats

def main():
    parser = argparse.ArgumentParser(description='Organize media files by date and type.')
    parser.add_argument('directory', help='Directory to organize')
    parser.add_argument('--organize-by', choices=['date', 'year_month', 'year_month_day'],
                        default='date', help='Organization structure')
    parser.add_argument('--copy', action='store_true', help='Copy instead of move files')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    
    args = parser.parse_args()

    try:
        stats = organize_media(args.directory, args.organize_by, args.copy, args.dry_run)
        print("\nOperation completed:")
        print(f"Files processed: {stats['moved']}")
        print(f"Files skipped: {stats['skipped']}")
        print(f"Errors encountered: {stats['errors']}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return 1

    return 0

if __name__ == '__main__':
    exit(main())
