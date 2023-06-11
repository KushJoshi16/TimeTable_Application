import pandas as pd
import json
from generator_algo.data import CLASS_HOURS as class_hours

data = None

def timeTableFromOutput():
    with open('classes/output.json') as f:
        data = json.load(f)
    day = [
        'monday',
        'tuesday',
        'wednesday',
        'thursday',
        'friday',
        'saturday'
        ]
    Time_table = {'sections':{}}
    for record in data:
        for group in eval(record['Group']):
            section = Time_table['sections'].get(group,None)
            if not section:
                section = dict({
                    'monday':['']*class_hours,
                    'tuesday':['']*class_hours,
                    'wednesday':['']*class_hours,
                    'thursday':['']*class_hours,
                    'friday':['']*class_hours,
                    'saturday':['']*class_hours
                    })
            
            sub_day = day[int(record['Assigned_time'])//class_hours]
            lecture =   int(record['Assigned_time'])%class_hours
            section[sub_day][lecture] = record['Subject']
            for i in range(int(record['Duration'])):
                section[sub_day][lecture+i] = record['Subject']
            
            Time_table['sections'][group] = section
            
    with open('classes/TimeTable.json','w') as f:
        json.dump(Time_table,f)


if __name__ == '__main__':
    timeTableFromOutput()