import json

class CoverageAnalyzer:
    def __init__(self, functions):
        self.functions = functions

    def generate_report(self):
        total = len(self.functions)
        documented = sum(1 for f in self.functions if f["has_docstring"])
        undocumented = total - documented
        coverage = (documented / total * 100) if total > 0 else 0

        report = {
            "total_functions": total,
            "documented": documented,
            "undocumented": undocumented,
            "coverage_percent": round(coverage, 2),
            "functions": self.functions
        }

        return report

    def save_json(self, filepath):
        report = self.generate_report()
        with open(filepath, "w") as f:
            json.dump(report, f, indent=4)