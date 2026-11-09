# AquaGuard AI — 3-minute narrated presentation script

**0:00–0:25 | Introduction and issue**  
Hello, my name is Farid Ahmad Khan from Kabul University. My project is AquaGuard AI, an explainable water-monitoring and demand-planning prototype for university campuses. Campuses use water in classrooms, laboratories, residences, cafeterias and landscaping. When monitoring depends on periodic manual readings or monthly bills, unusual use can remain unnoticed.

**0:25–0:50 | The solution**  
AquaGuard AI accepts meter readings through a CSV file and turns them into an interactive dashboard. It monitors consumption, screens for unusual patterns, explains why a reading was flagged, forecasts demand for seven days, and helps users explore conservation and response scenarios.

**0:50–1:25 | Dashboard and anomaly review**  
Here is the dashboard. The demonstration contains five virtual meters, 28 days and 15-minute intervals, for 13,440 synthetic readings. In anomaly review, the system compares each meter against its own recent rolling baseline. It shows the observed volume, expected baseline and estimated excess. Related flags are grouped into candidate events so a facilities team can prioritize investigation. These flags are screening results, not confirmed leak diagnoses.

**1:25–1:50 | Forecast**  
The demand page forecasts the next seven days. It uses a transparent weekday-aware baseline: 70 percent of the recent median for the same weekday and 30 percent of the recent 14-day median. This is a simple baseline, not a deep-learning model. Weather and occupancy are not included.

**1:50–2:15 | Scenario simulator**  
The simulator demonstrates how response time can affect a hypothetical constant excess flow. At 25 litres per hour over 48 hours, the estimated volume is 1,200 litres. If response takes 8 hours, it is 200 litres. The scenario difference is 1,000 litres. This is an estimate, not measured water savings.

**2:15–2:40 | Evaluation and data upload**  
The evaluation page reports true positives, false positives, false negatives, true negatives, precision, recall and F1 using synthetic injected events. Users can also upload their own CSV meter data and export readings. We do not invent accuracy metrics for uploaded data without labels.

**2:40–3:00 | Impact and next step**  
AquaGuard AI aims to help campus teams notice unusual water use earlier, prioritize inspections and plan demand. The next step is an authorized university pilot using real meter records, inspection-confirmed events and calibrated thresholds. Thank you.
