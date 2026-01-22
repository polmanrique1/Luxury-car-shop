import uvicorn

if __name__ == "__main__":
    # Esto le dice a uvicorn: entra en carpeta 'app', busca 'app.py' y arranca 'app'
    uvicorn.run("app.app:app", host="0.0.0.0", port=8080, reload=True)