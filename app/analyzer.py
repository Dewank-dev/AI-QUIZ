from collections import defaultdict

def analyze_performance(details):
    # details: list of {id, topic, status}
    topic_counts = defaultdict(lambda: {'correct':0,'total':0})
    for d in details:
        t = d.get('topic','General')
        topic_counts[t]['total'] += 1
        if d.get('status') == 'Correct':
            topic_counts[t]['correct'] += 1

    results = {}
    strong = []
    weak = []
    for topic, v in topic_counts.items():
        pct = round((v['correct']/v['total']*100) if v['total'] else 0,2)
        results[topic] = pct
        if pct >= 80:
            strong.append(topic)
        elif pct < 60:
            weak.append(topic)

    # Generate simple human-readable feedback
    feedback = []
    for t in strong:
        feedback.append(f'Good performance in {t}.')
    for t in weak:
        feedback.append(f'More practice is suggested for {t}.')
    if not feedback:
        feedback.append('Keep practicing regularly to maintain and improve your skills.')

    return {'topic_percentages': results, 'strong': strong, 'weak': weak, 'feedback': feedback}
