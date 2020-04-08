## S3 Testing

This repository provides examples of testing S3 interactions in Python using the following approaches:

- moto3
- botocore stubbers
- localstack

## Usage

Build the Docker image

```
docker build -t s3_testing .
```

Run the tests

```
docker-compose up
```

## Contributing

If you have examples of other S3 testing libraries, please send me a pull request.