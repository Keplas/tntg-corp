"""
Custom template filter for embedding YouTube videos.

Usage in templates:
  {% load video_tags %}
  {% with embed_url=program.video_url|youtube_embed_url %}
    {% if embed_url %}
      <iframe src="{{ embed_url }}" ...></iframe>
    {% else %}
      <a href="{{ program.video_url }}">Watch Now</a>
    {% endif %}
  {% endwith %}
"""
import re
from django import template

register = template.Library()

# Matches youtube.com/watch?v=ID, youtu.be/ID, youtube.com/embed/ID,
# and youtube.com/shorts/ID — capturing the 11-character video ID.
_YOUTUBE_RE = re.compile(
    r'(?:youtube\.com/(?:watch\?v=|embed/|shorts/)|youtu\.be/)([A-Za-z0-9_-]{11})'
)


@register.filter
def youtube_embed_url(url):
    """
    Return an embeddable https://www.youtube.com/embed/<id> URL if `url`
    is a recognizable YouTube link, otherwise return an empty string so
    templates can fall back to a plain "Watch Now" link.
    """
    if not url:
        return ''
    match = _YOUTUBE_RE.search(url)
    if not match:
        return ''
    return f'https://www.youtube.com/embed/{match.group(1)}'
