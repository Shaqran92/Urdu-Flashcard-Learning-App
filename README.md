# 🎴 Flashy – Learn Urdu with Flashcards

An interactive **Urdu Flashcard Learning Desktop App** built with **Python, Tkinter, and Pandas**.  
This application helps users learn Urdu vocabulary efficiently using smart flashcards, progress tracking, and a clean, beginner-friendly UI.

---

## 📌 Features

- 🧠 **Flashcard-based learning system**
- 🔄 **Auto-flip cards** after 3 seconds (can be toggled)
- 👆 **Manual flip** option
- 📊 **Progress tracking** with percentage & progress bar
- ❌ Mark words as *Don't Know*
- ✅ Mark words as *Known* (automatically removed)
- ↩ **Undo** last action
- 💾 **Progress saved automatically** (CSV-based storage)
- ⌨️ **Keyboard shortcuts** for fast navigation
- 🎨 Clean and responsive **Tkinter UI**
- 🔁 **Reset progress** anytime

---

## 🛠️ Technologies Used

- **Python 3**
- **Tkinter** – GUI
- **Pandas** – CSV data handling
- **ttk** – Progress bar & UI widgets
- **Pathlib** – File system management

---

## 📂 Project Structure

```bash
flashy-urdu/
│
├── main.py
├── data/
│ ├── urdu_words.csv
│ ├── words_to_learn.csv
│
├── images/
│ ├── front.png
│ ├── back.png
│ ├── right.png
│ └── wrong.png
│
├── learning_stats.csv
└── README.md
```


---

## 🚀 How to Run the Project

1. **Clone the repository**
```bash
git clone https://github.com/your-username/flashy-urdu.git
```

```bash
pip install pandas
```
```bash
python main.py
```

## ⌨️ Keyboard Shortcuts

| Key | Action |
| :-------- | ---------: |
| Space | Flip card |
| → | Don't know |
| ← | Know |
| U | Undo |
| R | Reset |
| Esc | Exit |

## 🧑‍💻 Author

### Shaqran Hussain
Python Developer | GUI Apps | Learning Projects
🔗 GitHub: https://github.com/Shaqran92/Urdu-Flashcard-Learning-App
