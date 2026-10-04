import random
from .storage import load_questions


class QuizEngine:
    def __init__(self):
        self.questions = load_questions()

    def fetch_questions(self, subject=None, topic=None, difficulty=None, num=10):
        all_q = self.questions
        if subject:
            all_q = [q for q in all_q if q.get('subject') == subject]
        if topic and topic != 'All':
            all_q = [q for q in all_q if q.get('topic') == topic]
        if difficulty and difficulty != 'Mixed':
            all_q = [q for q in all_q if q.get('difficulty') == difficulty]

        if not all_q:
            return []

        random.shuffle(all_q)
        selected = all_q[:min(len(all_q), num)]

        out = []
        for q in selected:
            opts = list(q.get('options', []))
            random.shuffle(opts)
            out.append({
                'id': q.get('id'),
                'question': q.get('question'),
                'options': opts,
                'answer': q.get('answer'),
                'subject': q.get('subject'),
                'topic': q.get('topic'),
                'difficulty': q.get('difficulty'),
                'explanation': q.get('explanation','')
            })

        # If there are fewer than desired, create simple variations by duplicating
        # existing questions with shuffled options so the user gets the requested
        # number of questions (variations are labeled). This avoids failing when
        # the bank is small while keeping behavior predictable for demos.
        desired_min = num
        next_id = max([q.get('id', 0) for q in self.questions]) + 1
        idx = 0
        while len(out) < desired_min and selected:
            base = selected[idx % len(selected)]
            opts = list(base.get('options', []))
            random.shuffle(opts)
            variation = {
                'id': next_id,
                'question': base.get('question') + ' (variation)',
                'options': opts,
                'answer': base.get('answer'),
                'subject': base.get('subject'),
                'topic': base.get('topic'),
                'difficulty': base.get('difficulty'),
                'explanation': base.get('explanation','')
            }
            out.append(variation)
            next_id += 1
            idx += 1

        return out
