# City Vault Backend

This is the backend service for City Vault application.

## Prerequisites

- Python 3.8+
- PostgreSQL database
- AWS credentials (for S3 storage)
- Python dependencies (install using `pip install -r requirements.txt`)

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=cityvault
DB_USER=your_db_user
DB_PASSWORD=your_db_password

# AWS
AWS_REGION=your_aws_region
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
S3_RAW_BUCKET=your-s3-bucket-raw
S3_VERIFIED_BUCKET=your-s3-bucket-verified

# JWT
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS (update with your frontend URL)
BACKEND_CORS_ORIGINS='["http://localhost:3000"]'
```

## Running the Application

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python run.py
   ```

The API will be available at `http://0.0.0.0:8000`

## API Documentation

- Swagger UI: `http://0.0.0.0:8000/docs`
- ReDoc: `http://0.0.0.0:8000/redoc`

## Development

- The application uses hot-reload in development mode.
- Make sure to set up proper CORS origins in the `.env` file for your development environment.
