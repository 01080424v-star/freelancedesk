const CSRF_TOKEN = document.querySelector('meta[name="csrf-token"]')?.content || '';

async function updateStatus(id, status, selectEl) {
    try {
        const resp = await fetch(`/api/admin/requests/${id}/status`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': CSRF_TOKEN,
            },
            body: JSON.stringify({ status }),
        });
        const data = await resp.json();
        if (resp.ok) {
            if (selectEl) {
                selectEl.className = `status-select badge-select badge-${status}`;
            }
        } else {
            alert(data.error || 'Помилка оновлення статусу');
            location.reload();
        }
    } catch (e) {
        alert("Помилка з'єднання з сервером");
        location.reload();
    }
}
