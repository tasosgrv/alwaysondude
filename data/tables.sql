CREATE TABLE guilds(
    id BIGINT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    chunked BOOLEAN NOT NULL,
    member_count INT NOT NULL,
    owner_id BIGINT NOT NULL,
    prefix CHAR(1) NOT NULL DEFAULT '.',
    earning_rate REAL NOT NULL DEFAULT 0.12,
    drops BOOLEAN NOT NULL DEFAULT TRUE,
    daily_reward REAL NOT NULL DEFAULT 25,
    currency_name VARCHAR(15) NOT NULL DEFAULT 'coins',
    currency_emote VARCHAR(54) NOT NULL DEFAULT ':moneybag:',
)



CREATE TABLE IF NOT EXISTS {table} (
    id BIGINT PRIMARY KEY,
    name VARCHAR(32) NOT NULL,
    discriminator INT NOT NULL,
    bot BOOLEAN NOT NULL,
    nick VARCHAR(32),  
    chunked BOOLEAN NOT NULL,
    points REAL,
    guild_id BIGINT REFERENCES guilds(id) 
    ON DELETE CASCADE,
    dailyreward timestamp
);