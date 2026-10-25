from typing import List, Dict, Any, Optional
import z3
from .models import RuleDefinition, RuleConflict

class Z3RuleConflictFinder:
    """
    Z3 SMT Solver based engine that evaluates regulatory rule sets against each other
    to mathematically identify contradictions, overlapping constraints, or ambiguous circulars
    BEFORE applications are scored.
    """
    def __init__(self, rules: List[RuleDefinition]):
        self.rules = rules

    def find_all_conflicts(self) -> List[RuleConflict]:
        conflicts: List[RuleConflict] = []
        n = len(self.rules)
        for i in range(n):
            for j in range(i + 1, n):
                r1 = self.rules[i]
                r2 = self.rules[j]
                
                # Compare rules governing the same category & variable
                if r1.category == r2.category and r1.variable_name == r2.variable_name:
                    if self._conditions_overlap(r1.condition, r2.condition):
                        conflict = self._check_pair_conflict(r1, r2)
                        if conflict:
                            conflicts.append(conflict)
        return conflicts

    def _conditions_overlap(self, cond1: Optional[Dict[str, Any]], cond2: Optional[Dict[str, Any]]) -> bool:
        """Checks if two rule conditions can apply to the same application profile."""
        if not cond1 or not cond2:
            return True
        for key in cond1:
            if key in cond2 and cond1[key] != cond2[key]:
                return False
        return True

    def _check_pair_conflict(self, r1: RuleDefinition, r2: RuleDefinition) -> Optional[RuleConflict]:
        """
        Formulate constraint check in Z3:
        Checks if there exists a parameter value x where Rule A holds and Rule B fails,
        or where both are mutually unsatisfiable.
        """
        solver = z3.Solver()
        x = z3.Real('param_x')
        
        # Translate rule 1
        c1 = self._build_z3_expr(x, r1.operator, r1.target_value)
        # Translate rule 2
        c2 = self._build_z3_expr(x, r2.operator, r2.target_value)
        
        if c1 is None or c2 is None:
            return None

        # Check 1: Mutually contradictory (Cannot both be satisfied simultaneously)
        solver.push()
        solver.add(c1)
        solver.add(c2)
        both_sat = solver.check()
        solver.pop()

        if both_sat == z3.unsat:
            return RuleConflict(
                conflict_id=f"CONF-{r1.rule_id}-{r2.rule_id}",
                rule_a_id=r1.rule_id,
                rule_b_id=r2.rule_id,
                rule_a_clause=r1.source.clause_reference,
                rule_b_clause=r2.source.clause_reference,
                category=r1.category,
                conflict_type="CONTRADICTION",
                explanation=(
                    f"Direct contradiction detected between '{r1.source.document_name} ({r1.source.clause_reference})' "
                    f"and '{r2.source.document_name} ({r2.source.clause_reference})'. "
                    f"No institution can satisfy both constraints simultaneously."
                ),
                requires_admin_override=True,
                override_active=False
            )

        # Check 2: Asymmetric ambiguity (Satisfies r2 but violates r1 without explicit repeal)
        solver.push()
        solver.add(c2)
        solver.add(z3.Not(c1))
        asym_sat = solver.check()
        counter_example = None
        if asym_sat == z3.sat:
            m = solver.model()
            val = m[x]
            counter_example = {"counterexample_value": float(val.as_fraction()) if hasattr(val, 'as_fraction') else str(val)}
        solver.pop()

        if asym_sat == z3.sat and counter_example:
            return RuleConflict(
                conflict_id=f"AMBIG-{r1.rule_id}-{r2.rule_id}",
                rule_a_id=r1.rule_id,
                rule_b_id=r2.rule_id,
                rule_a_clause=r1.source.clause_reference,
                rule_b_clause=r2.source.clause_reference,
                category=r1.category,
                conflict_type="SUBSET_AMBIGUITY",
                explanation=(
                    f"Regulatory ambiguity: '{r2.source.document_name} ({r2.source.clause_reference})' relaxes or alters "
                    f"'{r1.source.clause_reference}' (e.g. target {r2.target_value} vs {r1.target_value}). "
                    f"Institutions with intermediate values (e.g., {counter_example['counterexample_value']}) "
                    f"would be marked Deficient by the Handbook but Compliant by the Circular unless explicitly overridden."
                ),
                counterexample_model=counter_example,
                requires_admin_override=True,
                override_active=False
            )

        return None

    def _build_z3_expr(self, var: z3.ArithRef, op: str, target: Any):
        if op == ">=":
            return var >= float(target)
        elif op == "<=":
            return var <= float(target)
        elif op == "==":
            return var == float(target)
        elif op == ">":
            return var > float(target)
        elif op == "<":
            return var < float(target)
        return None
