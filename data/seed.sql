CREATE TABLE IF NOT EXISTS notebooks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  created_at DATETIME DEFAULT (STRFTIME('%Y-%m-%dT%H:%M:%fZ','now')) NOT NULL,
  updated_at DATETIME DEFAULT (STRFTIME('%Y-%m-%dT%H:%M:%fZ','now')) NOT NULL
);

CREATE TABLE IF NOT EXISTS notes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  notebook_id INTEGER NOT NULL,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  created_at DATETIME DEFAULT (STRFTIME('%Y-%m-%dT%H:%M:%fZ','now')) NOT NULL,
  updated_at DATETIME DEFAULT (STRFTIME('%Y-%m-%dT%H:%M:%fZ','now')) NOT NULL,
  FOREIGN KEY (notebook_id) REFERENCES notebooks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS action_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  note_id INTEGER,
  description TEXT NOT NULL,
  completed BOOLEAN NOT NULL DEFAULT 0,
  created_at DATETIME DEFAULT (STRFTIME('%Y-%m-%dT%H:%M:%fZ','now')) NOT NULL,
  updated_at DATETIME DEFAULT (STRFTIME('%Y-%m-%dT%H:%M:%fZ','now')) NOT NULL,
  FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE
);

INSERT INTO notebooks (name) VALUES
  ('General'),
  ('Work');

INSERT INTO notes (notebook_id, title, content) VALUES
  (1, 'Welcome', 'This is a starter note. TODO: explore the app!'),
  (2, 'Demo', 'Click around and add a note. Ship feature!');

INSERT INTO action_items (note_id, description, completed) VALUES
  (1, 'Try pre-commit', 0),
  (2, 'Run tests', 0);


