/*************************************************
 * CSRFトークン取得ヘルパー
 *************************************************/
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');


/*************************************************
 * Toast通知ヘルパー
 *************************************************/
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast-message ${type}`;
    
    let icon = 'ℹ️';
    if (type === 'success') icon = '✅';
    if (type === 'error') icon = '❌';
    
    toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
    
    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('fade-out');
        toast.addEventListener('animationend', () => {
            toast.remove();
        });
    }, 3000);
}


/*************************************************
 * API：おすすめ取得
 *************************************************/
const conditionForm = document.getElementById('condition-form');
if (conditionForm) {
    conditionForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const fatigue = document.getElementById('fatigue_level').value;
        const mood = document.getElementById('mood_level').value;
        const concern = document.getElementById('body_concern').value;
        const response = await fetch('/api/recommend/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({
                fatigue_level: Number(fatigue),
                mood_level: Number(mood),
                body_concern: concern
            })
        });
        if (!response.ok) {
            showToast('メニュー提案に失敗しました。', 'error');
            return;
        }
        const data = await response.json();
        displayRecommendations(data);
    });
}


/*************************************************
 * API：ルーティン操作
 *************************************************/
async function addRoutine(exerciseId) {
    const response = await fetch(`/api/routines/${exerciseId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        }
    });
    const data = await response.json();
    if (response.status === 201) {
        const exerciseTitle = data.routine && data.routine.exercise ? data.routine.exercise.name : '不明な運動メニュー';
        showToast(`${exerciseTitle} をルーティンに追加しました！`, 'success');
        fetchRoutines();
    } else if (response.status === 200) {
        const exerciseTitle = data.routine && data.routine.exercise ? data.routine.exercise.name : '不明な運動メニュー';
        showToast(`既にルーティンに登録されています。`, 'info');
        fetchRoutines();
    } else {
        const errorMessage = data && data.error ? data.error : 'ルーティン追加に失敗しました。';
        showToast(errorMessage, 'error');
    }
}

async function deleteRoutine(exerciseId) {
    const response = await fetch(`/api/routines/${exerciseId}/`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': csrftoken
        }
    });
    if (response.status === 204) {
        showToast('ルーティンから削除しました！', 'success');
        fetchRoutines();
    } else {
        showToast('ルーティン削除に失敗しました。', 'error');
    }
}


/*************************************************
 * API：取得系
 *************************************************/
async function fetchHistory(page = 1) {
    const container = document.getElementById('history-list');
    if (!container) return;

    const response = await fetch(`/api/history/?page=${page}`);
    if (!response.ok) {
        displayHistory([]);
        return;
    }
    const data = await response.json();
    displayHistory(data.results || []);
    displayPagination(data, 'pagination-container-history');
}

async function fetchRoutines(page = 1) {
    const container = document.getElementById('routine-list');
    if (!container) return;

    const response = await fetch(`/api/routines/?page=${page}`);
    if (!response.ok) {
        displayRoutines([]);
        return;
    }
    const data = await response.json();
    displayRoutines(data.results || []);
    displayPagination(data, 'pagination-container-routines');
}

async function fetchExerciseDetail(exerciseId) {
    const container = document.getElementById('exercise-detail');
    if (!container || !exerciseId) return;

    const response = await fetch(`/api/exercises/${exerciseId}/`);
    if (!response.ok) {
        displayExerciseDetail(null);
        return;
    }
    displayExerciseDetail(await response.json());
}

async function fetchExerciseList(page = 1) {
    const container = document.getElementById('exercise-list');
    if (!container) return;

    const keyword = document.getElementById('search-keyword').value;
    const params = new URLSearchParams();
    if (keyword) {
        params.append('q', keyword);
    }
    params.append('page', page);

    const apiUrl = `/api/exercises/?${params.toString()}`;
    const response = await fetch(apiUrl);
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = errorData.detail || errorData.error || `メニュー一覧の取得に失敗しました: ${response.status} ${response.statusText}`;
        showToast(errorMessage, 'error');
        displayExerciseList([]);
        return;
    }
    const data = await response.json();
    displayExerciseList(data.results || []);
    displayPagination(data, 'pagination-container');
}


/*************************************************
 * イベントリスナー
 *************************************************/
document.addEventListener('DOMContentLoaded', () => {
    // 各ページで対応するリストの初期読み込み
    if (document.getElementById('history-list')) {
        fetchHistory();
    }
    if (document.getElementById('routine-list')) {
        fetchRoutines();
    }
    if (document.getElementById('exercise-list')) {
        fetchExerciseList();
    }

    // 詳細ページの初期読み込み
    const detail = document.getElementById('exercise-detail');
    if (detail && detail.dataset.exerciseId) {
        fetchExerciseDetail(detail.dataset.exerciseId);
    }
});

const searchForm = document.getElementById('exercise-search-form');
if (searchForm) {
    searchForm.addEventListener('submit', (e) => {
        e.preventDefault();
        fetchExerciseList(1); // 検索時は1ページ目に戻す
    });
}

document.addEventListener('click', e => {
    const target = e.target;

    // ボタン系
    if (target.classList.contains('add-routine-btn')) {
        addRoutine(target.dataset.exerciseId);
        return;
    }
    if (target.classList.contains('delete-routine-btn')) {
        deleteRoutine(target.dataset.exerciseId);
        return;
    }

    // ページネーション系
    const paginationLink = target.closest('.page-link');
    if (paginationLink && paginationLink.dataset.page) {
        e.preventDefault();
        const page = parseInt(paginationLink.dataset.page, 10);
        if (isNaN(page)) return;

        const paginationNav = target.closest('.pagination-nav');
        if (!paginationNav) return;

        if (paginationNav.id === 'pagination-container') {
            fetchExerciseList(page);
        } else if (paginationNav.id === 'pagination-container-history') {
            fetchHistory(page);
        } else if (paginationNav.id === 'pagination-container-routines') {
            fetchRoutines(page);
        }
    }
});


/*************************************************
 * ===== DOM描画 =====
 *************************************************/
function parseSimpleMarkdown(text) {
    if (!text) return '';

    const lines = text.split('\n');
    let html = '';
    let listType = null; // 'ol' or 'ul' or null

    const closeList = () => {
        if (listType === 'ol') html += '</ol>';
        if (listType === 'ul') html += '</ul>';
        listType = null;
    };

    lines.forEach(line => {
        const trimmedLine = line.trim();

        // Heading
        if (trimmedLine.startsWith('### ')) {
            closeList();
            html += `<h4>${trimmedLine.substring(4)}</h4>`;
        }
        // Numbered List
        else if (trimmedLine.match(/^\d+\.\s/)) {
            if (listType !== 'ol') {
                closeList();
                html += '<ol style="padding-left: 20px; margin-bottom: 16px;">';
                listType = 'ol';
            }
            html += `<li>${trimmedLine.replace(/^\d+\.\s/, '')}</li>`;
        }
        // Bulleted List
        else if (trimmedLine.startsWith('* ')) {
            if (listType !== 'ul') {
                closeList();
                html += '<ul style="padding-left: 20px; margin-bottom: 16px;">';
                listType = 'ul';
            }
            html += `<li>${trimmedLine.substring(2)}</li>`;
        }
        // Bold/Strong text - simple paragraph version
        else if (trimmedLine.startsWith('**') && trimmedLine.endsWith('**')) {
            closeList();
            html += `<p><strong>${trimmedLine.substring(2, trimmedLine.length - 2)}</strong></p>`;
        }
        // Paragraph
        else if (trimmedLine) {
            closeList();
            html += `<p>${trimmedLine}</p>`;
        }
        // Empty line (acts as a separator)
        else {
            closeList();
        }
    });

    closeList(); // Close any open list at the end
    return html;
}

function displayRecommendations(data) {
    const div = document.getElementById('recommendations');
    if (!div) return;
    div.innerHTML = '';
    if (data.rest_suggestion) {
        div.innerHTML = `<p class="notice">${data.message}</p>`;
        return;
    }
    if (!Array.isArray(data) || data.length === 0) {
        div.innerHTML = '<p>おすすめは見つかりませんでした。</p>';
        return;
    }
    data.forEach(menu => {
        div.innerHTML += `
            <div class="menu-card">
                <h3><a href="/exercises/${menu.id}/">${menu.name}</a></h3>
                <p>${menu.description}</p>
                <p>カテゴリー: ${menu.category}</p>
                <p>タグ: ${menu.tags.map(t => t.name).join(', ')}</p>
                <button class="add-routine-btn" data-exercise-id="${menu.id}">ルーティンに追加</button>
            </div>
        `;
    });
}

function displayHistory(logs) {
    const div = document.getElementById('history-list');
    if (!div) return;
    div.innerHTML = '';
    if (!logs.length) {
        div.innerHTML = '<p>履歴はまだありません。</p>';
        return;
    }
    logs.forEach(log => {
        div.innerHTML += `
            <div class="log-entry">
                <p>日付: ${log.log_date}</p>
                <p>疲れ: ${log.fatigue_level}</p>
                <p>気分: ${log.mood_level}</p>
                ${log.body_concern ? `<p>悩み: ${log.body_concern}</p>` : ''}
            </div>
        `;
    });
}

function displayRoutines(routines) {
    const div = document.getElementById('routine-list');
    if (!div) return;
    div.innerHTML = '';
    if (!routines.length) {
        div.innerHTML = '<p>ルーティンはまだありません。</p>';
        return;
    }
    routines.forEach(r => {
        div.innerHTML += `
            <div class="routine-entry">
                <h3>${r.exercise.name}</h3>
                <p>${r.exercise.description}</p>
                <button class="delete-routine-btn" data-exercise-id="${r.exercise.id}">
                    削除
                </button>
            </div>
        `;
    });
}

function displayExerciseDetail(menu) {
    const div = document.getElementById('exercise-detail');
    if (!div) return;
    if (!menu) {
        div.innerHTML = '<p>メニューが見つかりません。</p>';
        return;
    }

    // beginner_guide が存在する場合に表示するセクション
    const guideHtml = menu.beginner_guide ? `
        <div class="beginner-guide-content">
            <h3>🔰 初心者向けガイド</h3>
            ${parseSimpleMarkdown(menu.beginner_guide)}
        </div>
    ` : '';

    div.innerHTML = `
        <div class="detail-header">
            <h1 class="detail-title">${menu.name}</h1>
            <div class="card-meta">
                <span>カテゴリー: ${menu.category}</span>
                <span>|</span>
                <span>タグ: ${menu.tags.map(t => `<span class="tag-badge">${t.name}</span>`).join(' ')}</span>
            </div>
        </div>
        <p class="detail-description">${menu.description}</p>
        
        ${guideHtml}

        <div class="card-actions">
            <button class="add-routine-btn" data-exercise-id="${menu.id}">
                ルーティンに追加
            </button>
        </div>
    `;
}

function displayExerciseList(menus) {
    const div = document.getElementById('exercise-list');
    if (!div) return;
    div.innerHTML = '';
    if (!Array.isArray(menus) || menus.length === 0) {
        div.innerHTML = '<p>条件に合うメニューは見つかりませんでした。</p>';
        return;
    }
    menus.forEach(menu => {
        div.innerHTML += `
            <div class="menu-card">
                <h3><a href="/exercises/${menu.id}/">${menu.name}</a></h3>
                <p>${menu.description}</p>
                <p>カテゴリー: ${menu.category}</p>
                <p>タグ: ${menu.tags.map(t => t.name).join(', ')}</p>
                <button class="add-routine-btn" data-exercise-id="${menu.id}">ルーティンに追加</button>
            </div>
        `;
    });
}

function displayPagination(data, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const { current_page, total_pages } = data;
    container.innerHTML = '';

    if (total_pages <= 1) return;

    const ul = document.createElement('ul');
    ul.className = 'pagination';

    // 「前へ」ボタン
    const prevLi = document.createElement('li');
    prevLi.className = `page-item ${current_page === 1 ? 'disabled' : ''}`;
    prevLi.innerHTML = `<a class="page-link" href="#" data-page="${current_page - 1}">前へ</a>`;
    ul.appendChild(prevLi);

    // ページ番号ボタン
    for (let i = 1; i <= total_pages; i++) {
        const pageLi = document.createElement('li');
        pageLi.className = `page-item ${i === current_page ? 'active' : ''}`;
        pageLi.innerHTML = `<a class="page-link" href="#" data-page="${i}">${i}</a>`;
        ul.appendChild(pageLi);
    }

    // 「次へ」ボタン
    const nextLi = document.createElement('li');
    nextLi.className = `page-item ${current_page === total_pages ? 'disabled' : ''}`;
    nextLi.innerHTML = `<a class="page-link" href="#" data-page="${current_page + 1}">次へ</a>`;
    ul.appendChild(nextLi);

    container.appendChild(ul);
}