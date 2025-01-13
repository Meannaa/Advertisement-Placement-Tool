import csv
import argparse
import matplotlib.pyplot as plt


class Demographic:
    def __init__(self, filename):
        self.demographics = self.load_demographics(filename)

    def load_demographics(self, filename):
        data = {}
        try:
            with open(filename, "r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        data[row["Location"]] = {
                            "age": int(float(row["Age"])),
                            "income": int(float(row["Income"])),
                            "employedpopulation": int(float(row.get("EmployedPopulation", 0))),
                            "ad_cost": int(float(row["AdCost"])),
                            "foottraffic": int(float(row["FootTraffic"])),
                            "population": int(float(row["Population"]))
                        }
                    except ValueError:
                        print(f"Skipping row with invalid data: {row}")
            return data
        except FileNotFoundError:
            print(f"Error: File {filename} not found.")
            return {}

    def filter_locations(self, target_age_range=None, target_income_range=None, min_employed_percentage=None):
        """
        Filters locations based on the provided criteria. Returns all locations if no filters are applied.

        Args:
            target_age_range (range, optional): Target age range.
            target_income_range (range, optional): Target income range.
            min_employed_percentage (float, optional): Minimum employed population percentage.

        Returns:
            list: A list of location names that meet the criteria.
        """
        if not any([target_age_range, target_income_range, min_employed_percentage]):
            # Return all locations if no filters are provided
            return list(self.demographics.keys())

        return [
            location for location, info in self.demographics.items()
            if (target_age_range is None or info["age"] in target_age_range) and
               (target_income_range is None or info["income"] in target_income_range) and
               (min_employed_percentage is None or (info["employedpopulation"] / info["population"]) * 100 >= min_employed_percentage)
        ]


class Ranker:
    """
    A class used to evaluate and rank advertising locations based on cost efficiency and audience reach.
    """
    def __init__(self):
        self.locations = []

    def add_location(self, location_name, ad_cost, foottraffic, employedpopulation, population):
        audience_reach = self.audience_reach(foottraffic, employedpopulation, population)
        cost_efficiency_score = self.cost_efficiency_score(audience_reach, ad_cost)

        self.locations.append({
            "location_name": location_name,
            "ad_cost": ad_cost,
            "audience_reach": audience_reach,
            "cost_efficiency_score": cost_efficiency_score
        })

    def audience_reach(self, foottraffic, employedpopulation, population):
        return round(foottraffic * (employedpopulation / population))

    def cost_efficiency_score(self, audience_reach, ad_cost):
        if ad_cost == 0:
            return 0
        return audience_reach / ad_cost

    def rank_locations(self, top_num=24):
        return sorted(self.locations, key=lambda loc: loc["cost_efficiency_score"], reverse=True)[:top_num]


class Budget:
    """
    Handles budget allocation for advertising locations based on cost efficiency scores.
    """

    def __init__(self, total_budget, top_locations):
        """
        Initializes the Budget class with a total budget and top-performing locations.

        Parameters:
            total_budget (float): The total budget available for allocation.
            top_locations (list): A list of dictionaries containing location details and cost efficiency scores.
        """
        self.total_budget = total_budget
        self.top_locations = top_locations

    def allocate_budget(self):
        """
        Allocates the total budget proportionally to the cost efficiency scores of the top locations.
        """
        total_efficiency_score = sum([loc["cost_efficiency_score"] for loc in self.top_locations])
        if total_efficiency_score == 0:
            print("Error: No valid cost efficiency score. Cannot allocate budget.")
            return
        for loc in self.top_locations:
            loc["allocated_budget"] = (loc["cost_efficiency_score"] / total_efficiency_score) * self.total_budget

    def adjust_budget_allocation(self, location_name, new_budget):
        for loc in self.top_locations:
            if loc["location_name"] == location_name:
                loc["allocated_budget"] = new_budget

    def optimal_spending(self):
        """
        Marks the allocated budget for each location as its 'optimal spending.'
        """
        for loc in self.top_locations:
            loc["optimal_spending"] = loc["allocated_budget"]

    def track_spending(self):
        total_spent = sum([loc["allocated_budget"] for loc in self.top_locations])
        remaining_budget = self.total_budget - total_spent
        print("\nBudget Allocation:")
        print(f"Total Budget: ${self.total_budget:.2f}")
        for loc in self.top_locations:
            print(f"{loc['location_name']}: Allocated Budget: ${loc['allocated_budget']:.2f}")
        print(f"Remaining Budget: ${remaining_budget:.2f}")


class UserInterface:
    def __init__(self):
        self.args = self.parse_args()

    def parse_args(self):
        def parse_range(value):
            try:
                start, end = map(int, value.split('-'))
                if start > end:
                    raise argparse.ArgumentTypeError(f"Invalid range: {value}")
                return range(start, end + 1)
            except ValueError:
                raise argparse.ArgumentTypeError(f"Invalid range format: {value}")

        parser = argparse.ArgumentParser(description="Strategic Advertising Placement Tool")
        parser.add_argument("--budget", type=int, required=True, help="Total advertising budget")
        parser.add_argument("--age", type=parse_range, help="Target age range (e.g., 25-35)")
        parser.add_argument("--income", type=parse_range, help="Target income range (e.g., 50000-80000)")
        parser.add_argument("--employedpercentage", type=float, help="Minimum employed population percentage (optional)")
        parser.add_argument("--top_num", type=int, default=24, help="Number of top locations to display")
        parser.add_argument("--demographics", type=str, default="demographics.csv", help="Demographics data file")
        return parser.parse_args()

    def run(self):
        analyzer = Demographic(self.args.demographics)

        target_age_range = self.args.age
        target_income_range = self.args.income
        min_employed_percentage = self.args.employedpercentage

        filtered_locations = analyzer.filter_locations(
            target_age_range=target_age_range,
            target_income_range=target_income_range,
            min_employed_percentage=min_employed_percentage
        )

        ranker = Ranker()
        for location in filtered_locations:
            data = analyzer.demographics[location]
            ranker.add_location(
                location_name=location,
                ad_cost=data["ad_cost"],
                foottraffic=data["foottraffic"],
                employedpopulation=data["employedpopulation"],
                population=data["population"],
            )

        top_locations = ranker.rank_locations(self.args.top_num)
        self.display_results(top_locations)

        budget_optimizer = Budget(self.args.budget, top_locations)
        budget_optimizer.allocate_budget()
        budget_optimizer.optimal_spending()
        budget_optimizer.track_spending()

        self.display_bar_chart(top_locations)
        self.save_results_to_file(top_locations, budget_optimizer)

    def display_results(self, top_locations):
        print("Top Advertising Locations:\n")
        for loc in top_locations:
            print(f"Location: {loc['location_name']}, "
                  f"Cost Efficiency Score: {loc['cost_efficiency_score']:.2f}, "
                  f"Audience Reach: {loc['audience_reach']:.2f}")

    def display_bar_chart(self, top_locations):
        sorted_locations = sorted(top_locations, key=lambda loc: loc["cost_efficiency_score"], reverse=True)
        locations = [loc["location_name"] for loc in sorted_locations][::-1]
        efficiency_scores = [loc["cost_efficiency_score"] for loc in sorted_locations][::-1]
        plt.barh(locations, efficiency_scores)
        plt.title("Top Advertising Locations", fontsize=16)
        plt.xlabel("Cost Efficiency Score", fontsize=14)
        plt.tight_layout()

        plt.savefig("advertising_chart.png")
        print("\nGraph saved as advertising_chart.png")
        plt.show()

    def save_results_to_file(self, top_locations, budget_optimizer):
        with open("advertising_results.txt", "w") as file:
            file.write("Top Advertising Locations:\n")
            for loc in top_locations:
                file.write(f"Location: {loc['location_name']}, "
                           f"Cost Efficiency Score: {loc['cost_efficiency_score']:.2f}, "
                           f"Audience Reach: {loc['audience_reach']:.2f}\n")

            file.write("\nBudget Allocation:\n")
            file.write(f"Total Budget: ${budget_optimizer.total_budget:.2f}\n")
            for loc in top_locations:
                file.write(f"{loc['location_name']}: Allocated Budget: ${loc['allocated_budget']:.2f}\n")
            remaining_budget = budget_optimizer.total_budget - sum([loc["allocated_budget"] for loc in top_locations])
            file.write(f"\nRemaining Budget: ${remaining_budget:.2f}\n")
        print("Results saved as advertising_results.txt")


if __name__ == "__main__":
    ui = UserInterface()
    ui.run()
