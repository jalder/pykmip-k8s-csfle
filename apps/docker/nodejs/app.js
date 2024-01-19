import fs  from "fs"
import os from "os"
import crypto from "crypto"
import mongodb from "mongodb"
import { debug } from "console"

async function main(){
    console.log("hello")
    const path = "./master-key.txt";
    let dbClient = new mongodb.MongoClient("mongodb://host.docker.internal:27017")
    await dbClient.connect()
    if(!fs.existsSync(path)){
        let key = crypto.randomBytes(96)
        console.log(key.toString("base64"))
        fs.writeFile(path, key, err => {if(err){console.log(err)}})
        
        await dbClient.db("encryption").dropDatabase()
        await dbClient.db("encryption").collection("__keyVault").createIndex({keyAltNames: 1}, {unique: true, partialFilterExpression: { keyAltNames: { $exists: true } }})
    
        let kmsProvider = {local: {key: key}}
    
        let keyNamespace = "encryption.__keyVault"
        let clientEncryption = new mongodb.ClientEncryption(dbClient, {keyVaultNamespace: keyNamespace, kmsProviders: kmsProvider})
        let clientKey = await clientEncryption.createDataKey("local", {keyAltNames: ["foobar"]})
        //console.log(clientKey)
        
    }
    
    let edoc = await dbClient.db("encryption").collection("__keyVault").find().toArray()
    console.log(edoc)

    let keyNamespace = "encryption.__keyVault"
    const localMasterKey = fs.readFileSync(path);
    let kmsProviders = {local: {key: localMasterKey}}

    const schema = {
        bsonType: "object",
        encryptMetadata: {
          keyId: [edoc[0]._id],
        },
        properties: {
          medicalRecords: {
            encrypt: {
              bsonType: "array",
              algorithm: "AEAD_AES_256_CBC_HMAC_SHA_512-Random",
            },
          },
          bloodType: {
            encrypt: {
              bsonType: "string",
              algorithm: "AEAD_AES_256_CBC_HMAC_SHA_512-Random",
            },
          },
          ssn: {
            encrypt: {
              bsonType: "int",
              algorithm: "AEAD_AES_256_CBC_HMAC_SHA_512-Random",
            },
          },
        },
      };
      
      var patientSchema = {};
      var db = "medicalRecords";
        var coll = "patients";
        var namespace = `${db}.${coll}`;
      patientSchema[namespace] = schema;
      // end-schema
      
      // start-extra-options
      const extraOptions = {
        //cryptSharedLibPath: "/app/crypt/libmongocrypt/cmake-build/mongo_crypt_v1.so",
        cryptSharedLibPath: "/app/crypt/lib/mongo_crypt_v1.so",
        //cryptSharedLibPath: "/usr/lib/aarch64-linux-gnu/libmongocrypt.so",
      };
      // end-extra-options

      console.log(patientSchema)
      
      // start-client
      const secureClient = new mongodb.MongoClient("mongodb://host.docker.internal:27017", {
        autoEncryption: {
          keyVaultNamespace: keyNamespace,
          kmsProviders,
          schemaMap: patientSchema,
          extraOptions: extraOptions,
          options: {logger: function(level, message){console.log(message); console.log(level)}}
        },
        monitorCommands: true
      });
      secureClient.on('commandStarted', (event) => console.debug(event));
      secureClient.on('commandSucceeded', (event) => console.debug(event));
      secureClient.on('commandFailed', (event) => console.debug(event));
      try {
        const writeResult = await secureClient
          .db(db)
          .collection(coll)
          .insertOne({
            name: "Jon Doe",
            ssn: 241014209,
            bloodType: "AB+",
            myKey: edoc[0]._id,
            medicalRecords: [{ weight: 180, bloodPressure: "120/80" }],
            insurance: {
              policyNumber: 123142,
              provider: "MaestCare",
            },
          });
          console.log(writeResult)
      } catch (writeError) {
        console.error("writeError occurred:", writeError);
      }
      

}

main()