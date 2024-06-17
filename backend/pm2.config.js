module.exports = {
  apps: [
    {
      name: 'fastapi',
      script:
        'uvicorn main:app --host 0.0.0.0 --port 3000 --ssl-keyfile key.pem --ssl-certfile cert.pem',
      env: {
        PORT: 3000,
        ENVIRONMENT: 'myenv',
      },
    },
  ],
};
