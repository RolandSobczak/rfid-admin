REPO_ROOT="/home/rsobczak/code/rfid-kube"
#REPO_ROOT="."
cd $REPO_ROOT

prev_git_sha=$(git rev-parse HEAD)
git pull
git_sha=$(git rev-parse HEAD)

if [ $git_sha -eq $prev_git_sha]; then
  exit 0
fi

echo "New version found..."
echo "Running pipeline."
echo "Current commit: $git_sha"

if [ -z "$git_sha" ]; then
    echo "Error: Git SHA is empty. Please check if you're in a valid Git repository."
    exit 1
fi

docker build -t localhost:32000/rfidio-admin:latest . -f docker/backend/Dockerfile

rfid_admin="localhost:32000/rfidio-admin:${git_sha}"
rfid_admin_latest="localhost:32000/rfidio-admin:latest"

docker build -t $rfid_admin -t rfid_admin_latest -f docker/backend/Dockerfile .
docker push $rfid_admin
docker push $rfid_admin_latest

rfid_worker="localhost:32000/rfidio-admin-worker:${git_sha}"
rfid_worker_latest="localhost:32000/rfidio-admin-worker:latest"

docker build -t $rfid_worker -t $rfid_worker_latest -f docker/worker/Dockerfile .
docker push $rfid_worker
docker push $rfid_worker_latest

rfid_sender="localhost:32000/rfidio-mq-sender:${git_sha}"
rfid_sender_latest="localhost:32000/rfidio-mq-sender:latest"

docker build -t $rfid_sender -t $rfid_sender_latest -f docker/sender/Dockerfile .
docker push $rfid_sender
docker push $rfid_sender_latest

 kubectl set image deployments --namespace=rfid-main --selector="app=admin-api" admin-api=$rfid_admin
 kubectl set image deployments --namespace=rfid-main --selector="app=admin-worker" admin-worker=$rfid_worker

cd -
