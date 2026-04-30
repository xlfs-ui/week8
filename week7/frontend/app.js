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
    text.textContent = `${n.title ?? ''}: ${n.content ?? ''} `;
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
}

async function loadActions(params = {}) {
  const list = document.getElementById('actions');
  list.innerHTML = '';
  const query = new URLSearchParams(params);
  const items = await fetchJSON('/action-items/?' + query.toString());
  for (const a of items) {
    const li = document.createElement('li');
    li.textContent = `${a.description} [${a.completed ? 'done' : 'open'}]`;
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
  document.getElementById('note-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = document.getElementById('note-title').value;
    const content = document.getElementById('note-content').value;
    try {
      await fetchJSON('/notes/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, content }),
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
    const description = document.getElementById('action-desc').value;
    try {
      await fetchJSON('/action-items/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description }),
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

  loadNotes().catch(showError);
  loadActions().catch(showError);
});


