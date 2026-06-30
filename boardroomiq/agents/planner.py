class PlannerAgent:
    name = "Planner Agent"

    def run(self, question: str, available_data: list[str]) -> list[str]:
        steps = [
            f"Received strategic question: {question}",
            f"Detected available datasets: {', '.join(available_data)}",
            "Assigned Finance Agent to inspect revenue, cost, and margin trends.",
            "Assigned Marketing Agent to inspect spend, conversion, and CAC movement.",
            "Assigned Operations Agent to inspect inventory, stockouts, and demand pressure.",
            "Assigned Risk Agent to inspect churn, dependency, and anomaly signals.",
        ]
        return steps
