from django.db import models
from django.conf import settings

# Tag モデルの定義
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, help_text="タグ名（例: 肩こり解消, ストレス軽減）")

    def __str__(self):
        return self.name

# ConditionLog モデルの定義
class ConditionLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    log_date = models.DateField()
    # 1から5までの疲れと気分のレベルを選択肢として定義
    # 入力内容はまだ仮
    fatigue_level = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text="疲れのレベル (1: 全くない - 5: 非常に疲れている)"
    )
    mood_level = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text="気分のレベル (1: 最悪 - 5: 最高)"
    )
    body_concern = models.TextField(
        blank=True,
        help_text="体の悩み（肩こりなど）を自由に記述"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.log_date} - Fatigue: {self.fatigue_level}, Mood: {self.mood_level}"

# ExerciseMenu モデルの定義
class ExerciseMenu(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    beginner_guide = models.TextField(blank=True, help_text="初心者向けアドバイスやコツ")
    category = models.CharField(
        max_length=50,
        choices=[
            ('stretch', 'ストレッチ'),
            ('strength', '筋力トレーニング'),
            ('cardio', '有酸素運動'),
            ('other', 'その他'),
        ],
        default='stretch'
    )
    target_area = models.CharField(
        max_length=100,
        blank=True,
        help_text="対象部位（例: 肩、背中、全身）"
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        help_text="この運動メニューに関連するタグ"
    )

    def __str__(self):
        return self.name

# Routine モデルの定義
class Routine(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exercise = models.ForeignKey(ExerciseMenu, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # 同じユーザーが同じ運動をルーティンに複数回追加できないようにする
        unique_together = ('user', 'exercise')

    def __str__(self):
        return f"{self.user.username}'s routine: {self.exercise.name}"