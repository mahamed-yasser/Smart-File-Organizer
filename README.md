# 🚀 Smart File Organizer

<div align="center">

![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)
![GitHub Stars](https://img.shields.io/github/stars/mahamedwow1-afk/Smart-File-Organizer?style=for-the-badge)

**تطبيق بايثون احترافي لتنظيم الملفات تلقائياً بواجهة مستخدم عصرية**

[🚀 Demo](#-demo) • [📖 Installation](#-installation) • [⚙️ Usage](#-usage) • [🤝 Contributing](#-contributing)

</div>

---

## 🎯 Overview

Smart File Organizer هو تطبيق سطح مكتب مبني بلغة Python يستخدم واجهة المستخدم PyQt6 لتنظيم الملفات والصور والفيديوهات والمستندات في مجلدات منظمة تلقائياً بناءً على نوع الملف والتاريخ.

![App Interface](screenshot.png)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📁 **Auto-Organization** | تصنيف تلقائي للملفات حسب النوع (صور، فيديو، مستندات) |
| 🌙 **Dark Mode** | دعم الوضع الليلي الكامل للواجهة |
| ↩️ **Undo Support** | إمكانية التراجع عن آخر عملية تنظيم |
| 📊 **History Tracking** | حفظ سجل جميع العمليات السابقة |
| ⚡ **Fast Processing** | معالجة سريعة للملفات باستخدام الخيوط المتوازية |
| 🎨 **Modern UI** | واجهة مستخدم عصرية وسهلة الاستخدام |

---

## 📸 Demo

### Main Interface
![Main Interface](screenshot.png)

### Organization Result
```
📁 Downloads/
├── 📁 Images/
│   ├── 📷 photo1.jpg
│   ├── 📷 photo2.png
│   └── 🖼️ screenshot.webp
├── 📁 Videos/
│   ├── 🎬 vacation.mp4
│   └── 🎬 tutorial.avi
├── 📁 Documents/
│   ├── 📄 report.pdf
│   └── 📄 notes.docx
└── 📁 Audio/
    ├── 🎵 song.mp3
    └── 🎵 podcast.wav
```

---

## 📦 Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Quick Install

```bash
# Clone the repository
git clone https://github.com/mahamedwow1-afk/Smart-File-Organizer.git
cd Smart-File-Organizer

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Build Executable (Windows)

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --onefile --windowed --icon=icon.ico gui_main.py

# The executable will be in dist/gui_main.exe
```

---

## ⚙️ Usage

### Basic Usage

```bash
# Open the application
python main.py

# Or run the GUI version
python gui_main.py
```

### Configuration

The application reads configuration from `config.json`:

```json
{
  "source_dir": "./Downloads",
  "target_dir": "./Organized",
  "auto_sort": true,
  "dark_mode": true,
  "max_file_size_mb": 500
}
```

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open folder |
| `Ctrl+S` | Start organization |
| `Ctrl+Z` | Undo last action |
| `Ctrl+H` | Show history |
| `Ctrl+Q` | Quit application |

---

## 🛠️ Tech Stack

### Backend
- **Python 3.9+**: Core programming language
- **PyQt6**: GUI framework
- **Pillow**: Image processing
- **FFmpeg-python**: Video/audio metadata extraction

### Tools
- **PyInstaller**: Executable packaging
- **git**: Version control
- **pytest**: Testing framework

---

## 📁 Project Structure

```
Smart-File-Organizer/
├── main.py                  # Entry point
├── gui_main.py              # GUI application
├── gui_main.spec            # PyInstaller specification
├── icon.ico                 # Application icon
├── config.json              # Configuration file
├── organizer_history.json   # History database
├── README.md                # This file
└── requirements.txt         # Python dependencies
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_organizer.py -v
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Mahamed Yasser**
- Python Developer & Video Editor
- Qalyubia, Egypt
- [GitHub Profile](https://github.com/mahamedwow1-afk)

---

## 🙏 Acknowledgments

- [PyQt6](https://www.qt.io/product/development-tools) - For the beautiful GUI framework
- [Pillow](https://pillow.readthedocs.io/) - For image processing capabilities
- [FFmpeg](https://ffmpeg.org/) - For multimedia processing

---

<div align="center">

Made with ❤️ by [Mahamed Yasser](https://github.com/mahamedwow1-afk)

</div>
