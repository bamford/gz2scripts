from get_gz2_classifications import *

def create_gz2_tables():
    task_ids = questions.field('id')[0]
    for task_id in task_ids:
        answer_ids = answers.field('id').select(condition='task_id = %i'%task_id,
                                                distinct=True)[0]
        for answer_id in answer_ids:
            objids, counts = cursor.execute('SELECT asset_id, COUNT(asset_id) FROM asset_classifications as C LEFT JOIN annotations as A ON (C.classification_id=A.classification_id) WHERE A.task_id=%i AND A.answer_id=%i GROUP BY asset_id ORDER BY asset_id LIMIT 10')
            print objids, counts
