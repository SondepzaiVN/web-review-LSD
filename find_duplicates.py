import json
import os
from pathlib import Path
from collections import defaultdict
import difflib

question_dir = Path(r'D:\web-review-LSD\Question')
all_questions = []

for json_file in question_dir.rglob('*.json'):
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for q in data:
                q['source_file'] = str(json_file.relative_to(question_dir))
            all_questions.extend(data)
    except Exception as e:
        print(f'Error: {e}')

print(f'Total questions: {len(all_questions)}')

# Find very similar questions using fuzzy matching
print('\n=== HIGHLY SIMILAR QUESTIONS (>85% match) ===\n')
similar_pairs = []
for i, q1 in enumerate(all_questions):
    for j, q2 in enumerate(all_questions):
        if i >= j:
            continue
        ratio = difflib.SequenceMatcher(None, q1['question'].lower(), q2['question'].lower()).ratio()
        if ratio > 0.85 and ratio < 1.0:
            similar_pairs.append((ratio, q1, q2))

similar_pairs.sort(key=lambda x: -x[0])
for ratio, q1, q2 in similar_pairs[:30]:
    print(f'Similarity: {ratio:.1%}')
    print(f'  Q1 (ID {q1["id"]}): {q1["question"][:80]}')
    print(f'  Q2 (ID {q2["id"]}): {q2["question"][:80]}')
    print(f'  Files: {q1["source_file"]} | {q2["source_file"]}')
    print()

question_map = defaultdict(list)
for q in all_questions:
    text = q['question'].strip().lower()
    question_map[text].append(q)

duplicates = {k: v for k, v in question_map.items() if len(v) > 1}
print(f'Found {len(duplicates)} exact duplicate groups\n')

for text, qs in duplicates.items():
    print(f'=== DUP ({len(qs)}x) ===')
    print(qs[0]['question'][:100])
    for q in qs:
        src = q['source_file']
        qid = q['id']
        print(f'  ID {qid} | {src}')
    print()

# Find similar questions (same topic/answer)
import re
print('\n\n=== SIMILAR QUESTIONS (same answer/topic) ===\n')

# Group by answer content
answer_map = defaultdict(list)
for q in all_questions:
    ans_key = q.get('answer', '')
    exp = q.get('explanation', '')[:50] if q.get('explanation') else ''
    key = f"{ans_key}|{exp}"
    answer_map[key].append(q)

# Find groups with multiple questions about same specific topic
topic_keywords = [
    'hiệp ước harmand', 'hiệp ước patenotre', 'ngày 3/2', 'ngày 24/2', 
    'đại hội iii', 'đại hội iv', 'đại hội v', 'đại hội vi', 'đại hội vii',
    'đại hội viii', 'đại hội ix', 'đại hội x', 'đại hội xi', 'đại hội xii', 'đại hội xiii',
    'cương lĩnh 1991', 'cương lĩnh 2011', 'luận cương', 'cương lĩnh chính trị đầu tiên',
    'hội nghị tw 6', 'hội nghị tw 4', 'hội nghị tw 5', 'hội nghị tw 7', 'hội nghị tw 8',
    'phan bội châu', 'phan châu trinh', 'trần phú', 'lê duẩn', 'trường chinh',
    'mặt trận việt minh', 'mặt trận liên việt', 'mặt trận tổ quốc',
    'kinh tế thị trường', 'cnh, hđh', 'nhà nước pháp quyền'
]

topic_groups = defaultdict(list)
for q in all_questions:
    qtext = q['question'].lower()
    for kw in topic_keywords:
        if kw in qtext:
            topic_groups[kw].append(q)
            break

for topic, qs in sorted(topic_groups.items(), key=lambda x: -len(x[1])):
    if len(qs) >= 3:
        print(f'\n--- Topic: "{topic}" ({len(qs)} questions) ---')
        for q in qs:
            print(f'  ID {q["id"]}: {q["question"][:70]}...')
