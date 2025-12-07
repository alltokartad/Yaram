# Yaram Browser

A modern web browser application built with Python and PyQt5.

## Features

- **Navigation Controls**
  - ← Back: Go to previous page
  - Forward →: Go to next page
  - 🔄 Refresh: Reload current page
  
- **Search & URL Input**
  - Search label for clarity
  - Unified search/URL input field
  - Support for URLs, domains, and search queries
  - Google search integration for queries

- **Downloads**
  - Download manager
  - File save dialog
  - Progress tracking
  - Download history

- **Version Management**
  - Current version: 1.0.0
  - Easy version updates in code

## Requirements

- Python 3.7+
- PyQt5
- PyQtWebEngine

## Installation

### Windows
```bash
pip install -r requirements.txt
run.bat
```

### Linux/Mac
```bash
pip install -r requirements.txt
chmod +x run.sh
./run.sh
```

### Manual Run
```bash
python yaram_browser.py
```

## Usage

1. **Navigate**: Type a URL or search query in the search box and press Enter or click Search
2. **Back/Forward**: Use the navigation buttons to move through history
3. **Refresh**: Click the refresh button to reload the page
4. **Download**: Right-click links and save, or use the download manager
5. **View Downloads**: Click the Downloads button to see download history

## Keyboard Shortcuts

- **Enter** in search box: Navigate to URL/search
- **Alt+Left Arrow** (system): Go back
- **Alt+Right Arrow** (system): Go forward

## Features Explained

### Back/Forward Navigation
- Maintains full browsing history
- Back button goes to previous page
- Forward button becomes available after going back
- Buttons are automatically disabled when unavailable

### Search & URL Handling
- Smart URL detection (adds https:// for domains)
- Automatic Google search for queries
- Label clearly shows "Search:" for user guidance

### Download Manager
- Shows download history
- Progress bar during downloads
- File save dialog for each download
- Success/error notifications

### Version Display
- Shows current version (v1.0.0)
- Easy to update in the code

## Troubleshooting

**Dependencies won't install:**
- Make sure Python 3.7+ is installed
- Try: `pip install --upgrade pip`
- Then retry: `pip install -r requirements.txt`

**Browser crashes on startup:**
- Make sure PyQtWebEngine is properly installed
- Try: `pip install --force-reinstall PyQtWebEngine`

**Cannot download files:**
- Check write permissions in your download folder
- Try selecting a different save location

## License

Yaram Browser v1.0.0
