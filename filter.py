import json

with open('list.json') as data_file:    
	data = json.load(data_file)

threads = []
for item in data:
	if "posts" in item:
		threads.append(item)

threads = sorted(threads, key = lambda x: (x["url"], x.get("page")))
with open('threads.json', 'w') as outfile:
    json.dump(threads, outfile)

