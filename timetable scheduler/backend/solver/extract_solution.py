"""
Solution extraction helper for modular solver
"""

from typing import Dict, List, Any


def extract_solution_with_batch_expansion(variables: Dict[str, Dict[str, Any]], solver, batches: List[str]) -> Dict[str, Any]:
    """
    Extract solution and expand CLASS batches to all actual batches.
    
    For theory subjects with batch="CLASS", create entries for all batches.
    For practical subjects, keep per-batch entries.
    """
    timetable = []
    
    for var_name, var_data in variables.items():
        if solver.Value(var_data["var"]) == 1:
            # Determine session type
            session_type = "theory"
            if var_data["subject_type"] in ["practical", "lab", "theory+lab"]:
                session_type = "practical"
            
            # Format time slot
            start_hour = var_data["hour"]
            end_hour = start_hour + var_data["duration"]
            
            # If this is a CLASS batch (theory), expand to all batches
            if var_data["batch"] == "CLASS":
                for batch in batches:
                    timetable.append({
                        "subject": var_data["subject"],
                        "batch": batch,
                        "room": var_data["room"],
                        "day": var_data["day"],
                        "start_hour": start_hour,
                        "end_hour": end_hour,
                        "duration": var_data["duration"],
                        "type": session_type,
                        "start_time": f"{start_hour:02d}:00",
                        "end_time": f"{end_hour:02d}:00"
                    })
            else:
                # Regular per-batch entry
                timetable.append({
                    "subject": var_data["subject"],
                    "batch": var_data["batch"],
                    "room": var_data["room"],
                    "day": var_data["day"],
                    "start_hour": start_hour,
                    "end_hour": end_hour,
                    "duration": var_data["duration"],
                    "type": session_type,
                    "start_time": f"{start_hour:02d}:00",
                    "end_time": f"{end_hour:02d}:00"
                })
    
    # Sort by day, then hour
    day_order = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}
    timetable.sort(key=lambda x: (day_order.get(x["day"], 7), x["start_hour"]))
    
    return {
        "status": "success",
        "timetable": timetable,
        "stats": {
            "total_slots": len(timetable),
            "subjects_scheduled": len(set(t["subject"] for t in timetable)),
            "batches_scheduled": len(set(t["batch"] for t in timetable))
        }
    }
