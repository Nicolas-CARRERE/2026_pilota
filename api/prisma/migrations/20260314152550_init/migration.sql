-- CreateTable
CREATE TABLE "Modality" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "description" TEXT,

    CONSTRAINT "Modality_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "AgeCategory" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "short_name" TEXT,
    "min_age" INTEGER,
    "max_age" INTEGER,
    "gender" TEXT,
    "description" TEXT,

    CONSTRAINT "AgeCategory_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "CompetitionGender" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "code" VARCHAR(2) NOT NULL,
    "description" TEXT,

    CONSTRAINT "CompetitionGender_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Discipline" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "modality_id" TEXT NOT NULL,
    "gender" TEXT,
    "age_category_id" TEXT,
    "description" TEXT,

    CONSTRAINT "Discipline_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "CompetitionSeries" (
    "id" TEXT NOT NULL,
    "code" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "description" TEXT,
    "competition_type" TEXT NOT NULL,

    CONSTRAINT "CompetitionSeries_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Organizer" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "short_name" TEXT,
    "country" TEXT,
    "type" TEXT NOT NULL,
    "founded_year" INTEGER,
    "website" TEXT,
    "is_active" BOOLEAN NOT NULL DEFAULT true,

    CONSTRAINT "Organizer_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "CompetitionYear" (
    "id" TEXT NOT NULL,
    "year" INTEGER NOT NULL,
    "is_current" BOOLEAN NOT NULL DEFAULT false,

    CONSTRAINT "CompetitionYear_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Club" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "short_name" TEXT,
    "country" TEXT,
    "region" TEXT,
    "founded_year" INTEGER,
    "website" TEXT,
    "is_active" BOOLEAN NOT NULL DEFAULT true,

    CONSTRAINT "Club_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Player" (
    "id" TEXT NOT NULL,
    "first_name" TEXT NOT NULL,
    "last_name" TEXT NOT NULL,
    "nickname" TEXT,
    "license" VARCHAR(32),
    "birth_date" DATE,
    "country" TEXT,
    "height_cm" INTEGER,
    "weight_kg" INTEGER,
    "dominant_hand" TEXT,
    "is_active" BOOLEAN NOT NULL DEFAULT true,

    CONSTRAINT "Player_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "PlayerClubHistory" (
    "id" TEXT NOT NULL,
    "player_id" TEXT NOT NULL,
    "club_id" TEXT NOT NULL,
    "joined_date" DATE NOT NULL,
    "left_date" DATE,
    "note" TEXT,

    CONSTRAINT "PlayerClubHistory_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Team" (
    "id" TEXT NOT NULL,
    "club_id" TEXT,
    "name" TEXT NOT NULL,
    "short_name" TEXT,
    "discipline_id" TEXT NOT NULL,
    "is_professional" BOOLEAN NOT NULL DEFAULT false,

    CONSTRAINT "Team_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "TeamPlayer" (
    "team_id" TEXT NOT NULL,
    "player_id" TEXT NOT NULL,
    "role" TEXT,

    CONSTRAINT "TeamPlayer_pkey" PRIMARY KEY ("team_id","player_id")
);

-- CreateTable
CREATE TABLE "Competition" (
    "id" TEXT NOT NULL,
    "series_id" TEXT,
    "discipline_id" TEXT NOT NULL,
    "year_id" TEXT NOT NULL,
    "organizer_id" TEXT NOT NULL,
    "age_category_id" TEXT,
    "gender_id" TEXT,
    "start_date" DATE NOT NULL,
    "end_date" DATE,
    "location" TEXT,
    "country" TEXT,
    "status" TEXT NOT NULL,
    "phase" TEXT,

    CONSTRAINT "Competition_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Court" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "city" TEXT NOT NULL,
    "country" TEXT NOT NULL,
    "court_type" TEXT NOT NULL,

    CONSTRAINT "Court_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Game" (
    "id" TEXT NOT NULL,
    "competition_id" TEXT NOT NULL,
    "series_id" TEXT,
    "court_id" TEXT,
    "player1_id" TEXT NOT NULL,
    "player2_id" TEXT NOT NULL,
    "start_date" DATE NOT NULL,
    "end_date" DATE,
    "winner_id" TEXT,
    "status" TEXT NOT NULL,
    "notes" TEXT,
    "source_id" TEXT,
    "external_id" TEXT,
    "scraped_from_url" TEXT,
    "score_complete" BOOLEAN,

    CONSTRAINT "Game_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "GameSidePlayer" (
    "game_id" TEXT NOT NULL,
    "player_id" TEXT NOT NULL,
    "side" INTEGER NOT NULL,
    "display_order" INTEGER,

    CONSTRAINT "GameSidePlayer_pkey" PRIMARY KEY ("game_id","player_id","side")
);

-- CreateTable
CREATE TABLE "GameScore" (
    "id" TEXT NOT NULL,
    "game_id" TEXT NOT NULL,
    "raw_score" VARCHAR(50) NOT NULL,
    "score_sets_player1" INTEGER,
    "score_sets_player2" INTEGER,
    "score_games_set1_player1" INTEGER DEFAULT 0,
    "score_games_set1_player2" INTEGER DEFAULT 0,
    "score_games_set2_player1" INTEGER DEFAULT 0,
    "score_games_set2_player2" INTEGER DEFAULT 0,
    "score_points_set3_player1" INTEGER DEFAULT 0,
    "score_points_set3_player2" INTEGER DEFAULT 0,

    CONSTRAINT "GameScore_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "PlayerStat" (
    "id" TEXT NOT NULL,
    "player_id" TEXT NOT NULL,
    "game_id" TEXT NOT NULL,
    "shots_total" INTEGER NOT NULL DEFAULT 0,
    "shots_won" INTEGER NOT NULL DEFAULT 0,
    "shots_unforced_errors" INTEGER NOT NULL DEFAULT 0,
    "forced_errors" INTEGER NOT NULL DEFAULT 0,
    "volleyes_total" INTEGER NOT NULL DEFAULT 0,
    "volleyes_won" INTEGER NOT NULL DEFAULT 0,
    "smashes_total" INTEGER NOT NULL DEFAULT 0,
    "smashes_won" INTEGER NOT NULL DEFAULT 0,
    "volleys_unforced_errors" INTEGER NOT NULL DEFAULT 0,
    "net_points_lost" INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT "PlayerStat_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Source" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "url" TEXT,
    "country" TEXT,
    "organizer_id" TEXT,
    "is_active" BOOLEAN NOT NULL DEFAULT true,
    "last_scraped" TIMESTAMP(3),
    "last_successful_scrape" TIMESTAMP(3),
    "scrape_frequency" TEXT,

    CONSTRAINT "Source_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ScrapedFilterOption" (
    "id" TEXT NOT NULL,
    "source_id" TEXT NOT NULL,
    "kind" TEXT NOT NULL,
    "value" TEXT NOT NULL,
    "label" TEXT NOT NULL,

    CONSTRAINT "ScrapedFilterOption_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ScrapedSpecialty" (
    "id" TEXT NOT NULL,
    "source_id" TEXT NOT NULL,
    "competition_option_id" TEXT NOT NULL,
    "value" TEXT NOT NULL,
    "label" TEXT NOT NULL,

    CONSTRAINT "ScrapedSpecialty_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ScrapingJobRun" (
    "id" TEXT NOT NULL,
    "source_id" TEXT NOT NULL,
    "url" TEXT NOT NULL,
    "start_time" TIMESTAMP(3) NOT NULL,
    "end_time" TIMESTAMP(3),
    "status" TEXT NOT NULL,
    "raw_content" TEXT,
    "errors_count" INTEGER NOT NULL DEFAULT 0,
    "logs" TEXT,

    CONSTRAINT "ScrapingJobRun_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "CompetitionSeries_code_key" ON "CompetitionSeries"("code");

-- CreateIndex
CREATE UNIQUE INDEX "ScrapedFilterOption_source_id_kind_value_key" ON "ScrapedFilterOption"("source_id", "kind", "value");

-- CreateIndex
CREATE UNIQUE INDEX "ScrapedSpecialty_source_id_competition_option_id_value_key" ON "ScrapedSpecialty"("source_id", "competition_option_id", "value");

-- AddForeignKey
ALTER TABLE "Discipline" ADD CONSTRAINT "Discipline_modality_id_fkey" FOREIGN KEY ("modality_id") REFERENCES "Modality"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Discipline" ADD CONSTRAINT "Discipline_age_category_id_fkey" FOREIGN KEY ("age_category_id") REFERENCES "AgeCategory"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "PlayerClubHistory" ADD CONSTRAINT "PlayerClubHistory_player_id_fkey" FOREIGN KEY ("player_id") REFERENCES "Player"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "PlayerClubHistory" ADD CONSTRAINT "PlayerClubHistory_club_id_fkey" FOREIGN KEY ("club_id") REFERENCES "Club"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Team" ADD CONSTRAINT "Team_club_id_fkey" FOREIGN KEY ("club_id") REFERENCES "Club"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Team" ADD CONSTRAINT "Team_discipline_id_fkey" FOREIGN KEY ("discipline_id") REFERENCES "Discipline"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "TeamPlayer" ADD CONSTRAINT "TeamPlayer_team_id_fkey" FOREIGN KEY ("team_id") REFERENCES "Team"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "TeamPlayer" ADD CONSTRAINT "TeamPlayer_player_id_fkey" FOREIGN KEY ("player_id") REFERENCES "Player"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Competition" ADD CONSTRAINT "Competition_series_id_fkey" FOREIGN KEY ("series_id") REFERENCES "CompetitionSeries"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Competition" ADD CONSTRAINT "Competition_discipline_id_fkey" FOREIGN KEY ("discipline_id") REFERENCES "Discipline"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Competition" ADD CONSTRAINT "Competition_year_id_fkey" FOREIGN KEY ("year_id") REFERENCES "CompetitionYear"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Competition" ADD CONSTRAINT "Competition_organizer_id_fkey" FOREIGN KEY ("organizer_id") REFERENCES "Organizer"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Competition" ADD CONSTRAINT "Competition_age_category_id_fkey" FOREIGN KEY ("age_category_id") REFERENCES "AgeCategory"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Competition" ADD CONSTRAINT "Competition_gender_id_fkey" FOREIGN KEY ("gender_id") REFERENCES "CompetitionGender"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Game" ADD CONSTRAINT "Game_competition_id_fkey" FOREIGN KEY ("competition_id") REFERENCES "Competition"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Game" ADD CONSTRAINT "Game_court_id_fkey" FOREIGN KEY ("court_id") REFERENCES "Court"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Game" ADD CONSTRAINT "Game_player1_id_fkey" FOREIGN KEY ("player1_id") REFERENCES "Player"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Game" ADD CONSTRAINT "Game_player2_id_fkey" FOREIGN KEY ("player2_id") REFERENCES "Player"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Game" ADD CONSTRAINT "Game_winner_id_fkey" FOREIGN KEY ("winner_id") REFERENCES "Player"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Game" ADD CONSTRAINT "Game_source_id_fkey" FOREIGN KEY ("source_id") REFERENCES "Source"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "GameSidePlayer" ADD CONSTRAINT "GameSidePlayer_game_id_fkey" FOREIGN KEY ("game_id") REFERENCES "Game"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "GameSidePlayer" ADD CONSTRAINT "GameSidePlayer_player_id_fkey" FOREIGN KEY ("player_id") REFERENCES "Player"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "GameScore" ADD CONSTRAINT "GameScore_game_id_fkey" FOREIGN KEY ("game_id") REFERENCES "Game"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "PlayerStat" ADD CONSTRAINT "PlayerStat_player_id_fkey" FOREIGN KEY ("player_id") REFERENCES "Player"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "PlayerStat" ADD CONSTRAINT "PlayerStat_game_id_fkey" FOREIGN KEY ("game_id") REFERENCES "Game"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ScrapedFilterOption" ADD CONSTRAINT "ScrapedFilterOption_source_id_fkey" FOREIGN KEY ("source_id") REFERENCES "Source"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ScrapedSpecialty" ADD CONSTRAINT "ScrapedSpecialty_source_id_fkey" FOREIGN KEY ("source_id") REFERENCES "Source"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ScrapedSpecialty" ADD CONSTRAINT "ScrapedSpecialty_competition_option_id_fkey" FOREIGN KEY ("competition_option_id") REFERENCES "ScrapedFilterOption"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ScrapingJobRun" ADD CONSTRAINT "ScrapingJobRun_source_id_fkey" FOREIGN KEY ("source_id") REFERENCES "Source"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
