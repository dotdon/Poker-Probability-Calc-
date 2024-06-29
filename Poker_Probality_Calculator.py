import tkinter as tk
from tkinter import ttk, Menu, Toplevel, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
import random
import os

class PokerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Poker Probability Calculator")
        self.master.attributes("-alpha", 0.95)  # Set slight transparency

        # Use a style object to encourage a more modern look
        style = ttk.Style(self.master)
        style.theme_use('clam')  # 'clam', 'alt', 'default', 'classic' to test different looks
        style.configure('TButton', font=('Helvetica', 12), padding=10)
        style.configure('TLabel', font=('Helvetica', 14), background='lightgray', relief='flat')
        style.configure('TFrame', background='lightgray')
        style.configure('CardButton.TButton', padding=5)
        style.configure('SelectedCard.TButton', background='lightblue')
        style.configure('CommunityCard.TButton', background='lightcoral')

        self.card_images = {}
        self.my_cards = []
        self.community_cards = []

        self.setup_card_images()
        self.load_card_images()
        self.setup_gui()

    def setup_card_images(self):
        card_folder = 'cards/'
        os.makedirs(card_folder, exist_ok=True)
        for rank in '23456789TJQKA':
            for suit in 'shdc':
                card_code = f'{rank}{suit}'.upper()
                file_path = f'{card_folder}{rank.lower()}{suit}.png'
                if not os.path.exists(file_path):
                    self.generate_card_image(rank, suit, file_path)

    def generate_card_image(self, rank, suit, file_path):
        image = Image.new('RGB', (72, 96), 'white')
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("Arial.ttf", 24)  # Use a TrueType font for better appearance
        suit_symbols = {'s': '♠', 'h': '♥', 'd': '♦', 'c': '♣'}
        text = f'{rank}{suit_symbols[suit.lower()]}'
        draw.text((10, 30), text, font=font, fill='black')
        image.save(file_path)

    def load_card_images(self):
        card_folder = 'cards/'
        for rank in '23456789TJQKA':
            for suit in 'shdc':
                card_code = f'{rank}{suit}'.upper()
                file_path = f'{card_folder}{rank.lower()}{suit}.png'
                image = Image.open(file_path).resize((72, 96), Image.Resampling.LANCZOS)
                self.card_images[card_code] = ImageTk.PhotoImage(image)

    def setup_gui(self):
        frame = ttk.Frame(self.master, padding="3 3 12 12")
        frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        ttk.Button(frame, text="Select My Cards", command=lambda: self.show_card_selector(self.my_cards, 'blue')).grid(column=1, row=1, sticky=tk.W)
        ttk.Button(frame, text="Select Community Cards", command=lambda: self.show_card_selector(self.community_cards, 'red')).grid(column=2, row=1, sticky=tk.W)

        self.result_label = ttk.Label(frame, text="Probability: 0.00%", font=('Helvetica', 16))
        self.result_label.grid(column=1, row=2, columnspan=2, sticky=(tk.W, tk.E))

        self.explanation_label = ttk.Label(frame, text="The probability represents your chances of winning the hand based on 50,000 simulations.", font=('Helvetica', 12), wraplength=400)
        self.explanation_label.grid(column=1, row=3, columnspan=2, sticky=(tk.W, tk.E))

        ttk.Button(frame, text="Calculate Probability", command=self.calculate_probability).grid(column=1, row=4, columnspan=2, sticky=tk.W)

    def show_card_selector(self, card_list, color):
        popup = Toplevel(self.master)
        popup.title("Select Cards")
        frame = ttk.Frame(popup, padding="3 3 12 12")
        frame.pack()

        row = 0
        col = 0
        for card_code, img in self.card_images.items():
            btn = ttk.Button(frame, image=img, style='CardButton.TButton')
            btn.image = img
            btn.grid(row=row, column=col, padx=5, pady=5)
            if card_code in card_list:
                if color == 'blue':
                    btn.config(style='SelectedCard.TButton')
                else:
                    btn.config(style='CommunityCard.TButton')
            btn.bind("<Button-1>", lambda event, c=card_code, cl=card_list, b=btn, col=color: self.toggle_card(c, cl, b, col))
            btn.bind("<Button-3>", lambda event, c=card_code, cl=card_list, b=btn, col=color: self.add_card(c, cl, b, col))
            col += 1
            if col % 10 == 0:
                row += 1
                col = 0

    def toggle_card(self, card_code, card_list, button, color):
        if card_code in card_list:
            card_list.remove(card_code)
            button.config(style='CardButton.TButton')  # Default style
        else:
            card_list.append(card_code)
            if color == 'blue':
                button.config(style='SelectedCard.TButton')  # Highlighted style
            else:
                button.config(style='CommunityCard.TButton')  # Community card style
        self.update_gui()

    def add_card(self, card_code, card_list, button, color):
        card_list.append(card_code)
        if color == 'blue':
            button.config(style='SelectedCard.TButton')  # Highlighted style
        else:
            button.config(style='CommunityCard.TButton')  # Community card style
        self.update_gui()

    def update_gui(self):
        selected_cards = ' '.join(self.my_cards + self.community_cards)
        self.result_label.config(text=f"Selected Cards: {selected_cards}")

    def calculate_probability(self):
        if len(self.my_cards) != 2 or len(self.community_cards) not in [0, 3, 4, 5]:
            messagebox.showerror("Error", "Check the number of selected cards.")
            return

        deck = [f'{r}{s}' for r in '23456789TJQKA' for s in 'shdc' if f'{r}{s}' not in self.my_cards + self.community_cards]
        probability = self.simulate_hand(self.my_cards, self.community_cards, deck, 1, 50000)
        self.result_label.config(text=f"Probability: {probability:.2%}")

    def simulate_hand(self, my_cards, community_cards, full_deck, num_opponents, num_simulations=50000):
        wins = 0
        total = 0

        for _ in range(num_simulations):
            deck = full_deck[:]
            random.shuffle(deck)

            board = community_cards[:]
            while len(board) < 5:
                board.append(deck.pop())

            if len(deck) < num_opponents * 2:
                continue

            my_strength = self.evaluate_hand(my_cards + board)

            opponent_strengths = []
            for _ in range(num_opponents):
                opponent_hand = [deck.pop() for _ in range(2)]
                opponent_strengths.append(self.evaluate_hand(opponent_hand + board))

            if my_strength > max(opponent_strengths):
                wins += 1
            total += 1

        return wins / total if total > 0 else 0

    def evaluate_hand(self, cards):
        suits = 'shdc'
        ranks = '23456789TJQKA'
        values = {r: i for i, r in enumerate(ranks)}
        card_ranks = [values[card[0]] for card in cards]
        card_suits = [card[1] for card in cards]

        rank_counts = {rank: card_ranks.count(rank) for rank in set(card_ranks)}
        suit_counts = {suit: card_suits.count(suit) for suit in set(card_suits)}

        is_flush = max(suit_counts.values()) >= 5
        is_straight = False
        sorted_ranks = sorted(rank_counts.keys())
        for i in range(len(sorted_ranks) - 4):
            if sorted_ranks[i + 4] - sorted_ranks[i] == 4:
                is_straight = True
                break

        if 14 in sorted_ranks and sorted_ranks[-1] == 5 and sorted_ranks[0] == 2:
            is_straight = True

        if is_straight and is_flush:
            return 8
        if 4 in rank_counts.values():
            return 7
        if 3 in rank_counts.values() and 2 in rank_counts.values():
            return 6
        if is_flush:
            return 5
        if is_straight:
            return 4
        if 3 in rank_counts.values():
            return 3
        if list(rank_counts.values()).count(2) == 2:
            return 2
        if 2 in rank_counts.values():
            return 1
        return 0

if __name__ == "__main__":
    root = tk.Tk()
    app = PokerApp(root)
    root.mainloop()

