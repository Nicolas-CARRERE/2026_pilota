"""
Tests for CTPB player extraction from resultats.php HTML.

These tests verify that player data is correctly extracted from the HTML structure.
"""

import pytest
from bs4 import BeautifulSoup
from app.services.player_extraction import (
    _parse_players_from_cell,
    _parse_club_name_and_players,
    extract_players_from_html,
    parse_player_line,
    validate_player,
    validate_players,
)


class TestPlayerExtraction:
    """Test player extraction from HTML cells."""

    def test_parse_players_format_license_name(self):
        """Test parsing '(license) Name' format."""
        html = """
        <td>
            <span class="small">
                <li> (061721) MENDIBURU Florian </li>
                <li> (063150) THICOIPE Bittor </li>
            </span>
        </td>
        """
        soup = BeautifulSoup(html, 'html.parser')
        cell = soup.find('td')
        players = _parse_players_from_cell(cell)
        
        assert len(players) == 2
        assert players[0] == {'license': '061721', 'name': 'MENDIBURU Florian'}
        assert players[1] == {'license': '063150', 'name': 'THICOIPE Bittor'}

    def test_parse_players_format_name_license(self):
        """Test parsing 'Name (license)' format."""
        html = """
        <td>
            <li> OLHAGARAY Mathieu (057867) </li>
        </td>
        """
        soup = BeautifulSoup(html, 'html.parser')
        cell = soup.find('td')
        players = _parse_players_from_cell(cell)
        
        assert len(players) == 1
        assert players[0] == {'license': '057867', 'name': 'OLHAGARAY Mathieu'}

    def test_parse_players_with_special_marker(self):
        """Test parsing players with (S) or (E) markers."""
        html = """
        <td>
            <li> BERROGAIN Andde (S) (088069) </li>
        </td>
        """
        soup = BeautifulSoup(html, 'html.parser')
        cell = soup.find('td')
        players = _parse_players_from_cell(cell)
        
        assert len(players) == 1
        assert players[0] == {'license': '088069', 'name': 'BERROGAIN Andde (S)'}

    def test_parse_players_license_only(self):
        """Test parsing license-only format."""
        html = """
        <td>
            <li> 040341 </li>
        </td>
        """
        soup = BeautifulSoup(html, 'html.parser')
        cell = soup.find('td')
        players = _parse_players_from_cell(cell)
        
        assert len(players) == 1
        assert players[0] == {'license': '040341', 'name': ''}

    def test_parse_players_empty_cell(self):
        """Test parsing empty cell."""
        players = _parse_players_from_cell(None)
        assert players == []

    def test_parse_club_name_and_players(self):
        """Test parsing club name and players together."""
        html = """
        <td class="L0" nowrap="">
            U.S.S.P. AMIKUZE
            <span class="small">(01)<br/>
                <li> (061721) MENDIBURU Florian </li>
                <li> (063150) THICOIPE Bittor </li>
            </span>
        </td>
        """
        soup = BeautifulSoup(html, 'html.parser')
        cell = soup.find('td')
        club_name, players = _parse_club_name_and_players(cell)
        
        assert club_name == 'U.S.S.P. AMIKUZE'
        assert len(players) == 2
        assert players[0] == {'license': '061721', 'name': 'MENDIBURU Florian'}
        assert players[1] == {'license': '063150', 'name': 'THICOIPE Bittor'}


class TestPlayerNameParsing:
    """Test player name parsing edge cases."""

    def test_name_with_parentheses_marker(self):
        """Test names with (S) or (E) markers."""
        html = """
        <td>
            <li> ETCHART-SARASOLA Aetz (S) (088068) </li>
        </td>
        """
        soup = BeautifulSoup(html, 'html.parser')
        cell = soup.find('td')
        players = _parse_players_from_cell(cell)
        
        assert len(players) == 1
        assert 'S' in players[0]['name']

    def test_hyphenated_name(self):
        """Test hyphenated player names."""
        html = """
        <td>
            <li> (088068) ETCHART-SARASOLA Aetz </li>
        </td>
        """
        soup = BeautifulSoup(html, 'html.parser')
        cell = soup.find('td')
        players = _parse_players_from_cell(cell)
        
        assert len(players) == 1
        assert players[0]['name'] == 'ETCHART-SARASOLA Aetz'


class TestPlayerExtractionService:
    """Test the player extraction service functions."""

    def test_extract_players_from_html(self):
        """Test extracting players from full HTML."""
        html = """
        <html>
            <body>
                <li> (061721) MENDIBURU Florian </li>
                <li> (063150) THICOIPE Bittor </li>
            </body>
        </html>
        """
        players = extract_players_from_html(html)
        
        assert len(players) == 2
        assert players[0] == {'license': '061721', 'name': 'MENDIBURU Florian'}
        assert players[1] == {'license': '063150', 'name': 'THICOIPE Bittor'}

    def test_parse_player_line_license_name(self):
        """Test parse_player_line with (license) Name format."""
        result = parse_player_line("(061721) MENDIBURU Florian")
        assert result == {'license': '061721', 'name': 'MENDIBURU Florian'}

    def test_parse_player_line_name_license(self):
        """Test parse_player_line with Name (license) format."""
        result = parse_player_line("OLHAGARAY Mathieu (057867)")
        assert result == {'license': '057867', 'name': 'OLHAGARAY Mathieu'}

    def test_parse_player_line_license_only(self):
        """Test parse_player_line with license only."""
        result = parse_player_line("040341")
        assert result == {'license': '040341', 'name': ''}

    def test_parse_player_line_empty(self):
        """Test parse_player_line with empty string."""
        result = parse_player_line("")
        assert result is None

    def test_validate_player_valid(self):
        """Test validate_player with valid data."""
        player = {'license': '061721', 'name': 'MENDIBURU Florian'}
        assert validate_player(player) is True

    def test_validate_player_invalid_license(self):
        """Test validate_player with invalid license format."""
        player = {'license': 'abc123', 'name': 'Test'}
        assert validate_player(player) is False

    def test_validate_player_missing_fields(self):
        """Test validate_player with missing fields."""
        player = {'license': '061721'}
        assert validate_player(player) is False

    def test_validate_players_mixed(self):
        """Test validate_players with mixed valid/invalid data."""
        players = [
            {'license': '061721', 'name': 'MENDIBURU Florian'},
            {'license': 'abc', 'name': 'Invalid'},
            {'license': '063150', 'name': 'THICOIPE Bittor'},
        ]
        valid, invalid_indices = validate_players(players)
        
        assert len(valid) == 2
        assert invalid_indices == [1]
