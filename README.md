# LOL 10-Minute Data Collection

This project collects League of Legends match data from the Riot Games API, focusing on the first 10 minutes of each game. The collected data is stored in a MySQL database and can be used for analysis or machine learning tasks such as early-game win prediction.

The main script for the current workflow is `match_crawler.py`.

## What the Collector Does

`match_crawler.py` starts from one seed Match ID, fetches match and timeline data from Riot API, saves valid matches into MySQL, then discovers more matches by sampling player PUUIDs from processed games.

The collector stores:

- Champions for all 10 players
- Patch, game mode, and game duration
- Blue/Red team win result
- Team objectives during the first 10 minutes, including kills, dragons, rift herald/voidgrubs, and towers
- Player stats at minute 10, including CS, gold, damage dealt, and damage taken
- KDA events from the first 10 minutes
- Items, summoner spells, runes, lane, and enemy lane champion

The current crawler only saves matches from these patches:

```python
("16.4", "16.04", "16.5", "16.05", "16.6", "16.06")
```

## Repository Files

Required files for running the crawler:

- `match_crawler.py` - main crawler script
- `config.py` - local Riot API key file, created manually and ignored by Git
- `databaseQuries.py` - database helper functions from the original project structure
- `RiotApiCalls.py` - Riot API helper functions from the original project structure
- `championsRequest.py` - champion, item, and rune helper functions from the original project structure
- `TableSetupNoData.txt` - SQL script for creating the database schema and seed lookup data

Optional files:

- `export_csv.py` - exports MySQL tables to CSV files
- `ItemsGen.py` - helper script for generating item data
- `DataCollection.py` and `collect_summoners.py` - older collection pipeline from the original project, not the main workflow in this version

## Requirements

- Python 3.10+
- MySQL Server
- Riot Games API key
- Python packages:

```bash
pip install requests mysql-connector-python pandas
```

`pandas` is still listed because some imported helper files require it, even though `match_crawler.py` does not directly use it.

## Setup

### 1. Create a Riot API Config File

Create a file named `config.py` in the project root:

```python
api_key = "RGAPI-your-api-key-here"
```

Do not commit `config.py` to GitHub. It contains your Riot API key and should stay local.

The `.gitignore` should include:

```gitignore
config.py
.env
venv/
__pycache__/
*.pyc
.ipynb_checkpoints/
```

### 2. Install Python Dependencies

Optional virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install requests mysql-connector-python pandas
```

### 3. Database Setup

The crawler expects a MySQL database named `LeagueStats` and a MySQL user matching the credentials currently hardcoded in `match_crawler.py`:

```python
config = {
    "user": "league_user",
    "password": "mysql",
    "host": "localhost",
    "port": 3306,
    "database": "LeagueStats",
    "buffered": True,
    "auth_plugin": "mysql_native_password",
}
```

Run the database schema script as a MySQL admin/root user:

```bash
mysql -u root -p < TableSetupNoData.txt
```

This creates:

- `LeagueStats` database
- Core tables used by the crawler
- Lookup/seed data for ranks, champions, items, keystones, and summoner spells

Then create the MySQL user used by the Python scripts:

```bash
mysql -u root -p
```

Inside the MySQL shell:

```sql
CREATE USER IF NOT EXISTS 'league_user'@'localhost' IDENTIFIED BY 'mysql';
GRANT ALL PRIVILEGES ON LeagueStats.* TO 'league_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

Verify that the crawler user can access the database:

```bash
mysql -u league_user -pmysql LeagueStats
```

Useful verification queries:

```sql
SHOW TABLES;
SELECT COUNT(*) FROM ChampionTbl;
SELECT COUNT(*) FROM ItemTbl;
SELECT COUNT(*) FROM RankTbl;
```

### 4. Choose a Starting Match ID

Edit the seed Match ID at the bottom of `match_crawler.py`:

```python
if __name__ == "__main__":
    crawl_pipeline("SG2_139856327")
```

Replace `"SG2_139856327"` with the match ID you want to start from.

### 5. Run the Crawler

```bash
python match_crawler.py
```

If Riot API rate limits the request, the crawler sleeps and retries the same match.

## Database Tables

Main tables written by the crawler:

- `MatchTbl` - Match ID, patch, queue type, rank ID, and game duration
- `TeamMatchTbl` - Blue/Red champion composition and team objectives from the first 10 minutes
- `SummonerUserTbl` - Summoner names
- `SummonerMatchTbl` - Relationship between summoners, matches, and champions
- `MatchStatsTbl` - Player-level minute-10 stats and first-10-minute event stats

Lookup tables:

- `ChampionTbl` - Champion ID and champion name
- `ItemTbl` - Item ID and item name
- `KeystoneTbl` - Rune keystone ID, keystone name, and tree name
- `RankTbl` - Rank ID and rank name
- `SummonerSpellTbl` - Summoner spell ID and spell name

## Data Fields

`TeamMatchTbl` stores one row per match with:

- Blue and Red team champion IDs
- Blue/Red kills
- Blue/Red dragons
- Blue/Red rift herald or voidgrub count
- Blue/Red tower kills
- Blue/Red win result

`MatchStatsTbl` stores one row per player per match with:

- CS at minute 10
- Damage dealt and damage taken at minute 10
- Total gold at minute 10
- Lane and inferred support role
- Win result
- Items, summoner spells, and runes
- Kills, deaths, assists during the first 10 minutes
- Dragon and baron kills during the first 10 minutes
- Enemy lane champion
- Vision score

## Export Data to CSV

To export tables from MySQL into CSV files:

```bash
python export_csv.py
```

CSV files are written to:

```text
League_CSV_Export/
```

## Notes and Limitations

- The crawler currently uses `sea.api.riotgames.com` and is configured around `SG2_...` match IDs.
- Most values in `MatchStatsTbl` are based on the first 10 minutes, but `visionScore` currently comes from the full match summary.
- `TurretDmgDealt` is currently saved as `0`.
- `RankFk` is currently fixed as `1` in `match_crawler.py`.
- Support role is inferred from champion ID and CS because Riot API often reports both bot-lane players as `BOTTOM`.
- Riot development API keys expire, so `config.py` may need to be updated regularly.

## Riot Games API Notice

This project uses the Riot Games API. This project is not endorsed by Riot Games and does not reflect the views or opinions of Riot Games or anyone officially involved in producing or managing Riot Games properties.
