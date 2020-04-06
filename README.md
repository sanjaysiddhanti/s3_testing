## S3 Testing

This repository provides examples of testing S3 interactions in Python using the following approaches:

- moto3
- botocore stubbers
- localstack

## Usage

Faster, will not work for localstack

```
docker build -t s3_testing .
docker run s3_testing:latest pytest test/
```

Slower, will work for all tests

```
docker build -t s3_testing .
docker-compose up
```