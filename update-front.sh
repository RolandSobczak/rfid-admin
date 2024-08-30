cd $HOME/code/RFIDIO-Frontend

git_sha=$(git rev-parse HEAD)

if [ -z "$git_sha" ]; then
    echo "Error: Git SHA is empty. Please check if you're in a valid Git repository."
    exit 1
fi

rfid_front="localhost:32000/rfidio-front:${git_sha}"
rfid_front_latest="localhost:32000/rfidio-front:latest"

docker build -t $rfid_front  -t $rfid_front_latest -f Dockerfile --build-arg="AUTH_API_URL=http://server.local/auth-api/v1/" --build-arg="TENANT_API_URL=http://server.local/{{ tenant_slug }}/v1/" .
docker push $rfid_front
docker push $rfid_front_latest

 kubectl set image deployment/front --namespace=rfid-main front=$rfid_front

cd -
