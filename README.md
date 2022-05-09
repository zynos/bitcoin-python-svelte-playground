# Bitcoin python svelte playground
![alt text](playground.png)
## Install on your Bitcoin lightning node
### Backend
```
chmod +x create_backend.sh
./create_backend.sh
```

### Frontend
```
npm install
npm run dev -- --port 3456
```

## Deploy on your fullnode
### start frontend (inside "frontend" directory)
`npm run dev -- --port 3456`
### start backend (inside "backend" directory)
`uvicorn test:app --reload --port=8000`

