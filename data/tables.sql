



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
)