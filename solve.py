import pandas as pd
import csv

# Load and check data
df = pd.read_json("data/contacts.json")
N = len(df)
assert df.Id.nunique() == N
assert df.Id.min() == 0
assert df.Id.max() == N - 1
assert df.isna().sum().sum() == 0

# Disjoint set union
par = [-1] * N
cnt_contact = list(df['Contacts'])

def root(v):
  if par[v] < 0:
    return v
  else:
    par[v] = root(par[v])
    return par[v]

def join(x, y):
  x = root(x)
  y = root(y)
  if x == y:
    return
  if par[x] > par[y]:
    x, y = y, x
  par[x] += par[y]
  par[y] = x
  cnt_contact[x] += cnt_contact[y]

# Function for grouping tickets by column
def group(col):
  for x, y in df.groupby(col)['Id']:
    if x != "":
      y = list(y)
      n = len(y)
      for i in range(1, n):
        join(y[i - 1], y[i])

# Group tickets by Email, Phone, OrderId
group("Email")
group("Phone")
group("OrderId")

# Build ticket_trace/contact
mp = {}
trace = {}
for i in range(N):
  r = root(i)
  if not r in mp:
    mp[r] = []
  mp[r].append(i)
for r in mp.keys():
  A = sorted(mp[r])
  x = str(A[0])
  for i in range(1, len(A)):
    x += "-" + str(A[i])
  trace[r] = x + ", " + str(cnt_contact[r])

# Print output
print("Total distinct users:", len(mp))
with open("data/output.csv", "w", newline="") as f:
  writer = csv.DictWriter(f, fieldnames=['ticket_id', 'ticket_trace/contact'])
  writer.writeheader()

  for i in range(N):
    writer.writerow({'ticket_id': i, 'ticket_trace/contact': trace[root(i)]})
