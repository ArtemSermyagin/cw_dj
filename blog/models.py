from django.db import models

from clients.models import Newsletter

NULLABLE = {'null': True, 'blank': True}


class BlogPost(models.Model):
    title = models.CharField(max_length=150, verbose_name='заголовок')
    slug = models.CharField(max_length=150, verbose_name='slug', **NULLABLE)
    body = models.TextField(verbose_name='содержимое')
    preview = models.ImageField(upload_to='blog_post/', verbose_name='изображение', **NULLABLE)
    date_creation = models.DateField(auto_now_add=True, verbose_name='Дата создания')
    sign_publication = models.BooleanField(verbose_name='признак публикации')
    number_views = models.IntegerField(verbose_name='количество просмотров', **NULLABLE)
    newsletter = models.ForeignKey(Newsletter, on_delete=models.CASCADE, related_name='blogs', verbose_name='рассылка для блога')

    def __str__(self):
        return f'{self.title}, {self.slug}, {self.body}, {self.preview},' \
               f'{self.date_creation}, {self.sign_publication}'

    class Meta:
        verbose_name = 'blog'
        verbose_name_plural = 'blogs'
        ordering = ('id',)
