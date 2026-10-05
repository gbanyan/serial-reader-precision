from experiment_a5.run import ARMS,jobs


def test_job_matrix_and_schedules():
    assert len(jobs())==96 and len(set(jobs()))==96
    assert ARMS['B-b1'][2][-1]==36000 and ARMS['N8-b16'][0]==(8,)
    # Gate checkpoints are shared with A.4 L arms (evaluated every 300 updates).
    assert all(s%300==0 for s in ARMS['B-b1'][2][:3])
