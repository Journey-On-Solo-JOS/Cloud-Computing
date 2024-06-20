# Journey on Solo BackEnd API

This repository contains for database and BackEnd API Endpoint

## Importing Database
To import the database, follow these steps:

1. Navigate to the firestore-database directory:

```
cd firestore-database
```
2. Install dependencies:
```
npm install
```
3. Run the import script with your CSV file:
```
node importDatatoFirestore items.csv
```

## Setting Up and Running on Google Cloud Compute Engine
 
To deploy and run the backend on Google Cloud Compute Engine:

1. Create a Compute Engine instance:
```
gcloud compute instances create journeyonsolo-v1 --project=cp-jos --zone=asia-southeast2-a --machine-type=e2-medium --network-interface=address=34.50.77.23,network-tier=PREMIUM,stack-type=IPV4_ONLY,subnet=default --maintenance-policy=MIGRATE --provisioning-model=STANDARD --service-account=168961830059-compute@developer.gserviceaccount.com --scopes=https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/trace.append --tags=http-server,https-server,lb-health-check --create-disk=auto-delete=yes,boot=yes,device-name=journeyonsolo-v1,image=projects/debian-cloud/global/images/debian-12-bookworm-v20240617,mode=rw,size=35,type=projects/cp-jos/zones/asia-southeast2-a/diskTypes/pd-balanced --no-shielded-secure-boot --shielded-vtpm --shielded-integrity-monitoring --labels=goog-ec-src=vm_add-gcloud --reservation-affinity=any
```
2. Allow inbound traffic on port 3000:
```
gcloud compute --project=cp-jos firewall-rules create allow-port-3000 --direction=INGRESS --priority=1000 --network=default --action=ALLOW --rules=tcp:3000 --source-ranges=0.0.0.0/0
```

3. Access your Compute Engine instance and clone the project:
```
git clone https://github.com/Journey-On-Solo-JOS/Cloud-Computing.git .

```
## Setting Up the Backend Locally
To set up the backend locally:
1. Navigate to the backend directory:
```
cd Cloud-Computing/backend
```
2. Create a virtual environment:
```
python3 -m venv myenv
```
3. Activate the virtual environment:
```
source myenv/bin/activate
```
3. Install Python dependencies and Node.js dependencies:
```
pip install -r requirement.txt
npm install
```
4. Start the backend application using PM2:
```
pm2 start pm2.config.js
```
5. Make sure you allowing port 3000 for all to open the port in internet:
```
gcloud compute --project=cp-jos firewall-rules create allow-port-3000 --direction=INGRESS --priority=1000 --network=default --action=ALLOW --rules=tcp:3000 --source-ranges=0.0.0.0/0
```

# Access API Documentation
You can access the API documentation guide easily via `{your_external_ip}/docs` or `{your_external_ip}/redoc`. For example, you can explore the Journey on Solo API Backend documentation at `35.219.85.151:3000/docs` or `35.219.85.151:3000/redoc`.