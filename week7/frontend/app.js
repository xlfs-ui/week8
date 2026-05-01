async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) {
    const message = await res.text();
    throw new Error(message || 'Request failed');
  }
  if (res.status === 204) return null;
  const raw = await res.text();
  return raw ? JSON.parse(raw) : null;
}

function showError(error) {
  const message = error instanceof Error ? error.message : String(error);
  alert(message);
}

function fillNotebookSelect(notebooks) {
  const select = document.getElementById('note-notebook');
  if (!select) return;
  select.innerHTML = '';
  for (const nb of notebooks) {
    const option = document.createElement('option');
    option.value = String(nb.id);
    option.textContent = nb.name;
    select.appendChild(option);
  }
}

function fillActionNoteSelect(notes) {
  const select = document.getElementById('action-note');
  if (!select) return;
  select.innerHTML = '';
  const unbound = document.createElement('option');
  unbound.value = '';
  unbound.textContent = 'Unlinked action item';
  select.appendChild(unbound);
  for (const note of notes) {
    const option = document.createElement('option');
    option.value = String(note.id);
    option.textContent = `${note.title}`;
    select.appendChild(option);
  }
}

async function loadNotebooks() {
  const list = document.getElementById('notebooks');
  list.innerHTML = '';
  const notebooks = await fetchJSON('/notebooks/');
  if (!Array.isArray(notebooks)) {
    throw new Error('Invalid notebooks response from server');
  }
  for (const nb of notebooks) {
    const li = document.createElement('li');
    li.textContent = `${nb.name} (#${nb.id})`;
    list.appendChild(li);
  }
  fillNotebookSelect(notebooks);
  return notebooks;
}

async function loadNotes(params = {}) {
  const list = document.getElementById('notes');
  list.innerHTML = '';
  const query = new URLSearchParams(params);
  const notes = await fetchJSON('/notes/?' + query.toString());
  if (!Array.isArray(notes)) {
    throw new Error('Invalid notes response from server');
  }
  for (const n of notes) {
    const noteId = n.id ?? n.note_id;
    if (noteId === undefined || noteId === null) continue;
    const li = document.createElement('li');
    const text = document.createElement('span');
    text.textContent = `[Notebook #${n.notebook_id}] ${n.title ?? ''}: ${n.content ?? ''} `;
    li.appendChild(text);

    const editBtn = document.createElement('button');
    editBtn.textContent = 'update';
    editBtn.onclick = async () => {
      const title = prompt('new title', n.title ?? '');
      if (title === null) return;
      const content = prompt('new content', n.content ?? '');
      if (content === null) return;
      try {
        await fetchJSON(`/notes/${noteId}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title, content }),
        });
        await loadNotes(params);
      } catch (error) {
        showError(error);
      }
    };
    li.appendChild(editBtn);

    const deleteBtn = document.createElement('button');
    deleteBtn.textContent = 'delete';
    deleteBtn.onclick = async () => {
      if (!confirm('confirm delete this note?')) return;
      try {
        await fetchJSON(`/notes/${noteId}`, { method: 'DELETE' });
        await loadNotes(params);
      } catch (error) {
        showError(error);
      }
    };
    li.appendChild(deleteBtn);
    list.appendChild(li);
  }
  fillActionNoteSelect(notes);
  return notes;
}

async function loadActions(params = {}) {
  const list = document.getElementById('actions');
  list.innerHTML = '';
  const query = new URLSearchParams(params);
  const items = await fetchJSON('/action-items/?' + query.toString());
  for (const a of items) {
    const li = document.createElement('li');
    const relationText = a.note_id ? ` note#${a.note_id}` : ' unlinked';
    li.textContent = `${a.description} [${a.completed ? 'done' : 'open'} |${relationText}]`;
    if (!a.completed) {
      const btn = document.createElement('button');
      btn.textContent = 'Complete';
      btn.onclick = async () => {
        try {
          await fetchJSON(`/action-items/${a.id}/complete`, { method: 'PUT' });
          await loadActions(params);
        } catch (error) {
          showError(error);
        }
      };
      li.appendChild(btn);
    } else {
      const btn = document.createElement('button');
      btn.textContent = 'Reopen';
      btn.onclick = async () => {
        try {
          await fetchJSON(`/action-items/${a.id}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ completed: false }),
          });
          await loadActions(params);
        } catch (error) {
          showError(error);
        }
      };
      li.appendChild(btn);
    }
    list.appendChild(li);
  }
}

window.addEventListener('DOMContentLoaded', () => {
  document.getElementById('notebook-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('notebook-name').value;
    try {
      await fetchJSON('/notebooks/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name }),
      });
      e.target.reset();
      await loadNotebooks();
    } catch (error) {
      showError(error);
    }
  });

  document.getElementById('note-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const notebookId = document.getElementById('note-notebook').value;
    const title = document.getElementById('note-title').value;
    const content = document.getElementById('note-content').value;
    try {
      await fetchJSON('/notes/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, content, notebook_id: Number(notebookId) || null }),
      });
      e.target.reset();
      await loadNotes();
    } catch (error) {
      showError(error);
    }
  });

  document.getElementById('note-search-btn').addEventListener('click', async () => {
    const q = document.getElementById('note-search').value;
    loadNotes({ q });
  });

  document.getElementById('action-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const noteId = document.getElementById('action-note').value;
    const description = document.getElementById('action-desc').value;
    try {
      await fetchJSON('/action-items/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description, note_id: noteId ? Number(noteId) : null }),
      });
      e.target.reset();
      await loadActions();
    } catch (error) {
      showError(error);
    }
  });

  document.getElementById('filter-completed').addEventListener('change', (e) => {
    const checked = e.target.checked;
    loadActions({ completed: checked });
  });

  Promise.all([loadNotebooks(), loadNotes(), loadActions()]).catch(showError);
});


