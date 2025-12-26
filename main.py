# ============== IMPORTS ==============
from tkinter import *
from tkinter import messagebox, ttk
import pandas as pd
import random
from pathlib import Path
import os
from datetime import datetime

# ============== CONSTANTS ==============
class Config:
    """Application configuration constants"""
    # Colors
    BACKGROUND_COLOR = "#A9D6E5"
    CARD_FRONT_COLOR = "#FFFFFF"
    CARD_BACK_COLOR = "#2B2B2B"
    TEXT_DARK = "#000000"
    TEXT_LIGHT = "#FFFFFF"
    SUCCESS_COLOR = "#4CAF50"
    DANGER_COLOR = "#F44336"
    
    # Timing
    FLIP_DELAY = 3000  # milliseconds
    
    # Fonts
    TITLE_FONT = ("Arial", 20, "italic")
    WORD_FONT = ("Arial", 35, "bold")
    STATS_FONT = ("Arial", 12)
    BUTTON_FONT = ("Arial", 10, "bold")
    
    # Paths
    BASE_DIR = Path(__file__).parent if "__file__" in dir() else Path(".")
    DATA_DIR = BASE_DIR / "data"
    IMAGES_DIR = BASE_DIR / "images"
    
    # Files
    ORIGINAL_FILE = DATA_DIR / "urdu_words.csv"
    PROGRESS_FILE = DATA_DIR / "words_to_learn.csv"
    STATS_FILE = DATA_DIR / "learning_stats.csv"


# ============== FLASHCARD APP CLASS ==============
class FlashcardApp:
    """Main Flashcard Application Class"""
    
    def __init__(self):
        self.window = Tk()
        self.window.title("🎴 Flashy - Learn Urdu")
        self.window.config(padx=50, pady=50, bg=Config.BACKGROUND_COLOR)
        
        # State variables
        self.current_card = {}
        self.flip_timer = None
        self.cards_learned_today = 0
        self.session_start = datetime.now()
        self.is_flipped = False
        self.auto_flip_enabled = True
        
        # Load data
        self.to_learn = self._load_data()
        self.original_count = len(self.to_learn)
        
        # Setup UI
        self._setup_ui()
        self._setup_keyboard_shortcuts()
        
        # Start first card
        if self.to_learn:
            self.next_card()
        else:
            self._show_completion_message()
    
    def _load_data(self) -> list:
        """Load vocabulary data from CSV files"""
        try:
            # Try to load progress file first
            if Config.PROGRESS_FILE.exists():
                data = pd.read_csv(Config.PROGRESS_FILE)
                if len(data) > 0:
                    return data.to_dict(orient="records")
            
            # Fall back to original file
            if Config.ORIGINAL_FILE.exists():
                original_data = pd.read_csv(Config.ORIGINAL_FILE)
                return original_data.to_dict(orient="records")
            
            # Demo data if no files exist
            messagebox.showwarning(
                "Data Not Found",
                "No vocabulary files found. Loading demo data."
            )
            return [
                {"Urdu": "سلام", "English": "Hello"},
                {"Urdu": "شکریہ", "English": "Thank you"},
                {"Urdu": "پانی", "English": "Water"},
            ]
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}")
            return []
    
    def _setup_ui(self):
        """Setup all UI components"""
        # Header Frame
        self.header_frame = Frame(self.window, bg=Config.BACKGROUND_COLOR)
        self.header_frame.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Progress Label
        self.progress_label = Label(
            self.header_frame,
            text=self._get_progress_text(),
            font=Config.STATS_FONT,
            bg=Config.BACKGROUND_COLOR
        )
        self.progress_label.pack()
        
        # Progress Bar
        self.progress_var = DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.header_frame,
            length=400,
            mode='determinate',
            variable=self.progress_var
        )
        self.progress_bar.pack(pady=5)
        self._update_progress_bar()
        
        # Canvas for flashcard
        self.canvas = Canvas(
            self.window,
            width=500,
            height=300,
            bg=Config.BACKGROUND_COLOR,
            highlightthickness=0
        )
        self.canvas.grid(row=1, column=0, columnspan=2, pady=20)
        
        # Load images with error handling
        try:
            self.card_front = PhotoImage(file=Config.IMAGES_DIR / "front.png")
            self.card_back = PhotoImage(file=Config.IMAGES_DIR / "back.png")
        except:
            # Create simple rectangles if images not found
            self.card_front = None
            self.card_back = None
        
        # Card elements
        if self.card_front:
            self.card_image = self.canvas.create_image(
                250, 150,
                image=self.card_front
            )
        else:
            self.card_image = self.canvas.create_rectangle(
                10, 10, 490, 290,
                fill="white", outline="gray", width=2
            )
        
        self.card_title = self.canvas.create_text(
            250, 80,
            text="",
            font=Config.TITLE_FONT
        )
        self.card_word = self.canvas.create_text(
            250, 170,
            text="",
            font=Config.WORD_FONT
        )
        
        # Buttons Frame
        self.button_frame = Frame(self.window, bg=Config.BACKGROUND_COLOR)
        self.button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        # Try to load button images, fallback to text buttons
        try:
            self.cross_image = PhotoImage(file=Config.IMAGES_DIR / "wrong.png")
            self.tick_image = PhotoImage(file=Config.IMAGES_DIR / "right.png")
            
            self.cross_button = Button(
                self.button_frame,
                image=self.cross_image,
                bg=Config.BACKGROUND_COLOR,
                highlightthickness=0,
                command=self.next_card
            )
            self.tick_button = Button(
                self.button_frame,
                image=self.tick_image,
                bg=Config.BACKGROUND_COLOR,
                highlightthickness=0,
                command=self.is_known  # FIXED: Was next_card in original
            )
        except:
            self.cross_button = Button(
                self.button_frame,
                text="✗ Don't Know",
                font=Config.BUTTON_FONT,
                bg=Config.DANGER_COLOR,
                fg="white",
                padx=20,
                pady=10,
                command=self.next_card
            )
            self.tick_button = Button(
                self.button_frame,
                text="✓ Know It!",
                font=Config.BUTTON_FONT,
                bg=Config.SUCCESS_COLOR,
                fg="white",
                padx=20,
                pady=10,
                command=self.is_known
            )
        
        self.cross_button.pack(side=LEFT, padx=20)
        self.tick_button.pack(side=LEFT, padx=20)
        
        # Control Frame
        self.control_frame = Frame(self.window, bg=Config.BACKGROUND_COLOR)
        self.control_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Flip Button
        self.flip_button = Button(
            self.control_frame,
            text="🔄 Flip Card (Space)",
            font=Config.STATS_FONT,
            command=self.manual_flip,
            bg="#E0E0E0"
        )
        self.flip_button.pack(side=LEFT, padx=5)
        
        # Auto-flip Toggle
        self.auto_flip_var = BooleanVar(value=True)
        self.auto_flip_check = Checkbutton(
            self.control_frame,
            text="Auto-flip (3s)",
            variable=self.auto_flip_var,
            bg=Config.BACKGROUND_COLOR,
            font=Config.STATS_FONT,
            command=self._toggle_auto_flip
        )
        self.auto_flip_check.pack(side=LEFT, padx=5)
        
        # Undo Button
        self.undo_button = Button(
            self.control_frame,
            text="↩ Undo",
            font=Config.STATS_FONT,
            command=self.undo_last,
            bg="#FFE082",
            state=DISABLED
        )
        self.undo_button.pack(side=LEFT, padx=5)
        
        # Reset Button
        self.reset_button = Button(
            self.control_frame,
            text="🔄 Reset All",
            font=Config.STATS_FONT,
            command=self.reset_progress,
            bg="#FFCDD2"
        )
        self.reset_button.pack(side=LEFT, padx=5)
        
        # Stats Frame
        self.stats_frame = Frame(self.window, bg=Config.BACKGROUND_COLOR)
        self.stats_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        self.stats_label = Label(
            self.stats_frame,
            text="Session: 0 cards learned",
            font=Config.STATS_FONT,
            bg=Config.BACKGROUND_COLOR
        )
        self.stats_label.pack()
        
        # Keyboard shortcuts hint
        self.hint_label = Label(
            self.window,
            text="⌨️ Shortcuts: Space=Flip | →=Don't Know | ←=Know | R=Reset",
            font=("Arial", 9),
            bg=Config.BACKGROUND_COLOR,
            fg="gray"
        )
        self.hint_label.grid(row=5, column=0, columnspan=2, pady=(20, 0))
        
        # Store for undo
        self.last_removed = None
    
    def _setup_keyboard_shortcuts(self):
        """Setup keyboard bindings"""
        self.window.bind("<space>", lambda e: self.manual_flip())
        self.window.bind("<Right>", lambda e: self.next_card())
        self.window.bind("<Left>", lambda e: self.is_known())
        self.window.bind("<r>", lambda e: self.reset_progress())
        self.window.bind("<u>", lambda e: self.undo_last())
        self.window.bind("<Escape>", lambda e: self.window.quit())
    
    def _get_progress_text(self) -> str:
        """Get progress text for display"""
        total = self.original_count
        remaining = len(self.to_learn)
        learned = total - remaining
        percentage = (learned / total * 100) if total > 0 else 0
        return f"📚 Progress: {learned}/{total} words learned ({percentage:.1f}%)"
    
    def _update_progress_bar(self):
        """Update the progress bar"""
        if self.original_count > 0:
            learned = self.original_count - len(self.to_learn)
            self.progress_var.set((learned / self.original_count) * 100)
    
    def _update_stats(self):
        """Update all statistics displays"""
        self.progress_label.config(text=self._get_progress_text())
        self._update_progress_bar()
        self.stats_label.config(
            text=f"🎯 Session: {self.cards_learned_today} cards learned"
        )
    
    def next_card(self):
        """Display the next flashcard"""
        if self.flip_timer:
            self.window.after_cancel(self.flip_timer)
        
        if not self.to_learn:
            self._show_completion_message()
            return
        
        self.is_flipped = False
        self.current_card = random.choice(self.to_learn)
        
        # Update card display
        self._show_front()
        
        # Start auto-flip timer if enabled
        if self.auto_flip_enabled:
            self.flip_timer = self.window.after(
                Config.FLIP_DELAY,
                self.flip_card
            )
    
    def _show_front(self):
        """Show the front of the card"""
        if self.card_front:
            self.canvas.itemconfig(self.card_image, image=self.card_front)
        else:
            self.canvas.itemconfig(self.card_image, fill="white")
        
        self.canvas.itemconfig(
            self.card_title,
            text="🇵🇰 Urdu",
            fill=Config.TEXT_DARK
        )
        self.canvas.itemconfig(
            self.card_word,
            text=self.current_card.get("Urdu", ""),
            fill=Config.TEXT_DARK
        )
    
    def flip_card(self):
        """Flip the card to show the answer"""
        self.is_flipped = True
        
        if self.card_back:
            self.canvas.itemconfig(self.card_image, image=self.card_back)
        else:
            self.canvas.itemconfig(self.card_image, fill="#2B2B2B")
        
        self.canvas.itemconfig(
            self.card_title,
            text="🇬🇧 English",
            fill=Config.TEXT_LIGHT
        )
        self.canvas.itemconfig(
            self.card_word,
            text=self.current_card.get("English", ""),
            fill=Config.TEXT_LIGHT
        )
    
    def manual_flip(self):
        """Manually flip the card"""
        if self.flip_timer:
            self.window.after_cancel(self.flip_timer)
        
        if self.is_flipped:
            self._show_front()
            self.is_flipped = False
        else:
            self.flip_card()
    
    def _toggle_auto_flip(self):
        """Toggle auto-flip feature"""
        self.auto_flip_enabled = self.auto_flip_var.get()
        if not self.auto_flip_enabled and self.flip_timer:
            self.window.after_cancel(self.flip_timer)
    
    def is_known(self):
        """Mark current card as known and remove from learning list"""
        if not self.current_card or not self.to_learn:
            return
        
        # Store for undo
        self.last_removed = self.current_card.copy()
        self.undo_button.config(state=NORMAL)
        
        # Remove from list
        if self.current_card in self.to_learn:
            self.to_learn.remove(self.current_card)
        
        self.cards_learned_today += 1
        
        # Save progress
        self._save_progress()
        
        # Update display
        self._update_stats()
        
        # Next card
        self.next_card()
    
    def undo_last(self):
        """Undo the last 'known' action"""
        if self.last_removed:
            self.to_learn.append(self.last_removed)
            self.cards_learned_today = max(0, self.cards_learned_today - 1)
            self._save_progress()
            self._update_stats()
            self.last_removed = None
            self.undo_button.config(state=DISABLED)
            messagebox.showinfo("Undo", "Last word restored to learning list!")
    
    def _save_progress(self):
        """Save current progress to CSV"""
        try:
            Config.DATA_DIR.mkdir(parents=True, exist_ok=True)
            df = pd.DataFrame(self.to_learn)
            df.to_csv(Config.PROGRESS_FILE, index=False)
        except Exception as e:
            print(f"Error saving progress: {e}")
    
    def reset_progress(self):
        """Reset all progress"""
        if messagebox.askyesno(
            "Reset Progress",
            "Are you sure you want to reset all progress?\nThis cannot be undone!"
        ):
            try:
                if Config.PROGRESS_FILE.exists():
                    Config.PROGRESS_FILE.unlink()
                
                # Reload original data
                self.to_learn = self._load_data()
                self.original_count = len(self.to_learn)
                self.cards_learned_today = 0
                self._update_stats()
                
                if self.to_learn:
                    self.next_card()
                
                messagebox.showinfo("Reset", "Progress has been reset!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset: {e}")
    
    def _show_completion_message(self):
        """Show completion message when all cards are learned"""
        self.canvas.itemconfig(self.card_title, text="🎉 Congratulations!", fill="green")
        self.canvas.itemconfig(self.card_word, text="All words learned!", fill="green")
        
        if self.card_front:
            self.canvas.itemconfig(self.card_image, image=self.card_front)
        
        messagebox.showinfo(
            "🎉 Congratulations!",
            f"You've learned all {self.original_count} words!\n\n"
            f"Cards learned this session: {self.cards_learned_today}\n\n"
            "Click 'Reset All' to start over."
        )
    
    def run(self):
        """Start the application"""
        self.window.mainloop()


# ============== MAIN ==============
def main():
    """Main entry point"""
    app = FlashcardApp()
    app.run()


if __name__ == "__main__":
    main()