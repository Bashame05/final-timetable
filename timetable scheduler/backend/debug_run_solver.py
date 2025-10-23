import sys, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from backend.solver.solver_modular import generate_timetable

week_config = {"week_start_time":"09:00","week_end_time":"16:00","lunch_start":"13:00","lunch_end":"14:00","working_days":["Mon","Tue","Wed"]}
rooms=[{"name":"R1","type":"classroom","capacity":60},{"name":"Lab1","type":"lab","capacity":30}]
subjects=[{"name":"Math","type":"theory","hours_per_week":3},{"name":"CSLab","type":"practical","hours_per_week":2}]
batches=["Batch A","Batch B"]

res = generate_timetable(week_config, subjects, rooms, batches)
print(res)
