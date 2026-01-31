# 【杉山さんへ：フロントエンド（HTML/CSS/JS画面要素）担当】

**あなたの役割**
ユーザーインターフェース（UI）/ユーザー体験（UX）を最も重視し、画面のHTML構造とCSSでのスタイリング、そしてリーダーがAPIから取得したデータが渡された後の純粋な**DOM操作**を担当していただきます。
**API連携（fetchの呼び出しなど）は一切触らなくて大丈夫です。**

**担当する主なファイル**
*   `templates/*.html` (各ページのHTMLファイル)
*   `static/css/style.css` (デザイン全般)
*   `static/js/main.js` (DOM操作の部分)

## 考えるべきポイント
1.  **UI/UX**: ユーザーが直感的に、快適に使えるデザインを追求してください。特に、入力フォームやボタンの配置、情報表示の分かりやすさを意識してください。レスポンシブデザイン（PCでもスマホでも見やすいか）に関しては、余裕があればで大丈夫です
2.  **HTMLの構造**: 意味が分かりやすいHTMLタグを使い、CSSでスタイリングしやすいようにクラス名などを適切に設定してください。
3.  **DOM操作**: リーダーがAPIからデータを取得し、`display...` 関数に渡します。あなたはそのデータを受け取り、HTMLの特定の `id` や `class` を持つ要素の中に、動的にHTMLを生成して表示する部分の編集を行なってください
4.  **CSSでのスタイリング**: アプリのイメージにあったデザインをお願いします。


### JavaScriptについて（重要）

JavaScriptは「難しい処理」を書く必要はありません。
以下の3つだけ分かれば十分です。

1. HTMLの要素を取得する
   例: document.getElementById('recommendations')

2. その中身を書き換える
   例: element.innerHTML = '表示したいHTML';

3. 配列データを順番に処理する
   例: data.forEach(item => { ... });

「関数を書く」「API通信をする」「イベント処理を書く」必要はありません。
今回、html、cssに関連するjsはこちらで簡単な例を用意したので、それに杉山さんが作成したhtml、cssと合わせてください。
もし合わせ方がわからない、jsに正しく反映できてるかわからないなどがあれば、すぐに相談してください。

### 追記
<div id="recommendations">
    <!-- JavaScriptでここに表示 -->
</div>
このような形でhtmlの例が書かれていることがありますが、これは、jsで受け取ったデータを、jsからhtmlにデータを送るイメージで、jsの関数でhtmlを記述します。
(下記のdisplayRecommendations関数参照)つまり、htmlファイル側では、id="recommendations"をつければ、中身は空でOKということです。

---

## 実装の骨子

### `templates/*.html`
各HTMLファイルは、以下の基本的な構造とナビゲーションをbase.htmlという形で持つように設計してください。各セクションに適切な `id` や `class` を設定し、CSSやJavaScriptから操作しやすくしてください。

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>コンディション・パートナー</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <header>
        <nav>
            <!-- header例 -->
            <a href="/">トップページ</a> |
            <a href="/history/">履歴を見る</a> |
            <a href="/routines-list/">ルーティンを見る</a> |
            <a href="/exercise-list/">運動メニュー一覧</a>
        </nav>
        <h1>[ページタイトルなど]</h1>
    </header>
    <main>
        <!-- 各ページ固有のコンテンツ -->
        {% block content %}{% endblock %}
    </main>
    <script src="/static/js/main.js"></script>
</body>
</html>

<!-- templates/top.html のデータ表示例 -->
{% extends 'base.html' %}
{% block content %}
    <section id="condition-input-section">
        <h2>今日のコンディションを入力</h2>
        <form id="condition-form">
            <!-- 疲れ、気分、悩みの入力フィールドと送信ボタン -->
        </form>
    </section>
    <section id="recommendations-section">
        <h2>おすすめメニュー</h2>
        <div id="recommendations">
            <!-- JavaScriptでここに表示 -->
        </div>
    </section>
{% endblock %}

<!-- templates/history.html の表示例 -->
{% extends 'base.html' %}
{% block content %}
    <h2>あなたの体調ログ履歴</h2>
    <div id="history-list">
        <!-- JavaScriptでここに表示 -->
    </div>
{% endblock %}

<!-- templates/routine_list.html の表示例 -->
{% extends 'base.html' %}
{% block content %}
    <h2>あなたのルーティン一覧</h2>
    <div id="routine-list">
        <!-- JavaScriptでここに表示 -->
    </div>
{% endblock %}

<!-- templates/exercise_detail.html の表示例 -->
{% extends 'base.html' %}
{% block content %}
    <div id="exercise-detail">
        <!-- JavaScriptでここに表示 -->
        <h1>メニュー詳細を読み込み中...</h1>
    </div>
{% endblock %}

<!-- templates/exercise_list.html の表示例 -->
{% extends 'base.html' %}
{% block content %}
    <section id="exercise-search-section">
        <h2>運動メニュー検索</h2>
        <form id="exercise-search-form">
            <!-- キーワード、カテゴリ、タグの入力フィールドと検索ボタン -->
        </form>
    </section>
    <section id="exercise-results-section">
        <h2>検索結果</h2>
        <div id="exercise-list">
            <!-- JavaScriptでここに表示 -->
        </div>
    </section>
{% endblock %}
```

### `static/js/main.js` (DOM操作に集中)
リーダーがAPIから取得したデータを、以下の `display...` 関数に渡します。杉山さんはどのようなHTML構造で、どのように表示するか、を実装してください。
```javascript

// 以下はmain.jsに記載されている、僕が各APIから取得したデータを、以下の関数に渡し、HTMLを生成するものです。ここのHTMLで、なにをどのように表示するかを杉山さんにお任せしようと思います(例えば、おすすめメニューではこれを見出しで、これをpタグで、など)。


// displayRecommendations: おすすめメニューを recommendationsDiv に表示
function displayRecommendations(data) {
    const recommendationsDiv = document.getElementById('recommendations');
    recommendationsDiv.innerHTML = '';

    if (data.rest_suggestion) {
        recommendationsDiv.innerHTML = `<p style="font-weight: bold; color: green;">${data.message}</p>`;
    } else if (Array.isArray(data) && data.length > 0) { // データが配列で、かつ中身がある場合
        data.forEach(menu => {
            const menuCard = document.createElement('div');
            menuCard.className = 'menu-card';
            menuCard.innerHTML = `
                <h3><a href="/exercises/${menu.id}/">${menu.name}</a></h3>
                <p>${menu.description}</p>
                <p>カテゴリー: ${menu.category}</p>
                <p>タグ: ${menu.tags.map(tag => tag.name).join(', ')}</p>
                <button class="add-routine-btn" data-exercise-id="${menu.id}">ルーティンに追加</button>
                <a href="/exercises/${menu.id}/">詳細を見る</a>
            `;
            recommendationsDiv.appendChild(menuCard);
        });
    } else {
        recommendationsDiv.innerHTML = '<p>あなたへのおすすめメニューは見つかりませんでした。基本的なストレッチを試してみましょう。</p>';
    }
}

// displayHistory: historyListDiv に体調ログを表示
function displayHistory(logs) {
    const historyListDiv = document.getElementById('history-list');
    historyListDiv.innerHTML = '';

    if (Array.isArray(logs) && logs.length > 0) {
        logs.forEach(log => {
            const logEntry = document.createElement('div');
            logEntry.className = 'log-entry';
            logEntry.innerHTML = `
                <p><strong>日付:</strong> ${log.log_date}</p>
                <p><strong>疲れレベル:</strong> ${log.fatigue_level}</p>
                <p><strong>気分レベル:</strong> ${log.mood_level}</p>
                ${log.body_concern ? `<p><strong>体の悩み:</strong> ${log.body_concern}</p>` : ''}
                <small>記録日時: ${new Date(log.created_at).toLocaleString()}</small>
            `;
            historyListDiv.appendChild(logEntry);
        });
    } else {
        historyListDiv.innerHTML = '<p>まだ体調ログがありません。トップページから記録してみましょう！</p>';
    }
}

// displayRoutines: routineListDiv にルーティンを表示
function displayRoutines(routines) {
    const routineListDiv = document.getElementById('routine-list');
    routineListDiv.innerHTML = '';

    if (Array.isArray(routines) && routines.length > 0) {
        routines.forEach(routine => {
            const routineEntry = document.createElement('div');
            routineEntry.className = 'routine-entry';
            routineEntry.innerHTML = `
                <h3><a href="/exercises/${routine.exercise.id}/">${routine.exercise.name}</a></h3>
                <p>${routine.exercise.description}</p>
                <p>カテゴリー: ${routine.exercise.category}</p>
                <p>タグ: ${routine.exercise.tags.map(tag => tag.name).join(', ')}</p>
                <small>追加日: ${new Date(routine.added_at).toLocaleString()}</small><br>
                <button class="delete-routine-btn" data-exercise-id="${routine.exercise.id}">ルーティンから削除</button>
            `;
            routineListDiv.appendChild(routineEntry);
        });
    } else {
        routineListDiv.innerHTML = '<p>まだルーティンがありません。トップページから追加してみましょう！</p>';
    }
}

// displayExerciseDetail: exerciseDetailDiv に運動メニュー詳細を表示
function displayExerciseDetail(menu) {
    const exerciseDetailDiv = document.getElementById('exercise-detail');
    exerciseDetailDiv.innerHTML = ''; // リセット

    if (menu) { // メニューデータが存在する場合
        exerciseDetailDiv.innerHTML = `
            <h1>${menu.name}</h1>
            <p><strong>説明:</strong> ${menu.description}</p>
            ${menu.beginner_guide_html ? `<div class="beginner-guide-content"><h3>初心者向けアドバイス:</h3>${menu.beginner_guide_html}</div>` : ''}
            <p><strong>カテゴリー:</strong> ${menu.category}</p>
            <p><strong>対象部位:</strong> ${menu.target_area}</p>
            <p><strong>タグ:</strong> ${menu.tags.map(tag => tag.name).join(', ')}</p>
            <button class="add-routine-btn" data-exercise-id="${menu.id}">ルーティンに追加</button>
        `;
    } else {
        exerciseDetailDiv.innerHTML = '<p>指定された運動メニューが見つかりませんでした。</p>';
    }
}

// displayExerciseList: exerciseListDiv に運動メニュー一覧を表示
function displayExerciseList(exercises) {
    const exerciseListDiv = document.getElementById('exercise-list');
    exerciseListDiv.innerHTML = '';

    if (Array.isArray(exercises) && exercises.length > 0) {
        exercises.forEach(menu => {
            const menuCard = document.createElement('div');
            menuCard.className = 'menu-card';
            menuCard.innerHTML = `
                <h3><a href="/exercises/${menu.id}/">${menu.name}</a></h3>
                <p>${menu.description}</p>
                <p>カテゴリー: ${menu.category}</p>
                <p>タグ: ${menu.tags.map(tag => tag.name).join(', ')}</p>
                <button class="add-routine-btn" data-exercise-id="${menu.id}">ルーティンに追加</button>
                <a href="/exercises/${menu.id}/">詳細を見る</a>
            `;
            exerciseListDiv.appendChild(menuCard);
        });
    } else {
        exerciseListDiv.innerHTML = '<p>条件に合う運動メニューは見つかりませんでした。</p>';
    }
}

```


## 杉山さんへの補足
*   `static/css/style.css` を使って、全ての画面のデザインをお願いします。

