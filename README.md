# Advertisement-Placement-Tool

## Project Overview

The Advertisement Placement Tool is made to help companies strategically place advertisements by identifying the most cost-effective locations. Using publicly available data from 24 major U.S. cities, the tool calculates Audience Reach, Demographic Fit Score, and Cost Efficiency Score. Users can customize inputs like age range, income, employed percentage, and budget, and the program recommends optimal locations based on these criteria. The results include a ranked list of cities, average location metrics, budget allocations, and a visual representation of cost efficiency.

## How to Run the Program

### Install required modules/libraries
```bash
pip install matplotlib
```

### Run the program with your chosen parameters:
   ```bash
   python3 test.py --budget <TOTAL_BUDGET> --age <AGE_RANGE> --income <INCOME_RANGE> --employedpercentage <EMPLOYED_PERCENTAGE> --top_num <NUMBER_OF_LOCATIONS>
   ```
### For example:
   ```bash
   python3 test.py --budget 10000 --age 30-40 --income 50000-80000 --employedpercentage 20 --top_num 10 --demographics demographics.json
   ```
#### Note:

The --budget parameter is required and must be a positive number. A ValueError will be raised if a negative or invalid value is provided.
The parameters --age, --income, --employedpercentage, and --top_num are optional. 
* If not specified, the program will use default values:
    * --age: No filter applied.
    * --income: No filter applied.
    * --employedpercentage: No filter applied.
    * --top_num: Default is 24.



## Outputs

1. **Ranked Locations**: A prioritized list of cities based on cost efficiency.
2. **Average Metrics**: A detailed breakdown of the average, income, and employeed percentage of the filtered locations.
3. **Budget Allocation**: A detailed breakdown of the budget assigned to each top location.
4. **`advertising_chart.png`**: A bar chart of cost efficiency scores and their locations.
5. **`advertising_results.txt`**: A summary of results and budget allocations.



## Methodology

## 1. **Audience Reach**:
Audience Reach measures of how many people are likely to see an ad at a certain location. It relies on foot traffic (how many people pass by the location), the employed population (how many people in the area have jobs and may have money to spend), and the total population of the area. The formula to calculate audience reach is::

### Audience Reach = Foot Traffic × (Employed Population / Total Population)
This gives an estimate of how many people in an area are likely to see the ad based on these factors. 

## 2. **Cost Efficiency Score**:
Cost Efficiency Score shows how well a location gives you exposure for the money you spend. It answers the question: “How many people will see my ad for each dollar I spend?” A higher score means you're getting more exposure for your money.

### Cost Efficiency Score = Audience Reach / Ad Cost
The cost efficiency score indicates how cost-effective a location is for reaching with an audience.
The budget is set by allocating according to each site’s Cost Efficiency Score. To determine the funding each location receives, we started by computing the overall Cost Efficiency Score for all the chosen locations. Subsequently, every site is allocated a segment of the budget based on its proportion of the overall score. Locations with a higher score receive a bigger share of the budget, while those with lower scores are allocated smaller shares. For example, if two places have ratings of 4 and 6, the combined score is 10. The initial site would receive 40% of the overall budget, while the subsequent site would obtain 60%. In this manner, the budget is allocated more effectively, providing more funds to places that excel at reaching the target audience for the expenditure.

## 3. **Budget Allocation**:
Budgets are allocated proportionally to the cost efficiency score of each location:
Allocated Budget = cost_efficiency_score / total_efficiency_score * total_budget
