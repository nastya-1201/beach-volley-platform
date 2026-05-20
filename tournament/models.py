from django.db import models
from django.core.exceptions import ValidationError


class Tournament(models.Model):
    FORMAT_CHOICES = [
        ('single_elim', 'Олимпийская система'),
        ('double_elim', 'До двух поражений'),
    ]

    name = models.CharField('Название турнира', max_length=200)
    start_date = models.DateField('Дата начала')
    end_date = models.DateField('Дата окончания')
    location = models.CharField('Место проведения', max_length=255, blank=True)
    format_type = models.CharField('Формат турнира', max_length=30, choices=FORMAT_CHOICES)
    video_link = models.URLField('Ссылка на видео', blank=True)
    photo_album_link = models.URLField('Ссылка на фотоальбом', blank=True)

    BRACKET_SIZE_CHOICES = [
    (6, '6 команд'),
    (8, '8 команд'),
    (10, '10 команд'),
    (12, '12 команд'),
    (16, '16 команд'),
    (24, '24 команды'),
    (32, '32 команды'),
]

    bracket_size = models.PositiveIntegerField(
        'Размер сетки',
        choices=BRACKET_SIZE_CHOICES,
        null=True,
        blank=True
    )
    bracket_data = models.JSONField(
        'Данные сетки',
        default=dict,
        blank=True
    )

    class Meta:
        verbose_name = 'Турнир'
        verbose_name_plural = 'Турниры'

    def __str__(self):
        return self.name


class TournamentGroup(models.Model):
    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        related_name='groups',
        verbose_name='Турнир'
    )
    name = models.CharField('Название группы', max_length=50)

    class Meta:
        unique_together = ('tournament', 'name')
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return f'{self.tournament.name} — группа {self.name}'


class Player(models.Model):
    first_name = models.CharField('Имя', max_length=100)
    last_name = models.CharField('Фамилия', max_length=100)
    age = models.PositiveIntegerField('Возраст', null=True, blank=True)
    volleyball_experience = models.PositiveIntegerField('Стаж в волейболе', null=True, blank=True)
    beach_experience = models.PositiveIntegerField('Стаж в пляжном волейболе', null=True, blank=True)
    photo = models.ImageField('Фотография', upload_to='players/', null=True, blank=True)

    class Meta:
        verbose_name = 'Игрок'
        verbose_name_plural = 'Игроки'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Court(models.Model):
    name = models.CharField('Название площадки', max_length=100)
    address = models.CharField('Адрес', max_length=255)
    contact_phone = models.CharField('Телефон ответственного', max_length=30, blank=True)

    class Meta:
        verbose_name = 'Площадка'
        verbose_name_plural = 'Площадки'

    def __str__(self):
        return self.name


class TournamentPair(models.Model):
    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        related_name='pairs',
        verbose_name='Турнир'
    )
    group = models.ForeignKey(
        TournamentGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pairs',
        verbose_name='Группа'
    )
    player1 = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='pairs_as_player1',
        verbose_name='Первый игрок'
    )
    player2 = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='pairs_as_player2',
        verbose_name='Второй игрок'
    )

    class Meta:
        verbose_name = 'Пара турнира'
        verbose_name_plural = 'Пары турнира'
        unique_together = ('tournament', 'player1', 'player2')

    def clean(self):
        if self.player1 == self.player2:
            raise ValidationError('В паре не может быть один и тот же игрок дважды.')

    def __str__(self):
        return f'{self.player1.first_name} / {self.player2.first_name}'


class Match(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Запланирован'),
        ('ongoing', 'Идёт'),
        ('finished', 'Сыгран'),
    ]

    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        related_name='matches',
        null=True,
        blank=True,
        verbose_name='Турнир'
    )
    group = models.ForeignKey(
        TournamentGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='matches',
        verbose_name='Группа'
    )
    pair1 = models.ForeignKey(
    TournamentPair,
    on_delete=models.CASCADE,
    related_name='matches_as_pair1',
    verbose_name='Пара 1',
    null=True,
    blank=True
    )

    pair2 = models.ForeignKey(
        TournamentPair,
        on_delete=models.CASCADE,
        related_name='matches_as_pair2',
        verbose_name='Пара 2',
        null=True,
        blank=True
    )
    court = models.ForeignKey(
        Court,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Площадка'
    )

    match_number = models.PositiveIntegerField('Номер матча', null=True, blank=True)
    next_match = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='previous_matches',
        verbose_name='Следующий матч'
    )
    BRACKET_STAGE_CHOICES = [
    ('winners', 'Сетка победителей'),
    ('losers', 'Сетка проигравших'),
    ('final', 'Финал'),
    ('third_place', 'Матч за 3 место'),
    ]

    bracket_stage = models.CharField(
        'Часть сетки',
        max_length=30,
        choices=BRACKET_STAGE_CHOICES,
        blank=True
    )

    round_number = models.PositiveIntegerField(
        'Раунд сетки',
        null=True,
        blank=True
    )

    position = models.PositiveIntegerField(
        'Позиция в раунде',
        null=True,
        blank=True
    )

    loser_next_match = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='loser_previous_matches',
        verbose_name='Следующий матч для проигравшего'
    )
    match_date = models.DateField('Дата матча')
    match_time = models.TimeField('Время матча')
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='planned')
    score = models.CharField('Счёт', max_length=20, blank=True)
    winner = models.ForeignKey(
        TournamentPair,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='won_matches',
        verbose_name='Победитель'
    )
    def clean(self):
        if self.pair1 and self.pair2 and self.pair1 == self.pair2:
            raise ValidationError('Матч не может быть между одной и той же парой.')

        if self.tournament and self.pair1 and self.pair1.tournament != self.tournament:
            raise ValidationError('Пара 1 должна относиться к выбранному турниру.')

        if self.tournament and self.pair2 and self.pair2.tournament != self.tournament:
            raise ValidationError('Пара 2 должна относиться к выбранному турниру.')

        if self.group and self.tournament and self.group.tournament != self.tournament:
            raise ValidationError('Группа должна относиться к выбранному турниру.')
    class Meta:
        verbose_name = 'Матч'
        verbose_name_plural = 'Матчи'

    def update_score_from_sets(self):
        pair1_sets = 0
        pair2_sets = 0

        for set_result in self.sets.all():
            if set_result.pair1_points > set_result.pair2_points:
                pair1_sets += 1
            elif set_result.pair2_points > set_result.pair1_points:
                pair2_sets += 1

        self.score = f'{pair1_sets}:{pair2_sets}'

        if pair1_sets > pair2_sets:
            self.winner = self.pair1
            self.status = 'finished'
        elif pair2_sets > pair1_sets:
            self.winner = self.pair2
            self.status = 'finished'
        else:
            self.winner = None

        self.save()

    def __str__(self):
        pair1_name = self.pair1 if self.pair1 else 'Пара 1'
        pair2_name = self.pair2 if self.pair2 else 'Пара 2'

        if self.match_number:
            return f'Матч {self.match_number}: {pair1_name} — {pair2_name}'
        return f'{pair1_name} — {pair2_name}'


class SetResult(models.Model):
    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name='sets',
        verbose_name='Матч'
    )
    set_number = models.PositiveIntegerField('Номер партии')
    pair1_points = models.PositiveIntegerField('Очки пары 1')
    pair2_points = models.PositiveIntegerField('Очки пары 2')

    class Meta:
        verbose_name = 'Партия'
        verbose_name_plural = 'Партии'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.match.update_score_from_sets()

    def __str__(self):
        return f'Партия {self.set_number}: {self.pair1_points}-{self.pair2_points}'


class News(models.Model):
    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        related_name='news',
        null=True,
        blank=True,
        verbose_name='Турнир'
    )
    title = models.CharField('Заголовок', max_length=200)
    content = models.TextField('Текст новости')
    created_at = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'

    def __str__(self):
        return self.title