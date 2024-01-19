# Docker, NodeJS CSFLE, and MongoDB Enterprise

This learning lab deploys a mongodb enterprise docker container (version 7) and a NodeJS application with MongoDB driver mongodb@6.3.0 and mongodb-client-encryption@6.0.0 in a separate container.  MongoDB services are forwarded to host/workstation port 27017 and the NodeJS MongoClient connects to host.docker.internal:27017.  This lab uses local keyfile for CSFLE, this is not recommended in production (use a proper KMS).

**This lab is built on Mac M1 using ARM64 CPU architecture.**  The MongoDB Enterprise builds and MongoClient (loaded with the CSFLE shared library) will NOT work on a Docker Desktop QEMU X86_64 environment.  Should you need to build for x86_64, reference the commented out lines in the Dockerfile and adjust as needed.

## Step 1: Deploy a database
Run ARM64 version of MongoDB Enterprise Server:

```
docker run --platform linux/arm64 -d -p 27017:27017 mongodb/mongodb-enterprise-server
```

## Step 2: Build and Run the NodeJS container
As this is a learning lab, our entrypoint command is simply a bash prompt.  This will allow us to run our application multiple times within the container.

```
docker build . -t mdbcsfle:latest
docker run -it mdbcsfle:latest
```

## Step 3: Run the CSFLE application demo

At the bash prompt for the running container (from Step 2), execute:
```
node app.js
```

## Step 4: Validate the inserted document is encrypted

From Compass UI or mongosh:
```
% mongosh mongodb://localhost:27017 --eval "db.getSiblingDB('medicalRecords').patients.find().sort({"_id":-1}).limit(1)" --quiet
[
  {
    _id: ObjectId("65aab04741e85bfaf22708eb"),
    name: 'Jon Doe',
    ssn: Binary.createFromBase64("AkHQ97flj0DMvRTNOjq/Xx8QgJlr2CR/YEFKqofQdKTpWTCi0LFdI8BDpjN26U8tUcNtvpI/YZeSrUXlJ78QnhgIO7ojWbkR4kZCbCjR725U5Q==", 6),
    bloodType: Binary.createFromBase64("AkHQ97flj0DMvRTNOjq/Xx8C+DyLVuXaldmNpETWzlxF8WfW9Y0f75JZTwTjx5EwLVlF0EZId6EHMY/PjsEVtitXtJYoUWGv6KiwNgWqkkm3oQ==", 6),
    myKey: new UUID("41d0f7b7-e58f-40cc-bd14-cd3a3abf5f1f"),
    medicalRecords: Binary.createFromBase64("AkHQ97flj0DMvRTNOjq/Xx8EdCmlbAQjdB6857eT9d9wXEtbXnAnwJWvhMr1zJJE4VqkhMIfZ5IqMes1cdh4McLbVnaWjeCX+2fYMS0e8qRBhd78CaoWpNNRZkY+zL1PaQ+VTfIfjQubkmTMBL2Ixxx4mNJVYtUU7SkmIVt0js5qBQ==", 6),
    insurance: { policyNumber: 123142, provider: 'MaestCare' }
  }
]
```

[Compass CSFLE Docs](./Compass-test.png)

### Notes
Server side enforcement:
```
db.getSiblingDB("foo").runCommand({
  collMod: "bar",
  validator: {
    $jsonSchema: {
      bsonType: "object",
      properties: {
        ssn: {
          encrypt: {
            keyId: [UUID('e88c40b2-42cf-4301-9f3a-3d247e19f6fd')],
            algorithm: "AEAD_AES_256_CBC_HMAC_SHA_512-Random",
            bsonType: "int",
          },
        },
        bloodType: {
          encrypt: {
            keyId: [UUID('e88c40b2-42cf-4301-9f3a-3d247e19f6fd')],
            algorithm: "AEAD_AES_256_CBC_HMAC_SHA_512-Deterministic",
            bsonType: "string",
          },
        },
      },
    },
  },
});
```