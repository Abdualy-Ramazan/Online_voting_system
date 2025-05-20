from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError

# --- Валидация изображений ---
def validate_image_size(image):
    if image.size > 2 * 1024 * 1024:
        raise ValidationError("Размер изображения не должен превышать 2MB.")

def validate_image_extension(image):
    valid_extensions = ['jpg', 'jpeg', 'png', 'gif']
    extension = image.name.split('.')[-1].lower()
    if extension not in valid_extensions:
        raise ValidationError(f"Неверный формат изображения. Допустимые: {', '.join(valid_extensions)}.")

# --- Опрос ---
class Poll(models.Model):
    question = models.CharField("Вопрос", max_length=255)
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)
    end_date = models.DateTimeField("Дата окончания")
    allow_multiple_choices = models.BooleanField("Разрешить множественный выбор", default=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    image = models.ImageField(
        "Изображение опроса",
        upload_to='poll_images/',
        blank=True,
        null=True,
        validators=[validate_image_size, validate_image_extension]
    )

    class Meta:
        verbose_name = "Опрос"
        verbose_name_plural = "Опросы"
        ordering = ['-pub_date']

    def __str__(self):
        return self.question

    def is_active(self):
        return self.end_date >= timezone.now()
    is_active.boolean = True

    def average_rating(self):
        ratings = self.ratings.all()
        if ratings:
            return round(sum(r.rating_value for r in ratings) / ratings.count(), 1)
        return None

    def clean(self):
        if self.end_date <= timezone.now():
            raise ValidationError("Дата окончания должна быть позже текущего времени.")
        if len(self.question.strip()) < 10:
            raise ValidationError("Вопрос должен содержать минимум 10 символов.")

# --- Варианты ответа ---
class Choice(models.Model):
    poll = models.ForeignKey(Poll, related_name='choices', on_delete=models.CASCADE)
    choice_text = models.CharField("Текст варианта", max_length=200)

    class Meta:
        verbose_name = "Вариант ответа"
        verbose_name_plural = "Варианты ответа"

    def __str__(self):
        return self.choice_text

    def clean(self):
        if not self.choice_text.strip():
            raise ValidationError("Текст варианта ответа не может быть пустым.")

# --- Голоса ---
class Vote(models.Model):
    poll = models.ForeignKey(Poll, related_name='votes', on_delete=models.CASCADE)
    vote_choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    user_name = models.CharField("Имя пользователя", max_length=100, default="anonymous")
    comment = models.TextField("Комментарий", null=True, blank=True)
    created_at = models.DateTimeField("Дата голосования", auto_now_add=True)

    class Meta:
        verbose_name = "Голос"
        verbose_name_plural = "Голоса"

    def __str__(self):
        return f"Голос от {self.user_name} за {self.poll.question}"

    def clean(self):
        if self.comment and len(self.comment) > 300:
            raise ValidationError("Комментарий к голосу не должен превышать 300 символов.")

# --- Оценка ---
class Rating(models.Model):
    poll = models.ForeignKey(Poll, related_name='ratings', on_delete=models.CASCADE)
    user_name = models.CharField("Имя пользователя", max_length=100, default="anonymous")
    rating_value = models.IntegerField("Оценка", default=0)
    comment = models.TextField("Комментарий", null=True, blank=True)
    created_at = models.DateTimeField("Дата оценки", auto_now_add=True)

    class Meta:
        verbose_name = "Оценка"
        verbose_name_plural = "Оценки"

    def __str__(self):
        return f"Оценка от {self.user_name} для {self.poll.question}"

    def clean(self):
        if not (1 <= self.rating_value <= 5):
            raise ValidationError("Оценка должна быть от 1 до 5.")
        if self.comment and len(self.comment) > 300:
            raise ValidationError("Комментарий к оценке не должен превышать 300 символов.")

# --- Объявления ---
class Announcement(models.Model):
    title = models.CharField("Заголовок", max_length=200)
    content = models.TextField("Текст объявления")
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")

    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def clean(self):
        if len(self.title.strip()) < 5:
            raise ValidationError("Заголовок объявления должен содержать минимум 5 символов.")

# --- Профиль ---
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(
        "Аватар",
        upload_to='avatars/',
        blank=True,
        null=True,
        validators=[validate_image_size, validate_image_extension]
    )

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return f"Профиль {self.user.username}"

    def clean(self):
        if self.avatar and self.avatar.size > 2 * 1024 * 1024:
            raise ValidationError("Размер аватара не должен превышать 2MB.")
