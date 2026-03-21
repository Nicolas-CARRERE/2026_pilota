#!/usr/bin/env python3
"""
Ingest scraped CTPB games with player data into PostgreSQL database.
"""

import json
import psycopg2
from datetime import datetime
from typing import Dict, List, Optional
import uuid

# DB config
DB_HOST = "51.210.97.147"
DB_PORT = 5532
DB_NAME = "2k26_pilota_bot"
DB_USER = "postgres"
DB_PASSWORD = "1bba97d121d71d2e"


def get_db_connection():
    """Connect to PostgreSQL."""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse DD/MM/YYYY date string."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%d/%m/%Y")
    except ValueError:
        return None


def normalize_status(raw_score: str) -> str:
    """Infer game status from raw score."""
    s = (raw_score or "").strip()
    if not s:
        return "scheduled"
    if "FG" in s.upper():
        return "forfait"
    if "/P" in s or "P/" in s:
        return "incomplete"
    if s.count("/") >= 1:
        return "completed"
    return "scheduled"


def get_or_create_club(conn, club_name: str, short_name: Optional[str] = None) -> str:
    """Get existing club or create new one, return club ID."""
    if not club_name:
        club_name = "Unknown Club"
    
    with conn.cursor() as cur:
        cur.execute('SELECT id FROM "Club" WHERE name = %s', (club_name,))
        row = cur.fetchone()
        if row:
            return row[0]
        
        club_id = str(uuid.uuid4())
        cur.execute('''
            INSERT INTO "Club" (id, name, short_name, country, region, is_active)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (club_id, club_name, short_name, "France", "Pays Basque", True))
        conn.commit()
        return club_id


def get_or_create_discipline(conn, discipline_name: str) -> str:
    """Get existing discipline or create new one, return discipline ID."""
    if not discipline_name:
        discipline_name = "Unknown"
    
    with conn.cursor() as cur:
        cur.execute('SELECT id FROM "Discipline" WHERE name = %s', (discipline_name,))
        row = cur.fetchone()
        if row:
            return row[0]
        
        modality_id = get_or_create_modality(conn, "Pelote Basque")
        discipline_id = str(uuid.uuid4())
        cur.execute('''
            INSERT INTO "Discipline" (id, name, modality_id, description)
            VALUES (%s, %s, %s, %s)
        ''', (discipline_id, discipline_name, modality_id, None))
        conn.commit()
        return discipline_id


def get_or_create_modality(conn, modality_name: str) -> str:
    """Get existing modality or create new one, return modality ID."""
    with conn.cursor() as cur:
        cur.execute('SELECT id FROM "Modality" WHERE name = %s', (modality_name,))
        row = cur.fetchone()
        if row:
            return row[0]
        
        modality_id = str(uuid.uuid4())
        cur.execute('''
            INSERT INTO "Modality" (id, name, description)
            VALUES (%s, %s, %s)
        ''', (modality_id, modality_name, "Basque Pelota"))
        conn.commit()
        return modality_id


def get_or_create_organizer(conn, organizer_name: str) -> str:
    """Get existing organizer or create new one, return organizer ID."""
    with conn.cursor() as cur:
        cur.execute('SELECT id FROM "Organizer" WHERE name = %s', (organizer_name,))
        row = cur.fetchone()
        if row:
            return row[0]
        
        organizer_id = str(uuid.uuid4())
        cur.execute('''
            INSERT INTO "Organizer" (id, name, short_name, type, is_active)
            VALUES (%s, %s, %s, %s, %s)
        ''', (organizer_id, organizer_name, "CTPB", "committee", True))
        conn.commit()
        return organizer_id


def get_or_create_competition_year(conn, year: int) -> str:
    """Get existing competition year or create new one."""
    with conn.cursor() as cur:
        cur.execute('SELECT id FROM "CompetitionYear" WHERE year = %s', (year,))
        row = cur.fetchone()
        if row:
            return row[0]
        
        year_id = str(uuid.uuid4())
        cur.execute('''
            INSERT INTO "CompetitionYear" (id, year, is_current)
            VALUES (%s, %s, %s)
        ''', (year_id, year, False))
        conn.commit()
        return year_id


def get_or_create_competition(conn, competition_name: str, year: int) -> str:
    """Get existing competition or create new one, return competition ID."""
    organizer_id = get_or_create_organizer(conn, "CTPB")
    year_id = get_or_create_competition_year(conn, year)
    discipline_id = get_or_create_discipline(conn, "Championnat")
    
    competition_id = str(uuid.uuid4())
    with conn.cursor() as cur:
        cur.execute('''
            INSERT INTO "Competition" (
                id, series_id, discipline_id, year_id, organizer_id,
                start_date, end_date, status, country
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            competition_id, None, discipline_id, year_id, organizer_id,
            datetime(year, 1, 1), datetime(year, 12, 31), "completed", "France"
        ))
        conn.commit()
        return competition_id


def get_or_create_court(conn, venue: Optional[str], city: str = "Pays Basque") -> Optional[str]:
    """Get existing court or create new one, return court ID."""
    if not venue:
        return None
    
    with conn.cursor() as cur:
        cur.execute('SELECT id FROM "Court" WHERE name = %s', (venue,))
        row = cur.fetchone()
        if row:
            return row[0]
        
        court_id = str(uuid.uuid4())
        court_type = "fronton"
        cur.execute('''
            INSERT INTO "Court" (id, name, city, country, court_type)
            VALUES (%s, %s, %s, %s, %s)
        ''', (court_id, venue, city, "France", court_type))
        conn.commit()
        return court_id


def get_or_create_player(conn, license_id: str, first_name: str, last_name: str) -> str:
    """Get existing player by license or create new one."""
    with conn.cursor() as cur:
        # Try to find by license
        cur.execute('SELECT id FROM "Player" WHERE license = %s', (license_id,))
        row = cur.fetchone()
        if row:
            return row[0]
        
        # Create new player
        player_id = str(uuid.uuid4())
        cur.execute('''
            INSERT INTO "Player" (id, first_name, last_name, license, is_active)
            VALUES (%s, %s, %s, %s, %s)
        ''', (player_id, first_name, last_name, license_id, True))
        conn.commit()
        return player_id


def get_or_create_team(conn, club_id: str, discipline_id: str) -> str:
    """Get existing team or create new one for a club."""
    with conn.cursor() as cur:
        cur.execute('SELECT id FROM "Team" WHERE club_id = %s AND discipline_id = %s', (club_id, discipline_id))
        row = cur.fetchone()
        if row:
            return row[0]
        
        team_id = str(uuid.uuid4())
        cur.execute('''
            INSERT INTO "Team" (id, club_id, name, discipline_id)
            VALUES (%s, %s, %s, %s)
        ''', (team_id, club_id, "Team", discipline_id))
        conn.commit()
        return team_id


def ingest_game(conn, game_data: Dict, source_id: str, competition_id: str, discipline_id: str) -> str:
    """Ingest a single game into DB with player data, return game ID."""
    with conn.cursor() as cur:
        # Get or create clubs
        club1_id = get_or_create_club(conn, game_data.get('club1_name', 'Unknown'))
        club2_id = get_or_create_club(conn, game_data.get('club2_name', 'Unknown'))
        
        # Get or create teams
        team1_id = get_or_create_team(conn, club1_id, discipline_id)
        team2_id = get_or_create_team(conn, club2_id, discipline_id)
        
        # Parse date
        game_date = parse_date(game_data.get('date', ''))
        
        # Get or create court
        court_id = get_or_create_court(conn, None)
        
        # Create players with real data
        club1_players = game_data.get('club1_players', [])
        club2_players = game_data.get('club2_players', [])
        
        # Get first player from each team (or create unknown)
        if club1_players and len(club1_players) > 0:
            p1 = club1_players[0]
            # Parse name: "MENDIBURU Florian" -> first_name="Florian", last_name="MENDIBURU"
            name_parts = p1['name'].replace('(S)', '').replace('(E)', '').strip().split()
            if len(name_parts) >= 2:
                last_name = name_parts[-1]
                first_name = " ".join(name_parts[:-1])
            else:
                last_name = name_parts[0] if name_parts else "Unknown"
                first_name = "Unknown"
            player1_id = get_or_create_player(conn, p1['license'], first_name, last_name)
        else:
            player1_id = get_or_create_player(conn, "UNK1", "Unknown", "Player1")
        
        if club2_players and len(club2_players) > 0:
            p2 = club2_players[0]
            name_parts = p2['name'].replace('(S)', '').replace('(E)', '').strip().split()
            if len(name_parts) >= 2:
                last_name = name_parts[-1]
                first_name = " ".join(name_parts[:-1])
            else:
                last_name = name_parts[0] if name_parts else "Unknown"
                first_name = "Unknown"
            player2_id = get_or_create_player(conn, p2['license'], first_name, last_name)
        else:
            player2_id = get_or_create_player(conn, "UNK2", "Unknown", "Player2")
        
        # Create game
        game_id = str(uuid.uuid4())
        status = normalize_status(game_data.get('raw_score', ''))
        external_id = game_data.get('no_renc')
        
        cur.execute('''
            INSERT INTO "Game" (
                id, competition_id, court_id, player1_id, player2_id,
                start_date, status, source_id, external_id,
                score_complete, phase
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            game_id, competition_id, court_id, player1_id, player2_id,
            game_date, status, source_id, external_id,
            game_data.get('raw_score') is not None, None
        ))
        
        # Create game score
        score_id = str(uuid.uuid4())
        raw_score = game_data.get('raw_score', '')
        cur.execute('''
            INSERT INTO "GameScore" (id, game_id, raw_score)
            VALUES (%s, %s, %s)
        ''', (score_id, game_id, raw_score))
        
        # Create game side players (all players from both teams)
        for idx, player_data in enumerate(club1_players):
            name_parts = player_data['name'].replace('(S)', '').replace('(E)', '').strip().split()
            if len(name_parts) >= 2:
                last_name = name_parts[-1]
                first_name = " ".join(name_parts[:-1])
            else:
                last_name = name_parts[0] if name_parts else "Unknown"
                first_name = "Unknown"
            
            player_id = get_or_create_player(conn, player_data['license'], first_name, last_name)
            cur.execute('''
                INSERT INTO "GameSidePlayer" (game_id, player_id, side, display_order)
                VALUES (%s, %s, %s, %s)
            ''', (game_id, player_id, 1, idx + 1))
        
        for idx, player_data in enumerate(club2_players):
            name_parts = player_data['name'].replace('(S)', '').replace('(E)', '').strip().split()
            if len(name_parts) >= 2:
                last_name = name_parts[-1]
                first_name = " ".join(name_parts[:-1])
            else:
                last_name = name_parts[0] if name_parts else "Unknown"
                first_name = "Unknown"
            
            player_id = get_or_create_player(conn, player_data['license'], first_name, last_name)
            cur.execute('''
                INSERT INTO "GameSidePlayer" (game_id, player_id, side, display_order)
                VALUES (%s, %s, %s, %s)
            ''', (game_id, player_id, 2, idx + 1))
        
        conn.commit()
        return game_id


def ingest_games_from_json(json_file: str, source_name: str, competition_year: int) -> int:
    """Ingest games from JSON file into DB."""
    with open(json_file, 'r') as f:
        games = json.load(f)
    
    conn = get_db_connection()
    source_id = get_or_create_source(conn, source_name)
    competition_id = get_or_create_competition(conn, source_name, competition_year)
    discipline_id = get_or_create_discipline(conn, "Main Nue")
    
    ingested_count = 0
    for i, game in enumerate(games):
        try:
            ingest_game(conn, game, source_id, competition_id, discipline_id)
            ingested_count += 1
            if (i + 1) % 100 == 0:
                print(f"  Ingested {i + 1}/{len(games)} games...")
        except Exception as e:
            print(f"  Error ingesting game {i}: {e}")
            continue
    
    conn.close()
    return ingested_count


def get_or_create_source(conn, source_name: str) -> str:
    """Get existing source or create new one."""
    with conn.cursor() as cur:
        cur.execute('SELECT id FROM "Source" WHERE name = %s', (source_name,))
        row = cur.fetchone()
        if row:
            return row[0]
        
        source_id = str(uuid.uuid4())
        cur.execute('''
            INSERT INTO "Source" (id, name, url, country, is_active)
            VALUES (%s, %s, %s, %s, %s)
        ''', (source_id, source_name, "https://ctpb.euskalpilota.fr", "France", True))
        conn.commit()
        return source_id


if __name__ == "__main__":
    print("Starting ingestion with player data...")
    
    # Ingest Competition: Championnat été 2025 (Main Nue specialty)
    print("\n=== Ingesting: Championnat été 2025 (Main Nue) ===")
    count = ingest_games_from_json('/tmp/comp_20250102_spec11.json', 'CTPB été 2025 Main Nue', 2025)
    print(f"✅ Ingested {count} games with players")
    
    print(f"\n🎉 Total ingested: {count} games")
