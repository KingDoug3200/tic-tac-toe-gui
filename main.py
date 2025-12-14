import random
import tkinter as tk
from tkinter import ttk, messagebox

EMPTY = ""

def other_player(p: str) -> str:
    return "O" if p == "X" else "X"

class TicTacToe:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.board = [EMPTY] * 9
        self.turn = "X"
        self.winner = None # "X" / "O" / "Draw" / None

    def available_moves(self):
        return [i for i, v in enumerate(self.board) if v == EMPTY]
    
    def make_move(self, idx: int) -> bool:
        if self.winner is not None:
            return False
        if idx < 0 or idx >= 9:
            return False
        if self.board[idx] != EMPTY:
            return False
        self.board[idx] = self.turn
        self._update_winner()
        if self.winner is None:
            self.turn = other_player(self.turn)
        return True
    
    def _update_winner(self):
        lines = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8), # rows
            (0, 3, 6), (1, 4, 7), (2, 5, 8), # cols
            (0, 4, 8), (2, 4, 6) # diagonals
        ]
        for a, b, c in lines:
            if self.board[a] and self.board[a] == self.board[b] == self.board[c]:
                self.winner = self.board[a]
                return
        
        if all(v != EMPTY for v in self.board):
            self.winner = "Draw"

# ---------- AI ----------
def best_move_easy(game: TicTacToe) -> int:
    # Random valid move
    return random.choice(game.available_moves())

def best_move_medium(game: TicTacToe, ai_symbol: str) -> int:
    # 1) win if possible
    # 2) block opponent win
    # 3) else random
    opp = other_player(ai_symbol)

    for m in game.available_moves():
        g2 = clone_game(game)
        g2.turn = ai_symbol
        g2.make_move(m)
        if g2.winner == ai_symbol:
            return m
        
    for m in game.available_moves():
        g2 = clone_game(game)
        g2.turn = opp
        g2.make_move(m)
        if g2.winner == opp:
            return m
    
    return best_move_easy(game)

def clone_game(game: TicTacToe) -> TicTacToe:
    g2 = TicTacToe()
    g2.board = game.board[:]
    g2.turn = game.turn
    g2.winner = game.winner
    return g2

def minimax(game: TicTacToe, ai_symbol: str, maximizing: bool) -> int:
    # Return score from AI perspective:
    # +1 AI win, -1 AI loss, 0 draw
    if game.winner is not None:
        if game.winner == "Draw":
            return 0
        return 1 if game.winner == ai_symbol else -1
    
    current = game.turn
    moves = game.available_moves()

    if maximizing:
        best = -999
        for m in moves:
            g2 = clone_game(game)
            g2.turn = current
            g2.make_move(m)
            score = minimax(g2, ai_symbol, False)
            best = max(best, score)
        return best
    else:
        best = 999
        for m in moves:
            g2 = clone_game(game)
            g2.turn = current
            g2.make_move(m)
            score = minimax(g2, ai_symbol, True)
            best = min(best, score)
        return best

def best_move_hard(game: TicTacToe, ai_symbol: str) -> int:
    # Perfect play usng minimax
    best_score = -999
    best_moves = []
    for m in game.available_moves():
        g2 = clone_game(game)
        g2.turn = ai_symbol
        g2.make_move(m)
        score = minimax(g2, ai_symbol, False)
        if score > best_score:
            best_score = score
            best_moves = [m]
        elif score == best_score:
            best_moves.append(m)
    
    # Randomize between equally optimal moves (so it doesnt feel identical every game)
    return random.choice(best_moves)

# ----------- GUI ----------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tic-Tac-Toe")
        self.resizable(False, False)

        self.game = TicTacToe()

        # Mode settings
        self.mode = tk.StringVar(value="Two Player")
        self.difficulty = tk.StringVar(value="Easy")
        self.human_symbol = tk.StringVar(value="X") # For vs AI, human plays X or O

        self._build_ui()
        self._sync_ui_with_state()
    
    def _build_ui(self):
        root = ttk.Frame(self, padding=12)
        root.grid(row=0, column=0)

        # Top controls
        controls = ttk.LabelFrame(root, text="Game Options", padding=10)
        controls.grid(row=0, column=0, sticky="ew")

        ttk.Label(controls, text="Mode:").grid(row=0, column=0, sticky="w")
        mode_cb = ttk.Combobox(
            controls,
            textvariable=self.mode,
            values=["Two Players", "Vs AI"],
            state="readonly",
            width=12
        )
        mode_cb.grid(row=0, column=1, padx=6)
        mode_cb.bind("<<ComboboxSelected>>", lambda e: self._on_mode_change())

        ttk.Label(controls, text="Difficulty:").grid(row=0, column=2, sticky="w")
        self.diff_cb = ttk.Combobox(
            controls,
            textvariable=self.difficulty,
            values=["Easy", "Medium", "Hard"],
            state="readonly",
            width=10
        )
        self.diff_cb.grid(row=0, column=3, padx=6)

        ttk.Label(controls, text="You play:").grid(row=0, column=4, sticky="w")
        self.symbol_cb = ttk.Combobox(
            controls,
            textvariable=self.human_symbol,
            values=["X", "O"],
            state="readonly",
            width=4
        )
        self.symbol_cb.grid(row=0, column=5, padx=6)

        ttk.Button(controls, text="New Game", command=self.new_game).grid(row=0, column=6, padx=6)

        # Status label
        self.status = ttk.Label(root, text="", padding=(0, 10))
        self.status.grid(row=3, column=0, sticky="w")

        # Board
        board_frame = ttk.Frame(root)
        board_frame.grid(row=2, column=0)

        self.buttons = []
        for r in range(3):
            for c in range(3):
                idx = r * 3 + c 
                btn = ttk.Button(
                    board_frame,
                    text="",
                    width=6,
                    command=lambda i=idx: self.on_click(i)
                )
                btn.grid(row=r, column=c, padx=4, pady=4, ipadx=6, ipady=6)
        
        self._on_mode_change()

    def _on_mode_change(self):
        is_vs_ai = (self.mode.get() == "Vs AI")
        self.diff_cb.configure(state="readonly" if is_vs_ai else "disabled")
        self.symbol_cb.configure(state="readonly" if is_vs_ai else"disabled")
        self.new_game()
    
    def _sync_ui_with_state(self):
        # Update board text + disable filled squares
        for i, btn in enumerate(self.buttons):
            btn.configure(text=self.game.board[i])
            state = "disabled" if self.game.board[i] != EMPTY or self.game.winner else "normal"
            btn.configure(state=state)
        
        # Status
        if self.game.winner == "Draw":
            self.status.configure(text="Result: Draw.")
        elif self.game.winner in ("X", "O"):
            self.status.configure(text=f"Winner: {self.game.winner}")
        else:
            self.status.configure(text=f"Turn: {self.game.turn}")
    
    def new_game(self):
        self.game.reset()
        self._sync_ui_with_state()

        # If vs AI and human chose "O", AI should start as X
        if self.mode.get() == "Vs AI":
            if self.human_symbol.get() == "O":
                self.after(150, self._ai_take_turn)
    
    def on_click(self, idx: int):
        if self.game.winner is not None:
            return
        
        if self.mode.get() == "Two Player":
            moved = self.game.make_move(idx)
            if moved:
                self._sync_ui_with_state()
                self._maybe_show_end_popup()
            return
        
        # Vs AI
        human = self.human_symbol.get()
        ai = other_player(human)

        # Only allow click if it is human's turn
        if self.game.turn != human:
            return
        
        moved = self.game.make_move(idx)
        if moved:
            self._sync_ui_with_state()
            if self.game.winner is None:
                self.after(150, self._ai_take_turn)
            else:
                self._maybe_show_end_popup()
    
    def _ai_take_turn(self):
        if self.game.winner is not None:
            self._maybe_show_end_popup()
            return
        
        human = self.human_symbol.get()
        ai = other_player(human)

        if self.game.turn != ai:
            return
        
        if self.difficulty.get() == "Easy":
            move = best_move_easy(self.game)
        elif self.difficulty.get() == "Medium":
            move = best_move_medium(self.game, ai)
        else:
            move = best_move_hard(self.game, ai)
        
        self.game.make_move(move)
        self._sync_ui_with_state()
        self._maybe_show_end_popup()

    def _maybe_show_end_popup(self):
        if self.game.winner is None:
            return
        if self.game.winner == "Draw":
            messagebox.showinfo("Game Over", "It's a draw!")
        else:
            messagebox.showinfo("Game Over", f"{self.game.winner} wins!")

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
