"""
Unit tests for the Huarong Path Puzzle Solver.

These tests verify that the solver can find solutions for the preset puzzle configurations.
"""

import pytest
from solver import solve_puzzle, PuzzleState, parse_board, PRESETS


class TestPuzzleState:
    """Tests for the PuzzleState class."""

    def test_is_goal_returns_true_when_2x2_at_bottom_center(self):
        """Test that is_goal correctly identifies when 2x2 piece is at goal position."""
        # Board with 2x2 piece (BB) at bottom center
        # BB is the 2x2 piece that needs to reach the goal
        goal_board = [
            "XADC",
            "XADC",
            "IYEE",
            ".BB.",
            ".BB."
        ]
        state = PuzzleState([list(row) for row in goal_board])
        assert state.is_goal() is True

    def test_is_goal_returns_false_when_2x2_not_at_goal(self):
        """Test that is_goal returns False when 2x2 piece is not at goal position."""
        board = [
            "ABBC",
            "ABBC",
            "DEEX",
            "DYZX",
            "K..I"
        ]
        state = PuzzleState([list(row) for row in board])
        assert state.is_goal() is False

    def test_get_piece_info_identifies_all_pieces(self):
        """Test that get_piece_info correctly identifies all pieces and their positions."""
        board = [
            "ABBC",
            "ABBC",
            "DEEX",
            "DYZX",
            "K..I"
        ]
        state = PuzzleState([list(row) for row in board])
        pieces = state.get_piece_info()
        
        # Check the 2x2 piece (BB) - this is Cao Cao
        assert 'B' in pieces
        assert len(pieces['B']) == 4
        assert set(pieces['B']) == {(0, 1), (0, 2), (1, 1), (1, 2)}
        
        # Check a 1x2 vertical piece (A)
        assert 'A' in pieces
        assert len(pieces['A']) == 2
        assert set(pieces['A']) == {(0, 0), (1, 0)}

    def test_can_move_piece_respects_boundaries(self):
        """Test that can_move_piece respects board boundaries."""
        board = [
            "ABBC",
            "ABBC",
            "DEEX",
            "DYZX",
            "K..I"
        ]
        state = PuzzleState([list(row) for row in board])
        
        # A piece at top-left cannot move up
        assert state.can_move_piece('A', (-1, 0)) is False
        # A piece at top-left cannot move left
        assert state.can_move_piece('A', (0, -1)) is False

    def test_move_piece_updates_board_correctly(self):
        """Test that move_piece correctly updates piece positions."""
        board = [
            "ABBC",
            "ABBC",
            "DEEX",
            "DYZX",
            "K..I"
        ]
        state = PuzzleState([list(row) for row in board])
        
        # Move I left (it can move left since there's an empty space)
        new_state = state.move_piece('I', (0, -1))
        
        # Check I is now at column 2 instead of 3
        assert new_state.board[4][3] == '.'
        assert new_state.board[4][2] == 'I'


class TestParseBoard:
    """Tests for board parsing functionality."""

    def test_parse_board_comma_separated(self):
        """Test parsing comma-separated board string."""
        board_str = "ABBC,ABBC,DEEX,DYZX,K..I"
        result = parse_board(board_str)
        assert result == ["ABBC", "ABBC", "DEEX", "DYZX", "K..I"]

    def test_parse_board_newline_separated(self):
        """Test parsing newline-separated board string."""
        board_str = "ABBC\nABBC\nDEEX\nDYZX\nK..I"
        result = parse_board(board_str)
        assert result == ["ABBC", "ABBC", "DEEX", "DYZX", "K..I"]

    def test_parse_board_handles_whitespace(self):
        """Test that parse_board handles extra whitespace."""
        board_str = "  ABBC  ,  ABBC  ,  DEEX  ,  DYZX  ,  K..I  "
        result = parse_board(board_str)
        assert result == ["ABBC", "ABBC", "DEEX", "DYZX", "K..I"]


class TestSolvePuzzle:
    """Tests for solving puzzle configurations.
    
    These tests verify that the solver can find valid solutions for the preset boards.
    Note: These tests may take a few seconds to run as they solve actual puzzles.
    """

    def test_solve_preset_1(self):
        """Test that preset 1 can be solved."""
        initial_board = PRESETS["1"]
        solution = solve_puzzle(initial_board)
        
        assert solution is not None, "Preset 1 should be solvable"
        assert len(solution) > 0, "Solution should have at least one move"
        
        # Verify the final state is a goal state
        final_state = solution[-1][2]
        assert final_state.is_goal(), "Final state should be the goal state"

    def test_solve_preset_2(self):
        """Test that preset 2 can be solved."""
        initial_board = PRESETS["2"]
        solution = solve_puzzle(initial_board)
        
        assert solution is not None, "Preset 2 should be solvable"
        assert len(solution) > 0, "Solution should have at least one move"
        
        # Verify the final state is a goal state
        final_state = solution[-1][2]
        assert final_state.is_goal(), "Final state should be the goal state"

    def test_solve_preset_3(self):
        """Test that preset 3 can be solved."""
        initial_board = PRESETS["3"]
        solution = solve_puzzle(initial_board)
        
        assert solution is not None, "Preset 3 should be solvable"
        assert len(solution) > 0, "Solution should have at least one move"
        
        # Verify the final state is a goal state
        final_state = solution[-1][2]
        assert final_state.is_goal(), "Final state should be the goal state"

    def test_solve_custom_board(self):
        """Test solving a custom board provided as a string."""
        board_str = "ABBC,ABBC,DEEX,DYZX,K..I"
        initial_board = parse_board(board_str)
        solution = solve_puzzle(initial_board)
        
        assert solution is not None, "Custom board should be solvable"
        assert len(solution) > 0, "Solution should have at least one move"

    def test_already_solved_board(self):
        """Test a board that is already in the goal state."""
        # Board with 2x2 piece (BB) already at bottom center
        # Only BB is a 2x2 piece, others are 1x2, 2x1, or 1x1
        goal_board = [
            "ADCC",
            "ADEE",
            "IKFF",
            ".BB.",
            ".BB."
        ]
        solution = solve_puzzle(goal_board)
        
        # Already solved boards return empty list
        assert solution == [], "Already solved board should return empty solution"
