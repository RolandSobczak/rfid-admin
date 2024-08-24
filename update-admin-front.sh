cd /home/$USER/code/rfid-kube-admin

git_sha=$(git rev-parse HEAD)

if [ -z "$git_sha" ]; then
    echo "Error: Git SHA is empty. Please check if you're in a valid Git repository."
    exit 1
fi

rfid_front="localhost:32000/admin-front:${git_sha}"
rfid_front_latest="localhost:32000/admin-front:latest"

docker build . \
  --build-arg="ADMIN_API_URL=http://admin.server.local/v1" \
  --build-arg="AUTH_API_URL=http://auth.server.local/v1" \
  --build-arg BASE_URL=/admin/ \
  -t $rfid_front \
  -t $rfid_front_latest

docker push $rfid_front
docker push $rfid_front_latest

 kubectl set image deployments --namespace=rfid-main --selector="app=admin-front" admin-front=$rfid_front

cd -
