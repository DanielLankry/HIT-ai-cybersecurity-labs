import pandas as pd
import numpy as np

n_total = 10000
n_attack = 300 
n_normal = n_total - n_attack

hours_morning = np.random.normal(9, 1.5, n_normal // 2)
hours_afternoon = np.random.normal(16, 2, n_normal // 2)
normal_hours = np.clip(np.concatenate([hours_morning, hours_afternoon]), 0, 23).astype(int)

normal_failed = np.random.poisson(0.8, n_normal)

normal_protocols = np.random.choice(['HTTPS', 'HTTP', 'DNS'], n_normal, p=[0.6, 0.3, 0.1])
normal_duration = []
for p in normal_protocols:
    if p == 'HTTPS':
        normal_duration.append(np.random.normal(250, 50))
    elif p == 'HTTP':
        normal_duration.append(np.random.normal(120, 30))
    else:
        normal_duration.append(np.random.normal(15, 5))

df_normal = pd.DataFrame({
    'hour': normal_hours,
    'failed_attempts': normal_failed,
    'login_duration': normal_duration,
    'protocol': normal_protocols,
    'label': 0
})

attack_hours = np.random.choice([2, 3, 4, 23], n_attack)
attack_failed = np.random.randint(15, 80, n_attack)
attack_duration = np.random.normal(2, 0.5, n_attack)

df_attack = pd.DataFrame({
    'hour': attack_hours,
    'failed_attempts': attack_failed,
    'login_duration': attack_duration,
    'protocol': 'SSH',
    'label': 1
})

df = pd.concat([df_normal, df_attack]).sample(frac=1).reset_index(drop=True)
df.to_csv('cybersecurity_logs.csv', index=False)

print(df.groupby('label')['failed_attempts'].describe())