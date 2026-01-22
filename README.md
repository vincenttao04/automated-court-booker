# automated-court-booker

future improvements

1. have an option to combine bond and c. drive data together for the bot to book courts at both stadiums.
2. add optional start and/or end time for algorithm so it only books within certain time constraints - speeds up convergence time as well. make this an iterative booking process to find the longest continuous sequence within the given time frame.
3. credit balance checker - have 3 different statuses (correspond to the 3 different pricing tiers) - calculates and checks if my credit balance is sufficient for the booking request (concurrent, not sequential - otherwise it will increase execution time)
4. test cases - important to test if my optimisation is working or not

open new (restart) terminal to open virtual environment

testing

- `python -m pytest -v`
- `python -m pytest -v -s` -> with output printed

run 

- `python main.py`

change booking preferences using /config.yaml (local dev only)