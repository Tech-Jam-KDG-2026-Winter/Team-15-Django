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
 * API：おすすめ取得
 *************************************************/
const conditionForm = document.getElementById('condition-form');
if (conditionForm) {
    conditionForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const fatigue = document.getElementById('fatigue').value;
        const mood = document.getElementById('mood').value;
        const concern = document.getElementById('concern').value;

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
            alert('メニュー提案に失敗しました。');
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
        const exerciseTitle = data.exercise ? data.exercise.name : '不明な運動メニュー';
        alert(`${exerciseTitle} をルーティンに追加しました！`);
        fetchRoutines();
    } else if(response.status === 200) {
        const exerciseTitle = data.exercise ? data.exercise.name : '不明な運動メニュー';
        alert(`この運動メニュー (${exerciseTitle}) は既にルーティンに登録されています。`);
        fetchRoutines(); 
    } else {
        const errorMessage = data && data.error ? data.error : 'ルーティン追加に失敗しました。';
        alert(errorMessage);
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
        alert('ルーティンから削除しました！');
        fetchRoutines();
    } else {
        alert('ルーティン削除に失敗しました。');
    }
}


/*************************************************
 * API：取得系
 *************************************************/
async function fetchHistory() {
    const container = document.getElementById('history-list');
    if (!container) return;

    const response = await fetch('/api/history/');
    if (!response.ok) {
        displayHistory([]);
        return;
    }

    displayHistory(await response.json());
}

async function fetchRoutines() {
    const container = document.getElementById('routine-list');
    if (!container) return;

    const response = await fetch('/api/routines/');
    if (!response.ok) {
        displayRoutines([]);
        return;
    }

    displayRoutines(await response.json());
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


/*************************************************
 * イベント委譲（ボタン操作）
 *************************************************/
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('add-routine-btn')) {
        addRoutine(e.target.dataset.exerciseId);
    }

    if (e.target.classList.contains('delete-routine-btn')) {
        deleteRoutine(e.target.dataset.exerciseId);
    }
});


/*************************************************
 * 初期ロード
 *************************************************/
document.addEventListener('DOMContentLoaded', () => {
    fetchHistory();
    fetchRoutines();

    // exercise_detail.html 用（data属性がある場合）
    const detail = document.getElementById('exercise-detail');
    if (detail && detail.dataset.exerciseId) {
        fetchExerciseDetail(detail.dataset.exerciseId);
    }
});


/*************************************************
 * ===== DOM =====
 *************************************************/
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

    div.innerHTML = `
        <h1>${menu.name}</h1>
        <p>${menu.description}</p>
        <p>カテゴリー: ${menu.category}</p>
        <p>タグ: ${menu.tags.map(t => t.name).join(', ')}</p>
        <button class="add-routine-btn" data-exercise-id="${menu.id}">
            ルーティンに追加
        </button>
    `;
}
