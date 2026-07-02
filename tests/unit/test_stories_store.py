import json

from hsg.classes.stories import StoryStore


class TestStoryStore:
    def test_load_json(self, tmp_path):
        data = {
            '一': {'keyword': 'One', 'keyword_ita': 'Uno', 'story': '<b>One</b>'},
            '二': {'keyword': 'Two', 'keyword_ita': 'Due', 'story': 'Two things'},
        }
        f = tmp_path / 'stories.json'
        f.write_text(json.dumps(data))

        store = StoryStore(str(f))
        assert store.get_story('一') is not None
        assert store.get_story('一')['keyword'] == 'One'
        assert store.get_story('三') is None

    def test_strip_html(self, tmp_path):
        data = {'一': {'keyword': 'One', 'story': '<b>One</b>'}}
        f = tmp_path / 'stories.json'
        f.write_text(json.dumps(data))

        store = StoryStore(str(f))
        story = store.get_story('一')
        assert '<b>' not in story['story']
        assert 'One' in story['story']
