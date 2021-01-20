CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(255) UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE user_posts (
    user_id INTEGER NOT NULL,
    post_id INTEGER UNIQUE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (post_id) REFERENCES post (id)
);

CREATE TABLE post (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    tag_id INTEGER NOT NULL,
    FOREIGN KEY (author_id) REFERENCES user (id),
    FOREIGN KEY (tag_id) REFERENCES tags (id)
);

CREATE TABLE post_tags (
    post_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    FOREIGN KEY (post_id) REFERENCES post (id),
    FOREIGN KEY (tag_id) REFERENCES tags (id)
);

CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT UNIQUE NOT NULL
);

CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER NOT NULL,
    sent TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    body TEXT NOT NULL,
    sender_id INTEGER NOT NULL,
    FOREIGN KEY (chat_id) REFERENCES chat (id),
    FOREIGN KEY (sender_id) REFERENCES user (id)
);

CREATE TABLE user_chats (
    user_id INTEGER NOT NULL,
    chat_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (chat_id) REFERENCES chat (id)
);

CREATE TABLE chat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user1_id INTEGER NOT NULL,
    user2_id INTEGER NOT NULL,
    FOREIGN KEY (user1_id) REFERENCES user (id),
    FOREIGN KEY (user2_id) REFERENCES user (id)
);
