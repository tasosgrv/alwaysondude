CREATE TABLE IF NOT EXISTS guilds (
    id BIGINT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    chunked BOOLEAN NOT NULL, 
    member_count INT NOT NULL, 
    owner_id BIGINT NOT NULL
);

CREATE TABLE IF NOT EXISTS members (
    id BIGINT PRIMARY KEY,
    name VARCHAR(32) NOT NULL,
    discriminator INT NOT NULL,
    bot BOOLEAN NOT NULL,
    nick VARCHAR(32),  
    chunked BOOLEAN NOT NULL,
    points INT,
    guild_id BIGINT REFERENCES guilds(id) 
    ON DELETE CASCADE
);
