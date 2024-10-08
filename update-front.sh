cd /home/rsobczak/code/RFIDIO-Frontend

git_sha=$(git rev-parse HEAD)

if [ -z "$git_sha" ]; then
    echo "Error: Git SHA is empty. Please check if you're in a valid Git repository."
    exit 1
fi

rfid_front="localhost:32000/rfidio-front:${git_sha}"
rfid_front_latest="localhost:32000/rfidio-front:latest"

docker build -t $rfid_front  -t $rfid_front_latest -f Dockerfile --build-arg="AUTH_API_URL=http://192.168.0.92/auth-api/v1/" --build-arg="TENANT_API_URL=http://192.168.0.92/tenant-api/v1/" .
docker push $rfid_front
docker push $rfid_front_latest

cd -
