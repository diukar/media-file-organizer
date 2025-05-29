# Media File Organizer

A Python application to organize media files (photos and videos) by date and type. Available in both command-line and GUI versions.

## Features

- Organizes files by creation date (using metadata when available)
- Supports multiple organization structures:
  - By date (YYYY-MM-DD)
  - By year/month (YYYY/MM)
  - By year/month/day (YYYY/MM/DD)
- Handles various media formats:
  - Photos: JPG, PNG, ARW, DNG, HEIC, RAW
  - Videos: MOV, MP4, AVI, MKV, WMV
- Extracts creation dates from EXIF data (photos) and video metadata
- Handles duplicate files automatically
- Provides dry-run mode to preview changes
- Option to copy instead of move files

## Installation

1. Clone this repository:
   ```bash
   git clone [repository-url]
   cd media-file-organizer
   ```

2. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate  # On Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Command Line Version
```bash
python script_v2.py /path/to/your/media/folder [options]

Options:
  --organize-by {date,year_month,year_month_day}
  --copy                Copy instead of move files
  --dry-run            Show what would be done without making changes
```

### GUI Version
```bash
python script_gui.py
```

## Requirements
- Python 3.6 or higher
- See requirements.txt for Python package dependencies

## Examples

1. Organize files by date (YYYY-MM-DD):
   ```bash
   python script_v2.py /path/to/media
   ```

2. Organize files by year and month:
   ```bash
   python script_v2.py /path/to/media --organize-by year_month
   ```

3. Preview changes without actually moving files:
   ```bash
   python script_v2.py /path/to/media --dry-run
   ```

4. Copy files instead of moving them:
   ```bash
   python script_v2.py /path/to/media --copy
   ```

## Output Structure

The script will create the following directory structure based on the chosen organization method:

For `--organize-by date` (default):
```
media_folder/
├── 2024-03-20/
│   ├── photos/
│   │   └── IMG_1234.jpg
│   └── videos/
│       └── VID_5678.mp4
└── 2024-03-21/
    ├── photos/
    │   └── IMG_9012.jpg
    └── videos/
        └── VID_3456.mp4
```

For `--organize-by year_month`:
```
media_folder/
├── 2024/
│   └── 03/
│       ├── photos/
│       │   └── IMG_1234.jpg
│       └── videos/
│           └── VID_5678.mp4
```

## Error Handling

- The script logs all operations and errors to both console and a log file
- Duplicate files are handled by adding a counter to the filename
- Hidden files are skipped
- Invalid directories or permissions issues are reported with clear error messages

## Known GUI Issues

### Critical UI Visibility Issues

The GUI version currently has severe visibility issues that require immediate attention:

1. Complete Text Invisibility:
   - Log output text is completely invisible in the log window
   - Directory path field text is not visible at all
   - Input fields show no text when typing

2. Light Mode Issues:
   - All text input fields suffer from complete text invisibility
   - No visual feedback when typing in any field
   - Critical information like file paths and logs cannot be read

3. Dark Mode Issues:
   - Same invisibility issues persist in dark mode
   - Text remains invisible across all input fields
   - Log output cannot be verified due to text being invisible

### Status

We are actively working on these critical issues with the following improvements:
- Implementing proper text visibility for all fields
- Ensuring immediate text visibility in the log window
- Making directory path text clearly visible
- Adding proper contrast for text input feedback
- Fixing text display in both light and dark modes

Immediate fixes being developed:
- Correcting text color and contrast in all input fields
- Ensuring log text is visible and readable
- Making path field text display properly
- Adding visual feedback for text input
- Implementing proper text rendering across the entire application

Please note: Until these fixes are implemented, users may need to copy-paste text or use the command-line version for full functionality. 