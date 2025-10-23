"""
Fixed constraint functions for modular solver
Handles theory (class-wide) vs practical (per-batch) correctly
"""

from ortools.sat.python import cp_model
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


def add_subject_hours_constraint_fixed(
    model: cp_model.CpModel,
    variables: Dict[str, Dict[str, Any]],
    subjects: List[Dict[str, Any]]
) -> None:
    """
    Constraint: Each subject gets exactly required hours per week.
    
    For theory (batch="CLASS"): Sum all CLASS entries
    For practical: Sum only one batch (hours are per-batch, not multiplied)
    """
    subject_hours = {s["name"]: s["hours_per_week"] for s in subjects}
    
    for subject_name, required_hours in subject_hours.items():
        # Find subject type
        subject_type = None
        for s in subjects:
            if s["name"] == subject_name:
                subject_type = s["type"]
                break
        
        if subject_type == "theory":
            # Theory: sum CLASS entries only
            theory_vars = []
            for var_name, var_data in variables.items():
                if var_data["subject"] == subject_name and var_data["batch"] == "CLASS":
                    theory_vars.append((var_data["var"], var_data["duration"]))
            
            if theory_vars:
                total_hours = sum(var * duration for var, duration in theory_vars)
                model.Add(total_hours == required_hours)
                logger.info(f"Theory {subject_name}: {required_hours}h constraint")
        
        else:
            # Practical: sum for ONE batch (all batches get same hours)
            practical_vars = []
            for var_name, var_data in variables.items():
                if var_data["subject"] == subject_name and var_data["batch"] == "Batch A":
                    practical_vars.append((var_data["var"], var_data["duration"]))
            
            if practical_vars:
                total_hours = sum(var * duration for var, duration in practical_vars)
                model.Add(total_hours == required_hours)
                logger.info(f"Practical {subject_name}: {required_hours}h per batch constraint")


def add_daily_hours_limit_constraint_fixed(
    model: cp_model.CpModel,
    variables: Dict[str, Dict[str, Any]]
) -> None:
    """
    Constraint 7: Max 2 hours per day per subject.
    
    For theory (CLASS): Max 2h per day total
    For practical: Max 2h per day per batch
    """
    daily_subject_hours = {}
    for var_name, var_data in variables.items():
        # For theory, use (subject, day) as key
        # For practical, use (subject, batch, day) as key
        if var_data["batch"] == "CLASS":
            key = (var_data["subject"], var_data["day"])
        else:
            key = (var_data["subject"], var_data["batch"], var_data["day"])
        
        if key not in daily_subject_hours:
            daily_subject_hours[key] = []
        
        daily_subject_hours[key].append(
            (var_data["var"], var_data["duration"])
        )
    
    # Enforce max 2 hours per day
    for hour_list in daily_subject_hours.values():
        total_hours = sum(var * duration for var, duration in hour_list)
        model.Add(total_hours <= 2)
    
    logger.info("Added daily hours limit constraint (fixed)")
