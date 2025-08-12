
# A simple Tic-Tac-Toe game in Python

board = [' ' for _ in range(9)] # A list to represent the 3x3 board

def print_board():
    """Prints the Tic-Tac-Toe board."""
    row1 = f"| {board[0]} | {board[1]} | {board[2]} |"
    row2 = f"| {board[3]} | {board[4]} | {board[5]} |"
    row3 = f"| {board[6]} | {board[7]} | {board[8]} |"
    print()
    print(row1)
    print(row2)
    print(row3)
    print()

def check_win(player):
    """Checks if a player has won."""
    win_conditions = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8), # Horizontal
        (0, 3, 6), (1, 4, 7), (2, 5, 8), # Vertical
        (0, 4, 8), (2, 4, 6)             # Diagonal
    ]
    for condition in win_conditions:
        if board[condition[0]] == board[condition[1]] == board[condition[2]] == player:
            return True
    return False

def check_draw():
    """Checks if the game is a draw."""
    return ' ' not in board

def get_move(player):
    """Gets the player's move and updates the board."""
    while True:
        try:
            move = int(input(f"Player {player}, enter your move (1-9): "))
            if 1 <= move <= 9 and board[move - 1] == ' ':
                board[move - 1] = player
                break
            else:
                print("Invalid move. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def main():
    """The main game loop."""
    current_player = 'X'
    while True:
        print_board()
        get_move(current_player)
        if check_win(current_player):
            print_board()
            print(f"Player {current_player} wins!")
            break
        if check_draw():
            print_board()
            print("It's a draw!")
            break
        current_player = 'O' if current_player == 'X' else 'X'

if __name__ == "__main__":
    main()
