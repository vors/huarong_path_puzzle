from collections import deque
from typing import List, Tuple, Set, Optional, Dict

import argparse

class PuzzleState:
    def __init__(self, board: List[List[str]]):
        self.board = [row[:] for row in board]
        self.width = len(board[0])
        self.height = len(board)
    
    def get_canonical_board(self) -> Tuple[Tuple[str, ...], ...]:
        """
        Convert board to canonical form where pieces of the same shape are normalized.
        This allows us to treat identical shapes as interchangeable.
        
        Piece shapes:
        - 2x2: appears 4 times (the goal piece) - label as 'A'
        - 1x2: appears 2 times each, 4 pieces total - label as 'B', 'C', 'D', 'E'
        - 2x1: appears 2 times (1 piece) - label as 'F'
        - 1x1: appears 1 time each, 4 pieces total - label as 'G', 'H', 'I', 'J'
        """
        # Get all piece positions
        pieces_info = self.get_piece_info()
        
        # Create a mapping from original piece labels to canonical labels
        shape_groups = {
            (2, 2): [],  # 2x2 piece
            (1, 2): [],  # 1x2 vertical pieces
            (2, 1): [],  # 2x1 horizontal pieces
            (1, 1): []   # 1x1 pieces
        }
        
        for piece_label, positions in pieces_info.items():
            min_r = min(p[0] for p in positions)
            max_r = max(p[0] for p in positions)
            min_c = min(p[1] for p in positions)
            max_c = max(p[1] for p in positions)
            
            height = max_r - min_r + 1
            width = max_c - min_c + 1
            
            shape = (width, height)
            shape_groups[shape].append((piece_label, positions))
        
        # Sort pieces within each shape group by their positions to get canonical ordering
        for shape in shape_groups:
            shape_groups[shape].sort(key=lambda x: tuple(sorted(x[1])))
        
        # Create canonical board
        canonical_board = [['.' for _ in range(self.width)] for _ in range(self.height)]
        
        # Assign canonical labels
        canonical_labels = {
            (2, 2): ['A'],
            (1, 2): ['B', 'C', 'D', 'E'],
            (2, 1): ['F'],
            (1, 1): ['G', 'H', 'I', 'J']
        }
        
        for shape, pieces in shape_groups.items():
            labels = canonical_labels[shape]
            for i, (original_label, positions) in enumerate(pieces):
                canonical_label = labels[i] if i < len(labels) else labels[-1]
                for r, c in positions:
                    canonical_board[r][c] = canonical_label
        
        return tuple(tuple(row) for row in canonical_board)
    
    def __hash__(self):
        """Hash based on canonical representation"""
        return hash(self.get_canonical_board())
    
    def __eq__(self, other):
        """Equality based on canonical representation"""
        return self.get_canonical_board() == other.get_canonical_board()
    
    def __str__(self):
        return '\n'.join(''.join(row) for row in self.board)
    
    def copy(self):
        return PuzzleState(self.board)
    
    def is_goal(self) -> bool:
        """Check if the 2x2 piece is at the bottom center"""
        # Bottom center for width 4 means columns 1-2 (0-indexed)
        # Bottom rows are height-2 and height-1 (0-indexed)
        target_positions = [
            (self.height - 2, 1), (self.height - 2, 2),
            (self.height - 1, 1), (self.height - 1, 2)
        ]
        
        # Find the 2x2 piece (appears 4 times in same positions)
        piece_counts = {}
        for r in range(self.height):
            for c in range(self.width):
                if self.board[r][c] != '.':
                    piece_counts[self.board[r][c]] = piece_counts.get(self.board[r][c], 0) + 1
        
        # The 2x2 piece appears exactly 4 times
        two_by_two = None
        for piece, count in piece_counts.items():
            if count == 4:
                two_by_two = piece
                break
        
        if not two_by_two:
            return False
        
        # Check if this piece is at the target positions
        for r, c in target_positions:
            if self.board[r][c] != two_by_two:
                return False
        
        return True
    
    def get_piece_info(self) -> Dict[str, List[Tuple[int, int]]]:
        """Get all positions occupied by each piece"""
        pieces = {}
        for r in range(self.height):
            for c in range(self.width):
                cell = self.board[r][c]
                if cell != '.':
                    if cell not in pieces:
                        pieces[cell] = []
                    pieces[cell].append((r, c))
        return pieces
    
    def can_move_piece(self, piece: str, direction: Tuple[int, int]) -> bool:
        """Check if a piece can move in a given direction"""
        dr, dc = direction
        piece_positions = self.get_piece_info()[piece]
        
        # Check all new positions
        new_positions = [(r + dr, c + dc) for r, c in piece_positions]
        
        for r, c in new_positions:
            # Out of bounds
            if r < 0 or r >= self.height or c < 0 or c >= self.width:
                return False
            
            # Check if the new position is either empty or already occupied by the same piece
            if self.board[r][c] != '.' and self.board[r][c] != piece:
                return False
        
        return True
    
    def move_piece(self, piece: str, direction: Tuple[int, int]) -> 'PuzzleState':
        """Move a piece in a given direction and return new state"""
        dr, dc = direction
        new_state = self.copy()
        piece_positions = self.get_piece_info()[piece]
        
        # Clear old positions
        for r, c in piece_positions:
            new_state.board[r][c] = '.'
        
        # Set new positions
        for r, c in piece_positions:
            new_state.board[r + dr][c + dc] = piece
        
        return new_state
    
    def get_all_moves(self) -> List[Tuple[str, str, 'PuzzleState']]:
        """Get all possible moves from current state"""
        moves = []
        pieces = self.get_piece_info()
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right
        direction_names = {(-1, 0): 'up', (1, 0): 'down', (0, -1): 'left', (0, 1): 'right'}
        
        for piece in sorted(pieces.keys()):  # Sort for consistent ordering
            for direction in directions:
                if self.can_move_piece(piece, direction):
                    new_state = self.move_piece(piece, direction)
                    moves.append((piece, direction_names[direction], new_state))
        
        return moves


def solve_puzzle(initial_board: List[str]) -> Optional[List[Tuple[str, str, PuzzleState]]]:
    """Solve the puzzle using BFS with smart canonical state deduplication"""
    # Parse initial board
    board = [list(row) for row in initial_board]
    initial_state = PuzzleState(board)
    
    print(f"Initial state canonical form:")
    print('\n'.join(''.join(row) for row in initial_state.get_canonical_board()))
    print()
    
    if initial_state.is_goal():
        return []
    
    # BFS queue: stores (current_state, path_to_current_state)
    queue = deque([(initial_state, [])])
    
    # Visited set using canonical representation for smart deduplication
    visited: Set[PuzzleState] = {initial_state}
    
    states_explored = 0
    
    while queue:
        current_state, path = queue.popleft()
        states_explored += 1
        
        if states_explored % 1000 == 0:
            print(f"Explored {states_explored} states, queue size: {len(queue)}, visited size: {len(visited)}")
        
        # Get all possible moves from current state
        for piece, direction, new_state in current_state.get_all_moves():
            # Skip if we've already visited this canonical state (smart deduplication)
            if new_state in visited:
                continue
            
            # Mark this canonical state as visited
            visited.add(new_state)
            
            # Add move to path
            new_path = path + [(piece, direction, new_state)]
            
            # Check if we reached the goal
            if new_state.is_goal():
                print(f"\nSolution found! Total states explored: {states_explored}")
                print(f"Total unique canonical states visited: {len(visited)}")
                return new_path
            
            # Add to queue for further exploration
            queue.append((new_state, new_path))
    
    print(f"\nNo solution found after exploring {states_explored} states")
    return None


# Preset boards for testing
PRESETS = {
    "1": [
        "ABBC",
        "ABBC",
        "DEEX",
        "DYZX",
        "K..I"
    ],
    "2": [
        "ABBK",
        "ABBI",
        "CCZY",
        "DXXS",
        "D..S"
    ],
    "3": [
        "AAFF",
        "AABB",
        "IEEK",
        "JYYZ",
        ".SS."
    ]
}


def parse_board(board_str: str) -> List[str]:
    """Parse a board string into a list of rows.
    
    The board can be provided as:
    - Newline-separated rows: "ABBC\\nABBC\\nDEEX\\nDYZX\\nK..I"
    - Comma-separated rows: "ABBC,ABBC,DEEX,DYZX,K..I"
    """
    # Try newline first
    if '\n' in board_str:
        rows = [row.strip() for row in board_str.strip().split('\n') if row.strip()]
    else:
        # Try comma-separated
        rows = [row.strip() for row in board_str.split(',') if row.strip()]
    
    return rows


def main():
    parser = argparse.ArgumentParser(
        description="Huarong Path Puzzle Solver",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use a preset board (1, 2, or 3):
  uv run python solver.py --preset 1

  # Provide a custom board (comma-separated rows):
  uv run python solver.py --board "ABBC,ABBC,DEEX,DYZX,K..I"

  # Provide a custom board (newline-separated in quotes):
  uv run python solver.py --board "ABBC
ABBC
DEEX
DYZX
K..I"
"""
    )
    parser.add_argument("--preset", type=str, choices=["1", "2", "3"],
                        help="Use a preset board configuration (1, 2, or 3)")
    parser.add_argument("--board", type=str,
                        help="Custom board as comma-separated or newline-separated rows")
    args = parser.parse_args()

    if args.board:
        initial_board = parse_board(args.board)
    elif args.preset:
        initial_board = PRESETS[args.preset]
    else:
        # Default to preset 1
        initial_board = PRESETS["1"]

    print("Initial Board:")
    print('\n'.join(initial_board))
    print("\n" + "="*50 + "\n")
    
    print("Solving puzzle using BFS with smart canonical deduplication...")
    print("(Treating same-shaped pieces as interchangeable)")
    print()
    
    solution = solve_puzzle(initial_board)
    
    if solution is None:
        print("No solution found!")
    else:
        print(f"\n{'='*50}\n")
        print(f"Solution found in {len(solution)} moves!\n")
        print("="*50 + "\n")
        
        # Print initial state
        print("Step 0: Initial Position")
        print('\n'.join(initial_board))
        print()
        
        # Print each move
        for i, (piece, direction, state) in enumerate(solution, 1):
            print(f"Step {i}: Move piece '{piece}' {direction}")
            print(state)
            print()
        
        print("="*50)
        print("GOAL REACHED!")
        print("="*50)


if __name__ == "__main__":
    main()