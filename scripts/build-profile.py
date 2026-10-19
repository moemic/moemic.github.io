#!/usr/bin/env python3
"""公開用データから既存サイトの実績・動画欄だけを生成する。"""
import argparse
from datetime import datetime
import html
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def exact_keys(value, expected):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise ValueError('公開データのフィールドが仕様と一致しません')


def text(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 2000:
        raise ValueError('空または長すぎる文章です')
    return html.escape(value, quote=True)


def render(data):
    exact_keys(data, ['schema_version', 'cases', 'videos', 'featured_video'])
    if type(data['schema_version']) is not int or data['schema_version'] != 2:
        raise ValueError('未対応のデータ版です')
    if not isinstance(data['cases'], list) or not 1 <= len(data['cases']) <= 100:
        raise ValueError('実績の件数が範囲外です')
    if not isinstance(data['videos'], list) or len(data['videos']) > 40:
        raise ValueError('動画の件数が範囲外です')
    cases, ids = [], set()
    for item in data['cases']:
        exact_keys(item, ['id', 'period', 'title', 'subtitle', 'open', 'groups'])
        if not isinstance(item['id'], str) or not re.fullmatch(r'[a-z0-9-]+', item['id']) or item['id'] in ids:
            raise ValueError('実績IDが不正または重複しています')
        ids.add(item['id'])
        if type(item['open']) is not bool or not isinstance(item['groups'], list) or len(item['groups']) != 3:
            raise ValueError('実績の形式が不正です')
        groups = []
        for group in item['groups']:
            exact_keys(group, ['heading', 'kind', 'content'])
            if group['kind'] == 'list' and isinstance(group['content'], list) and 1 <= len(group['content']) <= 20:
                body = '<ul>' + ''.join('<li>' + text(s) + '</li>' for s in group['content']) + '</ul>'
            elif group['kind'] == 'paragraph':
                body = '<p>' + text(group['content']) + '</p>'
            else:
                raise ValueError('実績本文の形式が不正です')
            groups.append('            <div><h4>' + text(group['heading']) + '</h4>' + body + '</div>')
        cases.append('        <details class="case"' + (' open' if item['open'] else '') + '>\n'
            + '          <summary><span class="yr">' + text(item['period']) + '</span><h3>'
            + text(item['title']) + '<small>' + text(item['subtitle']) + '</small></h3><span class="plus">+</span></summary>\n'
            + '          <div class="case-body">\n' + '\n'.join(groups) + '\n          </div>\n        </details>')
    videos, video_ids = [], set()
    for video in data['videos']:
        exact_keys(video, ['youtube_id', 'title'])
        vid = video['youtube_id']
        if not isinstance(vid, str) or not re.fullmatch(r'[A-Za-z0-9_-]{11}', vid) or vid in video_ids:
            raise ValueError('動画IDが不正または重複しています')
        video_ids.add(vid)
        videos.append('        <div class="video"><iframe loading="lazy" src="https://www.youtube.com/embed/'
                      + vid + '" title="' + text(video['title']) + '" allowfullscreen></iframe></div>')
    featured = ''
    video = data['featured_video']
    if video is not None:
        exact_keys(video, ['youtube_id', 'title', 'published_at'])
        vid = video['youtube_id']
        if not isinstance(vid, str) or not re.fullmatch(r'[A-Za-z0-9_-]{11}', vid):
            raise ValueError('最新動画のIDが不正です')
        if not isinstance(video['published_at'], str):
            raise ValueError('公開日時が不正です')
        published = datetime.fromisoformat(video['published_at'])
        if published.tzinfo is None:
            raise ValueError('公開日時にはタイムゾーンが必要です')
        title = text(video['title'])
        featured = ('      <article class="featured-work reveal">\n'
            + '        <p class="eyebrow">最新の公開動画</p>\n'
            + '        <h3>' + title + '</h3>\n'
            + '        <p class="featured-meta"><time datetime="' + text(video['published_at']) + '">'
            + published.strftime('%Y.%m.%d') + '</time> 公開 · <a href="https://www.youtube.com/watch?v='
            + vid + '" target="_blank" rel="noopener">YouTubeで見る ↗</a></p>\n'
            + '        <div class="video"><iframe loading="lazy" src="https://www.youtube.com/embed/'
            + vid + '" title="' + title + '" allowfullscreen></iframe></div>\n'
            + '      </article>')
    return '\n\n'.join(cases), '\n'.join(videos), featured


def build(document, data):
    cases, videos, featured = render(data)
    for name, body in [('cases', cases), ('videos', videos), ('featured', featured)]:
        start, end = '<!-- profile:' + name + ':start -->', '<!-- profile:' + name + ':end -->'
        if document.count(start) != 1 or document.count(end) != 1:
            raise ValueError('生成範囲のマーカーが一意ではありません')
        before, rest = document.split(start, 1)
        old, after = rest.split(end, 1)
        document = before + start + '\n' + body + '\n      ' + end + after
    return document


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='生成結果の一致だけを確認する')
    args = parser.parse_args()
    path = ROOT / 'index.html'
    current = path.read_text(encoding='utf-8')
    data = json.loads((ROOT / 'data/profile-public.json').read_text(encoding='utf-8'))
    generated = build(current, data)
    if args.check:
        if current != generated:
            raise SystemExit('公開データとHTMLが一致しません。生成を実行してください。')
        print('公開データとHTMLの一致を確認しました')
    elif current != generated:
        path.write_text(generated, encoding='utf-8')


if __name__ == '__main__':
    main()
